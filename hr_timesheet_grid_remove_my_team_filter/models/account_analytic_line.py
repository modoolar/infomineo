# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _action_open_to_validate_timesheet_view(self, type_view="week"):
        """
        Remove default filter my_team_timesheet if it is in context
        """
        action = super()._action_open_to_validate_timesheet_view(type_view=type_view)
        if action.get("context") and action["context"].get(
            "search_default_my_team_timesheet"
        ):
            action["context"]["search_default_my_team_timesheet"] = False
        return action
