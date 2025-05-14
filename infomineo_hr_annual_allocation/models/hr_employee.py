# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
import logging
import time
from datetime import datetime

from odoo import models

_logger = logging.getLogger(__name__)

DAYS_OFF_MAP_BY_COUNTRY = {
    "MA": {
        "timeoff_carryover_limit": 5,
        "sick_leave_plan": {
            "per_year": 5,
            "multiyear": {"quantity": False, "years": False},
            "accrual_xml_id": "False",
        },
        "seniority": {
            (0, 4): 20,
            (5, 9): 21.5,
            (10, 14): 23,
            (15, 19): 24.5,
            (20, 24): 26,
            (25, 29): 27.5,
            (30, 37): 29,
            (35, -1): 30,
        },
    },
    "ES": {
        "timeoff_carryover_limit": 5,
        "sick_leave_plan": {
            "per_year": 5,
            "multiyear": {"quantity": False, "years": False},
            "accrual_xml_id": "False",
        },
        "seniority": {
            (0, -1): 23,
        },
    },
    "MX": {
        "timeoff_carryover_limit": 5,
        "sick_leave_plan": {
            "per_year": 5,
            "multiyear": {"quantity": False, "years": False},
            "accrual_xml_id": "False",
        },
        "seniority": {
            (0, 1): 15,
            (2, 3): 17,
            (4, 4): 18,
            (5, 5): 20,
            (6, 10): 22,
            (11, 15): 24,
            (16, 20): 26,
            (21, 25): 28,
            (26, 30): 30,
            (31, 35): 32,
        },
    },
}

MAP_LEAVE_TYPE = {
    "holiday": "work_entry_type_leave",
    "sick_leave": "work_entry_type_sick_leave",
}


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    def allocate_annual_employee_time_off(self):
        """
        Loop through all employees with active contract, and based on the country, take
        allocation rules from mapper needed for creation of new allocations.
        """
        employees = self.search([])
        for employee in employees.filtered(lambda x: x.contract_id.state == "open"):
            employee_country = employee.address_id.country_id.code
            if employee_country and DAYS_OFF_MAP_BY_COUNTRY.get(
                employee_country, False
            ):
                time_off_map = DAYS_OFF_MAP_BY_COUNTRY[employee_country]
                self.create_sick_leave(time_off_map, employee)
        _logger.info("Allocation generation cron completed.")

    def create_sick_leave(self, time_off_map, employee):
        """
        Create sick leave type allocation for employee
        based on mapper differentiated by employee country.
        If we cant find per_year value in mapper, we need
        to create multiyear sick leave. Cancel all
        old allocations.
        """
        number_of_days = time_off_map["sick_leave_plan"]["per_year"]
        leave_type = self.get_leave_type(employee, MAP_LEAVE_TYPE["sick_leave"])
        if not leave_type:
            _logger.info(
                f"Missing leave type for company {employee.company_id.name}, "
                f"allocation not created for employee {employee.name}!"
            )
            return False
        old_allocations = self.get_old_allocations(employee, leave_type)
        accrual = False
        date_to = time.strftime("%Y-12-31")
        allocation = self.env["hr.leave.allocation"].create(
            {
                "name": f"Sick leave {employee.name}, {datetime.now().year}",
                "holiday_status_id": leave_type.id,
                "number_of_days": number_of_days,
                "employee_id": employee.id,
                "date_from": time.strftime("%Y-01-01"),
                "allocation_type": "accrual" if accrual else "regular",
                "accrual_plan_id": accrual and accrual.id,
                "date_to": date_to,
            }
        )
        _logger.info(f"Sick leave created. - {allocation.name}")

        old_allocations.write({"state": "cancel"})
        allocation.sudo().action_confirm()
        allocation.sudo().action_validate()

    def get_leave_type(self, employee, leave_type):
        """
        Take leave type from mapper(xml id of hr_work_entry_contract).
        """
        leave_type_model = self.env["hr.leave.type"]
        leave_type = leave_type_model.search(
            [
                (
                    "name",
                    "ilike",
                    "Sick Leave (%s)" % (employee.company_id.country_id.name),
                ),
                ("company_id", "=", employee.company_id.id),
            ]
        )
        return leave_type and leave_type[0] or leave_type_model

    def get_old_allocations(self, employee, leave_type):
        ret = self.env["hr.leave.allocation"].search(
            [
                ("employee_id", "=", employee.id),
                ("holiday_status_id", "=", leave_type.id),
                ("state", "!=", "cancel"),
                ("date_to", "!=", False),
            ],
            order="date_from desc",
        )
        return ret
