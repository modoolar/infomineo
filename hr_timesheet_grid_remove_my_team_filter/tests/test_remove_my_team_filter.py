# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestNoMyTeamFilterOnTimesheets(TransactionCase):
    def test_no_my_team_filter_timesheet_grid(self):
        """
        Check if default filter `my_team_timesheet` is present
        in the context after action is called
        """
        action = self.env[
            "account.analytic.line"
        ]._action_open_to_validate_timesheet_view()
        default_my_team_filter = (
            action["context"].get("search_default_my_team_timesheet", False)
            if action.get("context")
            else False
        )
        self.assertFalse(
            default_my_team_filter,
            "My Team filter is present in action, but it shouldn't be",
        )
