# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models

from odoo.addons.approvals_matrix.models.approval_rule import (
    approval_cancel_action,
    approval_pending_message,
    check_approval_rules,
)


class PurchaseOrder(models.Model):
    _name = "purchase.order"
    _inherit = ["approval.matrix.mixin", "purchase.order"]
    _approval_request_link = True
    _notification_field = "user_id"

    @approval_pending_message
    @check_approval_rules(action_type="confirm")
    def button_confirm(self):
        return super().button_confirm()

    @approval_pending_message
    @check_approval_rules(action_type="send_by_mail")
    def action_rfq_send(self):
        return super().action_rfq_send()

    @approval_cancel_action
    def button_cancel(self):
        return super().button_cancel()
