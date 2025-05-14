# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models

from odoo.addons.approvals_matrix.models.approval_rule import (
    approval_cancel_action,
    approval_pending_message,
    check_approval_rules,
)


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["approval.matrix.mixin", "sale.order"]
    _approval_request_link = True
    _notification_field = "user_id"

    @approval_pending_message
    @check_approval_rules(action_type="confirm")
    def action_confirm(self):
        return super().action_confirm()

    @approval_pending_message
    @check_approval_rules(action_type="send_by_mail")
    def action_quotation_send(self):
        return super().action_quotation_send()

    @approval_cancel_action
    def action_cancel(self):
        return super().action_cancel()
