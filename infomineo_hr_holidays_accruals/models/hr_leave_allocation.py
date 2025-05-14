# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from collections import defaultdict

from odoo import models

from odoo.addons.resource.models.resource import HOURS_PER_DAY


class HolidaysAllocation(models.Model):
    _inherit = "hr.leave.allocation"

    def _process_future_accrual_plans(self, date):
        """
        This method is based on the original Odoo's `_process_accrual_plans`.

        The goal of this method is to calculate the number of days
        that will be added to the employee's virtual_remaining_leaves
        based on the accrual plan and selected date (the date parameter).
        """

        # This line is changed. We will use this dictionary to keep track
        # of the number of days that will be added to the employee's
        # virtual_remaining_leaves as sum of days added for each allocation.
        number_of_days_to_add = defaultdict(lambda: 0)
        for allocation in self:
            level_ids = allocation.accrual_plan_id.level_ids.sorted("sequence")
            if not level_ids:
                continue

            # In the original method, the allocation is changed, but now
            # we don't want to change the original values, so we will use
            # these variables `allocation_nextcall`, `allocation_lastcall`,
            # `current_level_maximum_leave` to keep track of the current
            # state of the allocation.
            allocation_nextcall = allocation.nextcall
            allocation_lastcall = allocation.lastcall
            current_level_maximum_leave = 0
            if not allocation_nextcall:
                first_level = level_ids[0]
                # This line has changed, added _get_addition_value_for_level
                first_level_start_date = (
                    allocation.date_from + first_level._get_addition_value_for_level()
                )
                # This line has changed, we are now using the date parameter,
                # instead of the today's date in the original method.
                # Whole logic of this method is based on the date parameter.
                if date < first_level_start_date:
                    # Acrual plan has not started yet
                    continue
                allocation_lastcall = max(allocation.lastcall, first_level_start_date)
                allocation_nextcall = first_level._get_next_date(allocation_lastcall)
                if len(level_ids) > 1:
                    # This line has changed, added _get_addition_value_for_level
                    second_level_start_date = (
                        allocation.date_from
                        + level_ids[1]._get_addition_value_for_level()
                    )
                    allocation_nextcall = min(
                        second_level_start_date, allocation_nextcall
                    )
            days_added_per_level = defaultdict(lambda: 0)
            while allocation_nextcall <= date:
                (
                    current_level,
                    current_level_idx,
                ) = allocation._get_current_accrual_plan_level_id(allocation_nextcall)
                current_level_maximum_leave = (
                    current_level.maximum_leave
                    if current_level.added_value_type == "days"
                    else current_level.maximum_leave
                    / (
                        allocation.employee_id.sudo().resource_id.calendar_id.hours_per_day
                        or HOURS_PER_DAY
                    )
                )
                nextcall = current_level._get_next_date(allocation_nextcall)
                period_start = current_level._get_previous_date(allocation_lastcall)
                period_end = current_level._get_next_date(allocation_lastcall)
                if (
                    current_level_idx < (len(level_ids) - 1)
                    and allocation.accrual_plan_id.transition_mode == "immediately"
                ):
                    next_level = level_ids[current_level_idx + 1]
                    # This line has changed, added _get_addition_value_for_level
                    current_level_last_date = (
                        allocation.date_from
                        + next_level._get_addition_value_for_level()
                    )
                    if allocation_nextcall != current_level_last_date:
                        nextcall = min(nextcall, current_level_last_date)
                days_added_per_level[
                    current_level
                ] += allocation._process_accrual_plan_level(
                    current_level,
                    period_start,
                    allocation_lastcall,
                    period_end,
                    allocation_nextcall,
                )
                if (
                    current_level_maximum_leave > 0
                    and sum(days_added_per_level.values()) > current_level_maximum_leave
                ):
                    days_added_per_level[current_level] -= (
                        sum(days_added_per_level.values()) - current_level_maximum_leave
                    )
                allocation_lastcall = allocation_nextcall
                allocation_nextcall = nextcall
            # Return value is changed. We are now returning the sum of days
            # added for each allocation. This is the number of days that will be
            # added to the employee's virtual_remaining_leaves.
            if days_added_per_level:
                number_of_days_to_add[allocation.id] = sum(
                    days_added_per_level.values()
                )
        return sum(number_of_days_to_add.values())
