# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class AccountMoveLine(models.Model):
    _name = "account.move.line"
    _inherit = ["approval.matrix.mixin", "account.move.line"]
    _approval_request_link = True
    _parent_tracking_fields = "move_id"
