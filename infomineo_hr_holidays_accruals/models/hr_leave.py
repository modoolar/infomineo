# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _add_skip_days_context(self):
        return self.with_context(skip_check_number_of_days=True)

    def _get_future_virtual_remaining_leaves(self, date_from):
        return self.holiday_status_id.get_employees_days(
            [self.employee_id.id], fields.Date.to_date(date_from)
        )[self.employee_id.id][self.holiday_status_id.id]["virtual_remaining_leaves"]

    def _check_number_of_days(self, values):
        """
        This method returns True if:
        1) requested number of days is less than old number of days or
        2) if their difference is less than the employee's
        virtual_remaining_leaves for chosen date from in the future.
        """
        new_number_of_days = values.get("number_of_days", 0)
        date_from = values.get("request_date_from", False) or self.date_from
        future_virtual_remaining_leaves = self._get_future_virtual_remaining_leaves(
            date_from
        )
        return new_number_of_days < self.number_of_days or (
            new_number_of_days > 0
            and new_number_of_days - self.number_of_days
            < future_virtual_remaining_leaves
        )

    @api.constrains("state", "number_of_days", "holiday_status_id")
    def _check_holidays(self):

        if self.env.context.get("skip_check_number_of_days", False):
            if all(leave.holiday_status_id.accrual_count > 0 for leave in self):
                return
            else:
                accrual_hr_leave_ids = self.filtered(
                    lambda leave: leave.holiday_status_id.accrual_count > 0
                )
                return super(
                    HolidaysRequest, self - accrual_hr_leave_ids
                )._check_holidays()
        super(HolidaysRequest, self)._check_holidays()

    def action_approve(self):
        self = self._add_skip_days_context()
        return super().action_approve()

    def action_validate(self):
        self = self._add_skip_days_context()
        return super().action_validate()

    def action_refuse(self):
        self = self._add_skip_days_context()
        return super().action_refuse()

    def action_draft(self):
        self = self._add_skip_days_context()
        return super().action_draft()

    def write(self, values):
        if values.get("request_date_from", False) or values.get(
            "request_date_to", False
        ):
            number_of_days_is_valid = self._check_number_of_days(values)
            if number_of_days_is_valid:
                self = self._add_skip_days_context()
        return super().write(values)
