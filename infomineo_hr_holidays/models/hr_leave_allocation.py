# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from collections import defaultdict
from datetime import timedelta

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools.date_utils import get_timedelta

from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    is_automated_leave_allocation = fields.Boolean(readonly=True, default=False)
    number_of_days_in_first_period = fields.Float(default=0.0)

    @staticmethod
    def _prepare_default_creation_values():
        return {
            "active": True,
            "notes": False,
            "parent_id": False,
            "holiday_type": "employee",
            "mode_company_id": False,
            "category_id": False,
            "overtime_id": False,
        }

    def _set_dates(self, employee):
        self.ensure_one()
        date_from = employee.first_contract_date
        if not date_from:
            return
        if self.allocation_type == "regular":
            self.date_from = date_from
            return
        if employee.first_contract_date.day == 1:
            date_from = (
                employee.first_contract_date - relativedelta(months=1)
            ).replace(day=28)
        self.date_from = date_from - timedelta(days=1)
        self.nextcall = date_from
        self.lastcall = date_from

    def _set_number_of_days_in_first_period(self):
        for allocation in self:
            allocation.number_of_days_in_first_period = allocation.number_of_days

    def _check_first_call(self, level):
        return (
            self.is_automated_leave_allocation
            and level.accrual_plan_id.is_automated_leave_accrual_plan
            and self.env.context.get("first_call")
        )

    def _check_first_period(self, level):
        date_from = fields.Date.to_date(self.env.context.get("default_date_from"))
        if not date_from:
            return False
        level_start_date = self.date_from + get_timedelta(
            level.start_count, level.start_type
        )
        level_first_period_begin_date = level._get_next_date(level_start_date)
        level_second_period_begin_date = level._get_next_date(
            level_first_period_begin_date
        )
        return (
            self.is_automated_leave_allocation
            and level.accrual_plan_id.is_automated_leave_accrual_plan
            and level_second_period_begin_date
            > date_from
            > level_first_period_begin_date
        )

    def _process_accrual_plan_level(
        self, level, start_period, start_date, end_period, end_date
    ):
        """
        For the first time calling this method, end_date should be equal
        to level._get_next_date(allocation.lastcall), which is set as
        end_period
        """
        is_first_call = self._check_first_call(level)
        if is_first_call:
            end_date = end_period
        return super()._process_accrual_plan_level(
            level, start_period, start_date, end_period, end_date
        )

    def _process_automated_accrual_plan_level(self):
        """
        This method is based on the original Odoo's `_process_accrual_plans`.

        The goal of this method is to avoid calculating days for automated level_ids
        which are in the first accrual period, because the number of days, which
        was planned to be added on first cron call, has already added at the
        creation of automated allocation
        """
        today = fields.Date.today()
        first_allocation = _(
            """
            This allocation have already ran once, any modification won't
            be effective to the days allocated to the employee. If you need
            to change the configuration of the allocation, cancel and create
            a new one.
            """
        )
        for allocation in self:

            level_ids = self.accrual_plan_id.level_ids.sorted("sequence")
            if not level_ids:
                continue
            if not allocation.nextcall:
                first_level = level_ids[0]
                # This line hase changed
                first_level_start_date = (
                    allocation.date_from + first_level._get_addition_value_for_level()
                )
                if today < first_level_start_date:
                    # Accrual plan is not configured properly or has not started
                    continue
                allocation.lastcall = max(allocation.lastcall, first_level_start_date)
                allocation.nextcall = first_level._get_next_date(allocation.lastcall)
                if len(level_ids) > 1:
                    # This line has changed
                    second_level_start_date = (
                        allocation.date_from
                        + level_ids[1]._get_addition_value_for_level()
                    )
                    allocation.nextcall = min(
                        second_level_start_date, allocation.nextcall
                    )
                allocation._message_log(body=first_allocation)
            days_added_per_level = defaultdict(lambda: 0)
            while allocation.nextcall <= today:
                (
                    current_level,
                    current_level_idx,
                ) = allocation._get_current_accrual_plan_level_id(allocation.nextcall)
                current_level_maximum_leave = (
                    current_level.maximum_leave
                    if current_level.added_value_type == "days"
                    else current_level.maximum_leave
                    / (
                        allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day
                        or HOURS_PER_DAY
                    )
                )
                nextcall = current_level._get_next_date(allocation.nextcall)
                # Since _get_previous_date returns the given date if it corresponds
                # to a call date
                # this will always return lastcall except possibly on the first call
                # this is used to prorate the first number of days given to the employee
                period_start = current_level._get_previous_date(allocation.lastcall)
                period_end = current_level._get_next_date(allocation.lastcall)
                # Also prorate this accrual in the event that we are passing from
                # one level to another
                if (
                    current_level_idx < (len(level_ids) - 1)
                    and allocation.accrual_plan_id.transition_mode == "immediately"
                ):
                    next_level = level_ids[current_level_idx + 1]
                    # This line has changed
                    current_level_last_date = (
                        allocation.date_from
                        + next_level._get_addition_value_for_level()
                    )
                    if allocation.nextcall != current_level_last_date:
                        nextcall = min(nextcall, current_level_last_date)
                days_added_per_level[
                    current_level
                ] += allocation._process_accrual_plan_level(
                    current_level,
                    period_start,
                    allocation.lastcall,
                    period_end,
                    allocation.nextcall,
                )
                if (
                    current_level_maximum_leave > 0
                    and sum(days_added_per_level.values()) > current_level_maximum_leave
                ):
                    days_added_per_level[current_level] -= (
                        sum(days_added_per_level.values()) - current_level_maximum_leave
                    )
                allocation.lastcall = allocation.nextcall
                allocation.nextcall = nextcall
            if days_added_per_level:
                number_of_days_to_add = allocation.number_of_days + sum(
                    days_added_per_level.values()
                )
                max_allocation_days = current_level_maximum_leave + (
                    allocation.leaves_taken
                    if allocation.type_request_unit != "hour"
                    else allocation.leaves_taken
                    / (
                        allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day
                        or HOURS_PER_DAY
                    )
                )
                self._context.get("first_call")
                set_to_zero = allocation.date_from.day == 27 and self._context.get(
                    "first_call"
                )
                # Let's assume the limit of the last level is the correct one
                if set_to_zero:
                    allocation.number_of_days = 0.0
                else:
                    if current_level_maximum_leave > 0:
                        allocation.number_of_days = min(
                            number_of_days_to_add, max_allocation_days
                        )
                    else:
                        allocation.number_of_days = number_of_days_to_add

    @api.model_create_multi
    def create(self, vals_list):
        for values in vals_list:
            if values.get("is_automated_leave_allocation", False):
                values.update(self._prepare_default_creation_values())
        return super().create(vals_list)
