# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import api, fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    approval_authorization_level_id = fields.Many2one(
        comodel_name="approval.authorization.level", copy=False
    )
    approval_manager_id = fields.Many2one(related="employee_id.approval_manager_id")
    is_manager_missing = fields.Boolean(compute="_compute_is_manager_missing")

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + ["approval_manager_id"]

    @api.model
    def _get_implied_groups(self, user):
        """
        Returns implied groups
        """
        return user.groups_id

    @api.depends("employee_ids")
    def _compute_is_manager_missing(self):
        for user in self:
            user.is_manager_missing = (
                len(user.employee_ids.filtered(lambda e: not e.approval_manager_id)) > 0
            )
