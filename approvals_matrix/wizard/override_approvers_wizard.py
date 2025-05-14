# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
import os

from odoo import _, fields, models
from odoo.exceptions import UserError


class OverrideApproversWizard(models.TransientModel):
    _name = "override.approvers.wizard"
    _description = "Override Approvers Wizard"

    approval_request_id = fields.Many2one(comodel_name="approval.request")

    def action_approve(self):
        self.ensure_one()

        self_approver = self.approval_request_id.get_current_user_approver()

        is_overridden = self._override_approval(self_approver, "approved")
        if is_overridden:
            return

        if not self_approver:
            raise UserError(_("You are not an approver on this request."))

        approvers = self.approval_request_id.approver_ids.filtered(
            lambda x: x.sequence < self_approver.sequence and x.status != "approved"
        )

        approvers.sudo().write(
            {"status": "approved", "overridden_by_id": self.env.user.id}
        )
        approvers._remove_approvers_activities(self.approval_request_id.id)

        self_approver.with_context(
            override_approvers_wizard=os.getpid()
        ).action_approve()

    def action_refuse(self):
        self.ensure_one()

        self_approver = self.approval_request_id.get_current_user_approver()

        is_overridden = self._override_approval(self_approver, "refused")
        if is_overridden:
            return

        if not self_approver:
            raise UserError(_("You are not an approver on this request."))

        approvers = self.approval_request_id.approver_ids.filtered(
            lambda x: x.status != "approved" and x != self_approver
        )
        self_approver.action_refuse()

        approvers.sudo().write(
            {"status": "cancel", "overridden_by_id": self.env.user.id}
        )

    def _override_approval(self, self_approver, state):

        if (
            self.approval_request_id.approval_rule_id._can_override_approval()
            and not self_approver
        ):
            current_user = self.env.user

            approval_lines = self.approval_request_id.approver_ids

            approval_lines.sudo().write(
                {"status": state, "overridden_by_id": current_user.id}
            )
            self.approval_request_id.sudo()._get_user_approval_activities(
                user=current_user
            ).action_feedback()
            approval_lines._remove_approvers_activities(self.approval_request_id.id)
            return True
        return False
