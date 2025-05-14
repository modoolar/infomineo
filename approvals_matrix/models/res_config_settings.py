# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    include_parent_departments = fields.Boolean(
        related="company_id.include_parent_departments", readonly=False
    )
    approver_reminder = fields.Integer(
        related="company_id.approver_reminder",
        readonly=False,
        help="Approver Reminder period in days.",
    )
    approver_substitution = fields.Integer(
        related="company_id.approver_substitution",
        readonly=False,
        help="Approver Substitution period in days.",
    )
    hr_communication_channel_id = fields.Many2one(
        related="company_id.hr_communication_channel_id",
        readonly=False,
    )
    additional_approver_buffer = fields.Integer(
        related="company_id.additional_approver_buffer",
        readonly=False,
    )

    @api.constrains("approver_reminder", "approver_substitution")
    def _validate_approver_request_days(self):
        for rec in self.filtered(
            lambda x: x.approver_reminder or x.approver_substitution
        ):
            if rec.approver_reminder >= rec.approver_substitution:
                raise UserError(
                    _(
                        "Approver Substitution needs to be greater "
                        "than Approver Reminder (in days)."
                    )
                )
