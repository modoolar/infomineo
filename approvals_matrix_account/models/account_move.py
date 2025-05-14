# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models

from odoo.addons.approvals_matrix.models.approval_rule import (
    approval_cancel_action,
    approval_pending_message,
    check_approval_rules,
)


class AccountMove(models.Model):
    _name = "account.move"
    _inherit = ["approval.matrix.mixin", "account.move"]
    _approval_request_link = True
    _notification_field = "invoice_user_id"

    @approval_pending_message
    @check_approval_rules(action_type="confirm")
    def action_post(self):
        return super().action_post()

    @approval_pending_message
    @check_approval_rules(action_type="send_by_mail")
    def action_invoice_sent(self):
        return super().action_invoice_sent()

    @approval_cancel_action
    def button_cancel(self):
        return super().button_cancel()
