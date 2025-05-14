# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.depends("employee_ids")
    @api.depends_context("company")
    def _compute_company_employee(self):
        if self.env.context.get("view_leave_requests"):
            employee_per_user = {
                employee.user_id: employee
                for employee in self.env["hr.employee"].search(
                    [
                        ("user_id", "in", self.ids),
                        ("company_id", "in", self.env.user.company_ids.ids),
                    ]
                )
            }
            for user in self:
                user.employee_id = employee_per_user.get(user)
        else:
            super(ResUsers, self)._compute_company_employee()
