# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)


from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _get_domain_for_automated_leave_types(self):
        self.ensure_one()
        return [
            ("is_automated_leave_type", "=", True),
            ("company_id", "=", self.company_id.id),
        ]

    def _get_vals_for_automated_leave_allocation(self, leave_type):
        self.ensure_one()
        accrual_plan_type_and_days = (
            leave_type.get_automated_accrual_plan_allocation_type_and_number_of_days(
                self
            )
        )
        allocation_type = accrual_plan_type_and_days.get("allocation_type", False)
        is_not_accrual = allocation_type and allocation_type != "accrual"
        vals = {
            "employee_id": self.id,
            "employee_ids": [(4, self.id)],
            "private_name": leave_type.name + " " + str(fields.Date.today().year),
            "holiday_status_id": leave_type.id,
            "is_automated_leave_allocation": True,
            "state": "validate",
            "accrual_plan_id": accrual_plan_type_and_days.get("accrual_plan_id", False),
            "allocation_type": allocation_type,
            "number_of_days": accrual_plan_type_and_days.get("number_of_days", False),
        }
        if is_not_accrual:
            vals["date_to"] = fields.Date.context_today(self).replace(month=12, day=31)
        return vals

    def _get_new_automated_leave_allocations(self):
        return self.env["hr.leave.allocation"].search(
            [
                ("employee_id", "=", self.id),
                ("is_automated_leave_allocation", "=", "True"),
            ]
        )

    def _create_automated_leave_allocation(self):
        self.ensure_one()
        automated_leave_type_ids = self.env["hr.leave.type"].search(
            self._get_domain_for_automated_leave_types()
        )
        for leave_type in automated_leave_type_ids:
            creation_vals = self._get_vals_for_automated_leave_allocation(leave_type)
            self.env["hr.leave.allocation"].create(creation_vals)

    def _delete_automated_leave_allocation(self):
        self.ensure_one()
        automated_leave_alllocations = self.env["hr.leave.allocation"].search(
            [
                ("employee_id", "=", self.id),
                ("is_automated_leave_allocation", "=", True),
                ("state", "=", "validate"),
            ]
        )
        automated_leave_alllocations.action_refuse()
        automated_leave_alllocations.action_draft()
        automated_leave_alllocations.unlink()

    def _process_allocations(self):
        for employee in self:
            automated_hr_leave_allocation_ids = (
                employee.sudo()._get_new_automated_leave_allocations()
            )
            for allocation in automated_hr_leave_allocation_ids:
                allocation._set_dates(employee)
