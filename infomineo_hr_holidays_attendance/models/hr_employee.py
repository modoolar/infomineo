# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _compute_show_leaves(self):
        """
        Overridden Odoo's compute method for field `show_leaves` to change the
        group from hr_user to hr_coach.
        """
        show_leaves = self.env["res.users"].has_group(
            "infomineo_hr_attendance.group_hr_coach"
        )
        for employee in self:
            if show_leaves or employee.user_id == self.env.user:
                employee.show_leaves = True
            else:
                employee.show_leaves = False
