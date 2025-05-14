# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from datetime import datetime

from odoo import fields, models


class HRLeaveType(models.Model):
    _inherit = "hr.leave.type"

    def _calculate_additional_days_off_in_advance(
        self, date, employee_id, accrual_hr_leave_type_id
    ):
        allocation_ids = self.env["hr.leave.allocation"].search(
            [
                ("employee_id", "=", employee_id),
                ("holiday_status_id", "=", accrual_hr_leave_type_id),
                ("allocation_type", "=", "accrual"),
                ("accrual_plan_id", "!=", False),
                "|",
                ("date_to", "=", False),
                ("date_to", ">", date),
            ]
        )
        if len(allocation_ids) < 1:
            return 0
        return allocation_ids._process_future_accrual_plans(date)

    def _get_accrual_time_off_ids(self, hr_leave_types):
        return self.env["hr.leave.accrual.plan"].read_group(
            [("time_off_type_id", "in", hr_leave_types)],
            ["time_off_type_id"],
            ["time_off_type_id"],
        )

    def get_employees_days(self, employee_ids, date=None):
        res = super().get_employees_days(employee_ids, date)
        date = (
            fields.Date.to_date(self.env.context.get("default_date_from"))
            if not date
            else date
        ) or fields.Date.context_today(self)
        if date > datetime.now().date():
            for employee_id, hr_leave_types in res.items():
                accruals_read_group = self.sudo()._get_accrual_time_off_ids(
                    list(hr_leave_types.keys())
                )
                accrual_hr_leave_type_ids = [
                    res["time_off_type_id"][0] for res in accruals_read_group
                ]
                for accrual_hr_leave_type_id in accrual_hr_leave_type_ids:
                    res[employee_id][accrual_hr_leave_type_id][
                        "virtual_remaining_leaves"
                    ] += self.sudo()._calculate_additional_days_off_in_advance(
                        date, employee_id, accrual_hr_leave_type_id
                    )
        return res

    def _get_days_request(self):
        self.ensure_one()
        res = super()._get_days_request()
        res[1]["virtual_remaining_leaves"] = (
            ("%.2f" % self.virtual_remaining_leaves).rstrip("0").rstrip(".")
            if self.accrual_count > 0
            else res[1]["virtual_remaining_leaves"]
        )
        return res
