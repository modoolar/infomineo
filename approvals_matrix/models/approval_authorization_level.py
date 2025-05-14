# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import api, fields, models


class ApprovalAuthorizationLevel(models.Model):
    _name = "approval.authorization.level"
    _rec_name = "common_name"
    _description = "Approval Authorization Level"

    name = fields.Char(required=True)
    authorization_level = fields.Integer()
    user_ids = fields.One2many(
        comodel_name="res.users",
        inverse_name="approval_authorization_level_id",
    )
    common_name = fields.Char(compute="_compute_common_name", store=True)

    @api.depends("name", "authorization_level")
    def _compute_common_name(self):
        for auth_level in self:
            auth_level.common_name = (
                auth_level.name + " - L" + str(auth_level.authorization_level)
            )
