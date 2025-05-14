# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import datetime

from dateutil.relativedelta import relativedelta
from freezegun import freeze_time

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.infomineo_hr_holidays_accruals.tests.common import (
    TestHrHolidaysAccrualsCommon,
)


class TestAccrualAllocationsFutureDays(TestHrHolidaysAccrualsCommon):
    def setUp(self):
        super(TestAccrualAllocationsFutureDays, self).setUp()

    def _get_employees_future_virtual_remaining_leaves(self, employee_id, date):
        self.leave_type = self.leave_type.with_context(test_date_from=date)
        return self.leave_type.get_employees_days([employee_id], date)[employee_id][
            self.leave_type.id
        ]["virtual_remaining_leaves"]

    def test_daily_frequency_future_approve(self):
        """
        This test is made to check if the future allocation is working properly
        for the daily frequency. Allocation is created with 1 day and with the
        accrual_plan_daily which add 1 day per day. After the allocation is
        confirmed and validated, the remaining leaves should be 1. Then, the
        future_virtual_remaining_leaves is checked for the new_date, and it
        should be 5. After that, we are trying to create the new time off request
        with 9 days duration, and it should raise the validation error. Then, we
        are trying to create and approve the new time off request with 5 days
        duration, and it should be approved.
        """
        self.assertEqual(
            self.allocation.number_of_days, 1, "There should be 1 day allocated"
        )
        self.allocation.action_confirm()
        self.allocation.action_validate()
        first_date = datetime.date(2024, 6, 27)
        first_date_virtual_remaining_leaves = (
            self._get_employees_future_virtual_remaining_leaves(
                self.employee_emp.id, first_date
            )
        )
        self.assertEqual(
            first_date_virtual_remaining_leaves, 1, "There should be 1 remaining leave"
        )

        new_date = first_date + relativedelta(days=3)
        with freeze_time(self.start_date):
            future_virtual_remaining_leaves = (
                self._get_employees_future_virtual_remaining_leaves(
                    self.employee_emp.id, new_date
                )
            )
            self.assertEqual(
                future_virtual_remaining_leaves, 5, "There should be 5 days allocated"
            )
            with self.assertRaises(
                ValidationError,
                msg=(
                    _(
                        "The number of remaining time off is"
                        " not sufficient for this time off type.\n"
                    )
                ),
            ):
                self.env["hr.leave"].with_context(test_date_from=new_date).create(
                    {
                        "name": "Test Time Off",
                        "employee_id": self.employee_emp.id,
                        "holiday_status_id": self.leave_type.id,
                        "date_from": new_date,
                        "date_to": new_date + relativedelta(days=9),
                    }
                )

            future_hr_leave_1 = (
                self.env["hr.leave"]
                .with_context(test_date_from=new_date)
                .create(
                    {
                        "name": "Test Time Off",
                        "employee_id": self.employee_emp.id,
                        "holiday_status_id": self.leave_type.id,
                        "date_from": new_date,
                        "date_to": new_date + relativedelta(days=5),
                    }
                )
            )
            future_hr_leave_1.action_approve()
            self.assertEqual(
                future_hr_leave_1.state, "validate", "Time off request is approved"
            )

    def test_monthly_frequency_future_approve(self):
        """
        This test is made to check if the future allocation is working properly
        for the monthly frequency. Allocation is created with 1 day and with the
        accrual_plan_monthly which add 1 day per month. After the allocation is
        confirmed and validated, the remaining leaves should be 1. Then, the
        future_virtual_remaining_leaves is checked for the new_date, and it
        should be between 3 and 4. After that, we are trying to create the new
        time off request with 7 days duration, and it should raise the validation
        error. Then, we are trying to create and approve the new time off request
        with 3 days duration, and it should be approved.
        """
        self.allocation.accrual_plan_id = self.accrual_plan_monthly.id
        self.allocation.action_confirm()
        self.allocation.action_validate()
        first_date = datetime.date(2024, 6, 27)
        first_date_virtual_remaining_leaves = (
            self._get_employees_future_virtual_remaining_leaves(
                self.employee_emp.id, first_date
            )
        )
        self.assertEqual(
            first_date_virtual_remaining_leaves, 1, "There should be 1 remaining leave"
        )

        new_date = first_date + relativedelta(months=3)
        with freeze_time(self.start_date):
            future_virtual_remaining_leaves = (
                self._get_employees_future_virtual_remaining_leaves(
                    self.employee_emp.id, new_date
                )
            )
            self.assertGreater(
                future_virtual_remaining_leaves,
                3,
                "There should be more than 3 days allocated",
            )
            self.assertLess(
                future_virtual_remaining_leaves,
                4,
                "There should be less than 4 days allocated",
            )

            with self.assertRaises(
                ValidationError,
                msg=(
                    _(
                        "The number of remaining time off"
                        " is not sufficient for this time off type.\n"
                    )
                ),
            ):
                self.env["hr.leave"].with_context(test_date_from=new_date).create(
                    {
                        "name": "Test Time Off",
                        "employee_id": self.employee_emp.id,
                        "holiday_status_id": self.leave_type.id,
                        "date_from": new_date,
                        "date_to": new_date + relativedelta(days=7),
                    }
                )
            future_hr_leave_2 = (
                self.env["hr.leave"]
                .with_context(test_date_from=new_date)
                .create(
                    {
                        "name": "Test Time Off",
                        "employee_id": self.employee_emp.id,
                        "holiday_status_id": self.leave_type.id,
                        "date_from": new_date,
                        "date_to": new_date + relativedelta(days=3),
                    }
                )
            )
            future_hr_leave_2.action_approve()
            self.assertEqual(
                future_hr_leave_2.state, "validate", "Time off request is approved"
            )
