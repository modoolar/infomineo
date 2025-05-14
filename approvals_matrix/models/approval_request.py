# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
import os

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import groupby


class ApprovalRequest(models.Model):
    _inherit = "approval.request"

    active_approval_line = fields.Integer(
        compute="_compute_active_approval_line", store=True
    )
    max_approval_line = fields.Integer()
    is_advanced = fields.Boolean(related="category_id.is_advanced")
    origin_object_count = fields.Integer(compute="_compute_origin_object_count")
    source_document = fields.Reference(selection="_selection_source_document")
    res_id = fields.Integer()
    res_model = fields.Char()
    approval_rule_id = fields.Many2one(
        comodel_name="approval.rule", ondelete="restrict"
    )
    current_matrix_line_sequence = fields.Integer(
        compute="_compute_active_approval_line", store=True
    )
    active = fields.Boolean(default=True)
    is_override_button_visible = fields.Boolean(
        compute="_compute_is_override_button_visible"
    )
    can_user_see_companies = fields.Boolean(compute="_compute_can_user_see_companies")
    approval_method_name = fields.Char()
    approval_model_state = fields.Char()

    def _compute_can_user_see_companies(self):
        for rec in self:
            rec.can_user_see_companies = (
                rec.company_id.id
                in self.env.company.ids
                + self.env.context.get("allowed_company_ids", [])
            )

    @api.depends("active_approval_line", "request_status", "approver_ids.user_id")
    def _compute_is_override_button_visible(self):
        advanced_requests = self.filtered(lambda x: x.is_advanced)
        for rec in advanced_requests:
            if (
                rec.approval_rule_id._can_override_approval()
                and rec.request_status == "pending"
            ):
                rec.is_override_button_visible = True
            else:
                rec.is_override_button_visible = bool(
                    rec.request_status == "pending"
                    and rec.approver_ids.filtered(
                        lambda x: x.user_id == self.env.user
                        and x.matrix_line_id.sequence
                        != min(
                            self.approver_ids.mapped("matrix_line_id.sequence"),
                            default=-1,
                        )
                        and x.status in ["new", "pending", "waiting"]
                    )
                )

        (self - advanced_requests).is_override_button_visible = False

    def create_request_status_activity(self, message_type):

        for req in self:
            message = ""
            partner_ids = []
            if message_type == "create":
                message = req._get_request_approval_created_activity_message()
            elif message_type == "change_status":
                message = req._get_request_status_activity_message()
                req_user = self._get_req_submitter()
                partner_ids = req_user.partner_id.ids

            req.source_document.with_user(SUPERUSER_ID).message_post(
                body=message,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
                partner_ids=partner_ids,
            )

    def _get_request_approval_created_activity_message(self):
        self.ensure_one()

        current_req = self._get_current_request_link_message()
        return _("New Approval Request %s is created.") % current_req

    def _get_request_status_activity_message(self):
        self.ensure_one()

        req_submitter_message = self._get_req_submitter_link_message()

        return _("%s Approval request has been %s") % (
            req_submitter_message,
            self.request_status,
        )

    def _get_req_submitter_link_message(self):
        req_user = self._get_req_submitter()
        if req_user:
            return (
                _(
                    """<a href="/web#model=res.partner&amp;id=%s"
                 class="o_mail_redirect" data-oe-id="%s"
                 data-oe-model="res.partner" target="_blank">@%s</a>"""
                )
                % (
                    req_user.partner_id.id,
                    req_user.partner_id.id,
                    req_user.partner_id.name,
                )
            )
        else:
            return ""

    def _get_req_submitter(self):
        notification_field = self._get_notification_field()
        return (
            self.env[self.res_model].browse(self.res_id)[notification_field]
            if notification_field
            else self.env["res.users"]
        )

    def _get_notification_field(self):
        self.ensure_one()

        has_notification_field = getattr(
            self.env[self.res_model], "_notification_field", False
        )
        return (
            self.env[self.res_model]._notification_field
            if has_notification_field
            else False
        )

    def _get_current_request_link_message(self):
        return _("<a href=# data-oe-model=%s data-oe-id=%s>%s</a>") % (
            self._name,
            self.id,
            self.name,
        )

    @api.model
    def _selection_source_document(self):
        return [
            (model.model, model.name)
            for model in self.env["ir.model"]
            .sudo()
            .search(
                [
                    ("approval_request_link", "=", True),
                    ("model", "!=", "ir.model"),
                ]
            )
        ]

    @api.depends("approver_ids", "approver_ids.status")
    def _compute_active_approval_line(self):
        advanced_requests = self.filtered(lambda x: x.is_advanced)
        for request in advanced_requests:
            (
                request.active_approval_line,
                request.current_matrix_line_sequence,
            ) = request._get_approved_levels()

        (self - advanced_requests).active_approval_line = 0
        (self - advanced_requests).current_matrix_line_sequence = 0

    @api.depends("approver_ids.status", "approver_ids.required")
    def _compute_request_status(self):
        advanced_requests = self.filtered(lambda x: x.is_advanced)

        for request in advanced_requests:
            request.request_status = request._get_advanced_request_status()

        advanced_requests.filtered(
            lambda x: x.is_advanced and x.request_status in ["approved", "refused"]
        ).create_request_status_activity(message_type="change_status")

        advanced_requests.filtered(
            lambda x: x.is_advanced
            and x.request_status == "approved"
            and x.source_document.state == x.approval_model_state
            and x.approval_rule_id.action_type == "confirm"
            and x.approval_rule_id.automatic_document_confirmation
        )._confirm_source_document()

        super(ApprovalRequest, self - advanced_requests)._compute_request_status()

    def _confirm_source_document(self):
        """
        If a request is an advanced request, request_status is approved,
        action_type of approval rule is confirm,
        and automatic_document_confirmation flag is set on approval rule,
        we will change Odoo's logic to automatically
        confirm the source document.
        """
        for request in self:
            getattr(request.source_document, request.approval_method_name)()

    def _compute_origin_object_count(self):
        for request in self:
            request.origin_object_count = 1 if request.source_document else 0

    def _get_advanced_request_status(self):
        self.ensure_one()

        if any(x == "refused" for x in self.approver_ids.mapped("status")):
            request_status = "refused"
        elif all(x == "cancel" for x in self.approver_ids.mapped("status")):
            request_status = "cancel"
        elif any(x == "pending" for x in self.approver_ids.mapped("status")):
            request_status = "pending"
        elif self.active_approval_line == self.max_approval_line:
            request_status = "approved"
        else:
            request_status = "new"
        return request_status

    def action_approve(self, approver=None):
        super().action_approve(approver=approver)

        if not isinstance(approver, models.BaseModel):
            approver = self.mapped("approver_ids").filtered(
                lambda approver: approver.user_id == self.env.user
            )
        self.sudo()._update_next_approvers(approver, cancel_activities=False)

    def action_refuse(self, approver=None):
        super().action_refuse(approver=approver)

        if not isinstance(approver, models.BaseModel):
            approver = self.mapped("approver_ids").filtered(
                lambda approver: approver.user_id == self.env.user
            )
        self.sudo()._update_next_approvers(approver, cancel_activities=True)

    def _cancel_activities(self):
        approval_activity = self.env.ref("approvals.mail_activity_data_approval")
        activities = self.activity_ids.filtered(
            lambda a: a.activity_type_id == approval_activity
        )
        activities.unlink()

    def _update_next_approvers(self, approver, cancel_activities=False):
        """
        If a request is an advanced request, we will change Odoo's logic to
        cancel all other Approvers statuses and activities if the request is Refused.
        The logic is that if someone Refuses the request, Request is Refused,
        and all other Activities that are yet to be responded by Approvers are
        canceled and their statuses are changed to Cancel.
        """

        advanced_requests = self.filtered("is_advanced")

        advanced_requests._update_advanced_next_approvers(
            approver=approver,
            cancel_activities=cancel_activities,
        )

    def _update_advanced_next_approvers(self, approver, cancel_activities=False):
        if any(self.filtered(lambda x: not x.is_advanced)):
            raise UserError(
                _("You need to call this method only for Advanced Approvals.")
            )
        approver.flush()

        approvers_updated = self.env["approval.approver"]
        for approval in self:

            if approver.status == "approved":

                # We are going to check if minimum approval number has been made
                # and we need to cancel the rest of the approvers of that level.
                is_matrix_line_approved = approval._check_matrix_line_approved(approver)
                if (
                    is_matrix_line_approved
                    or self.env.context.get("override_approvers_wizard") == os.getpid()
                ):
                    next_approvers = approval.approver_ids.filtered(
                        lambda x: x.matrix_line_id.sequence
                        == approval.current_matrix_line_sequence
                    )
                    next_approvers = (
                        next_approvers - approver
                        if self.env.context.get("override_approvers_wizard")
                        == os.getpid()
                        else next_approvers
                    )
                    if next_approvers:
                        next_approvers.sudo().write({"status": "pending"})
                        next_approvers._create_activity()
            elif approver.status == "refused":
                if cancel_activities:
                    next_approvers = approval.approver_ids.filtered(
                        lambda x: x.matrix_line_id.sequence
                        > approval.current_matrix_line_sequence
                        and x != approver
                    )
                    if next_approvers:
                        next_approvers.sudo().write({"status": "cancel"})
                    approvers_updated.request_id._cancel_activities()
                    approval.active = False
            elif approver.status == "waiting":
                if (
                    approver.matrix_line_id.sequence
                    == approval.current_matrix_line_sequence
                ):
                    approver.status = "pending"

    def _check_matrix_line_approved(self, approver):
        self.ensure_one()

        same_level_approver_lines = self.approver_ids.filtered(
            lambda x: x.matrix_line_id == approver.matrix_line_id
        )
        approved_lines = same_level_approver_lines.filtered(
            lambda x: x.status == "approved"
        )
        if len(approved_lines) >= approver.matrix_line_id.minimum_approvals:
            buffer_approvers = same_level_approver_lines - approved_lines
            self.cancel_buffers(buffer_approvers)
            return True
        return False

    def cancel_buffers(self, buffer_approvers):
        self.ensure_one()

        if buffer_approvers:
            buffer_approvers.write({"status": "cancel"})

            activities = self.activity_ids.filtered(
                lambda x: x.user_id in buffer_approvers.mapped("user_id")
            )
            activities.unlink()

    def action_draft(self):
        if any(self.mapped("is_advanced")):
            raise UserError(_("You are not allowed to perform this operation!"))
        super().action_draft()

    def action_cancel(self):
        if any(self.mapped("is_advanced")):
            raise UserError(_("You are not allowed to perform this operation!"))
        super().action_cancel()

    def action_withdraw(self, approver=None):
        if any(self.mapped("is_advanced")):
            raise UserError(_("You are not allowed to perform this operation!"))
        super().action_withdraw(approver=approver)

    def _get_approved_levels(self):
        self.ensure_one()

        employee_manager = self.sudo()._get_owner_parent(raise_error=True)

        no_approval_level = 0
        sequences = self.approver_ids.mapped("matrix_line_id.sequence")
        if not sequences:
            raise UserError(_("You don't have sequences for Approval Rule Lines."))
        current_matrix_line_sequence = min(sequences)
        finished_lines = self.env["advanced.approval.category.approver"]
        for advanced_approver, advanced_approver_grouped_request_approvers in groupby(
            self.approver_ids, lambda x: x.matrix_line_id
        ):
            minimum_approved = advanced_approver.minimum_approvals
            manager_approved = False

            for approver in advanced_approver_grouped_request_approvers:
                if (
                    minimum_approved <= 0
                    and advanced_approver.use_employee_manager == manager_approved
                ):
                    break
                if approver.status == "approved":
                    minimum_approved -= 1
                    if (
                        advanced_approver.use_employee_manager
                        and approver.user_id.employee_id == employee_manager
                    ):
                        manager_approved = True

            if minimum_approved <= 0:
                no_approval_level += 1
                finished_lines |= advanced_approver
                unfinished_lines = (
                    self.mapped("approver_ids.matrix_line_id") - finished_lines
                )
                if unfinished_lines:
                    current_matrix_line_sequence = min(
                        (unfinished_lines).mapped("sequence")
                    )
                else:
                    current_matrix_line_sequence += 1

        return no_approval_level, current_matrix_line_sequence

    def _get_owner_parent(self, raise_error=False):
        self.ensure_one()

        employee_owner = self.env["hr.employee"].search(
            [("user_id", "=", self.request_owner_id.id)], limit=1
        )
        if raise_error:
            self._check_advanced_manager(employee_owner)

        return employee_owner.approval_manager_id

    def _check_advanced_manager(self, employee_owner):
        self.ensure_one()

        if any(self.mapped("category_id.advanced_approver_ids.use_employee_manager")):

            if not employee_owner.approval_manager_id:
                raise UserError(
                    _(
                        "This request needs to be approved by your manager. "
                        "There is no manager linked to your employee profile."
                    )
                )
            if not employee_owner.approval_manager_id:
                raise UserError(
                    _(
                        "This request needs to be approved by your manager. "
                        "There is no user linked to your manager."
                    )
                )
            if not self.approver_ids.filtered(
                lambda a: a.user_id == employee_owner.approval_manager_id
            ):
                raise UserError(
                    _(
                        "This request needs to be approved by your manager. "
                        "Your manager is not in the approvers list."
                    )
                )

    def action_view_origin_object(self):
        self.ensure_one()

        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale.action_quotations_with_onboarding"
        )

        if self.origin_object_count == 1:
            action["views"] = [(self.env.ref("sale.view_order_form").id, "form")]
            action["res_id"] = self.source_document.id
            action["context"] = dict(self._context)
        return action

    def action_override_approvers(self):
        self.ensure_one()
        res = self.env["ir.actions.act_window"]._for_xml_id(
            "approvals_matrix.override_approvers_wizard_action"
        )
        res["context"] = {"default_approval_request_id": self.id}
        return res

    def get_current_user_approver(self):
        self.ensure_one()

        return self.approver_ids.filtered(lambda x: x.user_id == self.env.user)
