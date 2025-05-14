# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    include_parent_departments = fields.Boolean()
    approver_reminder = fields.Integer()
    approver_substitution = fields.Integer()
    hr_communication_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        default=lambda x: x._default_hr_communication_channel(),
    )
    additional_approver_buffer = fields.Integer(default=0)

    @api.model
    def _default_hr_communication_channel(self):
        return self.env.ref(
            "approvals_matrix.channel_approvals_hr", raise_if_not_found=False
        )
