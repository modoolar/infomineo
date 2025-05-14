# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class PurchaseOrderLine(models.Model):
    _name = "purchase.order.line"
    _inherit = ["approval.matrix.mixin", "purchase.order.line"]
    _approval_request_link = True
    _parent_tracking_fields = "order_id"
