# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class SaleOrderLine(models.Model):
    _name = "sale.order.line"
    _inherit = ["approval.matrix.mixin", "sale.order.line"]
    _approval_request_link = True
    _parent_tracking_fields = "order_id"
