# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class PurchaseRequisitionLine(models.Model):
    _name = "purchase.requisition.line"
    _inherit = ["approval.matrix.mixin", "purchase.requisition.line"]
    _approval_request_link = True
    _parent_tracking_fields = "requisition_id"
