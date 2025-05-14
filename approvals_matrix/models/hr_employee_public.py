# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import fields, models


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    approval_authorization_level_id = fields.Many2one(
        comodel_name="approval.authorization.level", readonly=True
    )
    approval_manager_id = fields.Many2one(comodel_name="res.users", readonly=True)
