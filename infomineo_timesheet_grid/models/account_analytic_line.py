# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    validated = fields.Boolean("Is Validated")
    validated_on = fields.Datetime(compute="_compute_validated_on", store=True)

    @api.depends("validated")
    def _compute_validated_on(self):
        for rec in self:
            rec.validated_on = fields.Datetime.now() if rec.validated else None

    def handle_timesheet_action(self, action_method):
        if self.user_has_groups(
            "infomineo_timesheet_grid.group_timesheet_team_approver"
        ):
            manager_timesheet_group = self.env.ref(
                "hr_timesheet.group_hr_timesheet_approver"
            )
            self.env.user.groups_id += manager_timesheet_group
            result = action_method()
            self.env.user.groups_id -= manager_timesheet_group
            return result
        return action_method()

    def action_validate_timesheet(self):
        return self.sudo().handle_timesheet_action(super().action_validate_timesheet)

    def action_invalidate_timesheet(self):
        return self.handle_timesheet_action(super().action_invalidate_timesheet)

    def write(self, vals):
        if (
            "validated" in vals
            and self.user_has_groups(
                "infomineo_timesheet_grid.group_timesheet_team_approver"
            )
            and not self.user_has_groups("hr_timesheet.group_hr_timesheet_approver")
        ):
            manager_timesheet_group = self.env.ref(
                "hr_timesheet.group_hr_timesheet_approver"
            )
            self.env.user.groups_id += manager_timesheet_group
            result = super().write(vals)
            self.env.user.groups_id -= manager_timesheet_group
            return result
        return super().write(vals)

    def _get_domain_for_validation_timesheets(self, validated=False):
        """Override of the base timesheet validation domain method
        to include Team Approver rights.

        This override modifies the base domain logic
        to enable Team Approvers to validate timesheets
        without requiring additional manager relationships.
        This makes validation behavior consistent
        across both validation methods (checkbox list and action dropdown).
        """
        if self.user_has_groups(
            "infomineo_timesheet_grid.group_timesheet_team_approver"
        ):
            return [("is_timesheet", "=", True), ("validated", "=", validated)]

        return super()._get_domain_for_validation_timesheets(validated=validated)
