# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import datetime

from odoo.addons.hr_holidays.tests.common import TestHrHolidaysCommon


class TestHrHolidaysAccrualsCommon(TestHrHolidaysCommon):
    def setUp(self):
        super(TestHrHolidaysAccrualsCommon, self).setUp()

        self.leave_type = self.env["hr.leave.type"].create(
            {
                "name": "Test Time Off",
                "time_type": "leave",
                "requires_allocation": "yes",
            }
        )

        self.accrual_plan_daily = (
            self.env["hr.leave.accrual.plan"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": "Accrual Plan Daily Test",
                    "time_off_type_id": self.leave_type.id,
                    "level_ids": [
                        (
                            0,
                            0,
                            {
                                "start_count": 0,
                                "start_type": "day",
                                "added_value": 1,
                                "added_value_type": "days",
                                "frequency": "daily",
                                "maximum_leave": 10000,
                            },
                        )
                    ],
                }
            )
        )
        self.accrual_plan_monthly = (
            self.env["hr.leave.accrual.plan"]
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": "Accrual Plan Monthly Test",
                    "time_off_type_id": self.leave_type.id,
                    "level_ids": [
                        (
                            0,
                            0,
                            {
                                "start_count": 0,
                                "start_type": "day",
                                "added_value": 1,
                                "added_value_type": "days",
                                "frequency": "monthly",
                                "maximum_leave": 10000,
                            },
                        )
                    ],
                }
            )
        )
        self.start_date = datetime.date(2024, 6, 27)
        self.allocation = (
            self.env["hr.leave.allocation"]
            .with_user(self.user_hrmanager_id)
            .with_context(tracking_disable=True)
            .create(
                {
                    "name": "Accrual allocation for employee",
                    "accrual_plan_id": self.accrual_plan_daily.id,
                    "employee_id": self.employee_emp.id,
                    "holiday_status_id": self.leave_type.id,
                    "number_of_days": 1,
                    "allocation_type": "accrual",
                    "date_from": self.start_date - datetime.timedelta(days=1),
                    "nextcall": self.start_date,
                }
            )
        )
