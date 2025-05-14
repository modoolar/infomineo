# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
import logging
from datetime import timedelta

from odoo import Command, api, fields, models

_logger = logging.getLogger(__name__)


class ApprovalApprover(models.Model):
    _inherit = "approval.approver"
    _check_company_auto = False

    sequence = fields.Integer("Sequence", default=10)
    matrix_line_id = fields.Many2one(comodel_name="advanced.approval.category.approver")
    warning_level = fields.Selection(
        selection=[
            ("reminded", "Remind"),
            ("manager_reminded", "Manager Reminded"),
            ("substituted", "Substituted"),
        ]
    )
    pending_timestamp = fields.Datetime(
        compute="_compute_pending_timestamp", store=True
    )
    overridden_by_id = fields.Many2one(comodel_name="res.users")

    @api.depends("status")
    def _compute_pending_timestamp(self):
        for rec in self:
            rec.pending_timestamp = (
                fields.Datetime.now() if rec.status == "pending" else False
            )

    @api.model
    def _send_approver_reminder_cron(self):
        self._notify_substitute_approvers(
            self.env.company.approver_reminder,
            self._get_approvers_remind_domain(),
            "reminded",
        )

    @api.model
    def _send_manager_reminder_cron(self):
        self._notify_substitute_approvers(
            self.env.company.approver_reminder + 1,
            self._get_approvers_remind_manager_domain(),
            "manager_reminded",
        )

    @api.model
    def substitute_approvers_cron(self):
        self._notify_substitute_approvers(
            self.env.company.approver_reminder,
            self._get_approvers_substitute_domain(),
            "substituted",
        )

    def _get_approvers_remind_domain(self):
        return [("warning_level", "=", False)]

    def _get_approvers_remind_manager_domain(self):
        return [("warning_level", "=", "reminded")]

    def _get_approvers_substitute_domain(self):
        return [("warning_level", "=", "manager_reminded")]

    def _notify_substitute_approvers(self, approver_days, domain, next_state):
        if not approver_days:
            return

        domain.append(
            (
                "pending_timestamp",
                "<",
                fields.Datetime.now() - timedelta(days=approver_days),
            ),
        )
        approver_lines = self.search(domain)

        lines = approver_lines.additional_actions(next_state)

        lines._change_warning_level(next_state)

        for line in approver_lines:
            line._send_reminder_message(next_state)

    def _send_reminder_message(self, next_state):
        self.ensure_one()

        message_partner = self._get_message_partner(next_state)
        if not message_partner:
            _logger.info("Employee %s doesn't have a Manager" % self.user_id.name)
            return

        channel_data = self.env["mail.channel"].channel_get([message_partner.id])
        channel = self.env["mail.channel"].browse(channel_data["id"])
        message_text_values = self._prepare_notification_values(next_state)
        channel.message_post(
            subject=message_text_values[0],
            body=(message_text_values[1]),
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
            partner_ids=self.user_id.partner_id.ids,
        )

    def _get_message_partner(self, next_state):
        return (
            self.user_id.employee_id.approval_manager_id.user_id.partner_id
            if next_state == "manager_reminded"
            else self.user_id.partner_id
        )

    def _prepare_notification_values(self, next_state):
        self.ensure_one()

        if next_state == "reminded":
            message_text_values = self._get_message_reminder_text()
        elif next_state == "manager_reminded":
            message_text_values = self._get_message_reminder_manager_text()
        elif next_state == "substituted":
            message_text_values = self._get_message_substitute_text()
        else:
            message_text_values = ("", "")

        return message_text_values

    def _get_message_reminder_text(self):
        self.ensure_one()

        return (
            "Approval Request Reminder",
            "You have an Approval Request: %s pending." % self.request_id.name,
        )

    def _get_message_reminder_manager_text(self):
        self.ensure_one()

        return (
            "Approval Request Reminder",
            "Approver %s has an active approval request: %s, on which"
            "he didn't react in %s days."
            % (
                self.user_id.partner_id.name,
                self.request_id.name,
                self.env.company.approver_reminder + 1,
            ),
        )

    def _get_message_substitute_text(self):
        return (
            "Approval Request Substitute",
            "Dear Approver since you have not reacted on time, "
            "this approval request has been sent to a new Approver.",
        )

    def _change_warning_level(self, next_state):
        self.write({"warning_level": next_state})

    def additional_actions(self, next_state):
        """
        Hook method that can be used when we want to do some action
        when we change the warning state of an approver line.
        :returns modified self (approver lines)
        """
        return self._substitute_approvers(next_state)

    def _substitute_approvers(self, next_state):
        if next_state != "substituted":
            return self

        substituted_lines = self.env["approval.approver"]

        for rec in self:
            # We can't substitute Manager Approver line
            if not rec.matrix_line_id or rec._is_manager_approver():
                continue

            # We need to exclude from the search all approvers
            # on the request associated with the same matrix line.
            same_matrix_lines = rec.request_id.approver_ids.filtered(
                lambda x: x.matrix_line_id == rec.matrix_line_id
            )
            selected_users = rec.matrix_line_id.with_context(
                initiated_by_cron=True
            ).get_selected_approvers(
                invoked_from_model=rec.request_id.res_model,
                user_employee=rec.request_id.request_owner_id.employee_id,
                use_unavailable=True,
                exclude_user_ids=same_matrix_lines.mapped("user_id").ids,
                raise_if_not_found=False,
            )
            if not selected_users:
                continue

            rec.request_id.write(
                {
                    "approver_ids": [
                        Command.create(
                            {
                                "user_id": user.id,
                                "status": rec.status,
                                "sequence": rec.sequence,
                                "matrix_line_id": rec.matrix_line_id.id,
                            }
                        )
                        for user in selected_users
                    ]
                }
            )
            new_lines = rec.request_id.approver_ids.filtered(
                lambda x: x.user_id in selected_users
            )
            if next_state == "substituted":
                new_lines._create_activity()

            rec.write({"status": "cancel"})
            substituted_lines |= rec

        return substituted_lines

    def _is_manager_approver(self):
        self.ensure_one()

        return (
            self.matrix_line_id._get_employee_manager(
                self.request_id.request_owner_id.employee_id
            )
            == self.user_id.employee_id
        )

    def _remove_approvers_activities(self, approval_request_id):
        approvers_mail_activities = self.env["mail.activity"].search(
            [
                ("res_model", "=", "approval.request"),
                ("res_id", "=", approval_request_id),
                ("user_id", "in", self.mapped("user_id").ids),
            ]
        )
        approvers_mail_activities.unlink()
