from odoo import api

from odoo.addons.hr.models.res_users import User as originalUser


@api.depends("employee_ids")
@api.depends_context("company")
def _compute_company_employee(self):
    employee_per_user = {
        employee.user_id: employee
        for employee in self.env["hr.employee"].search(
            [
                ("user_id", "in", self.ids),
                ("company_id", "in", self.env.user.company_ids.ids),
                ("active", "=", True),
            ]
        )
    }
    for user in self:
        user.employee_id = employee_per_user.get(user)


def post_load():
    originalUser._patch_method("_compute_company_employee", _compute_company_employee)
