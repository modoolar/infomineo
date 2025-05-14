# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models

from odoo.addons.approvals_matrix.models.approval_rule import (
    approval_cancel_action,
    approval_pending_message,
    check_approval_rules,
)


class PurchaseRequisition(models.Model):
    _name = "purchase.requisition"
    _inherit = ["approval.matrix.mixin", "purchase.requisition"]
    _approval_request_link = True
    _notification_field = "user_id"

    @approval_pending_message
    @check_approval_rules(action_type="confirm")
    def action_in_progress(self):
        return super().action_in_progress()

    @approval_cancel_action
    def action_cancel(self):
        return super().action_cancel()
