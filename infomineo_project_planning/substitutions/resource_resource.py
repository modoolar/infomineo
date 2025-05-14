# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from collections import defaultdict
from datetime import datetime

import pytz

from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT

from odoo.addons.planning.models.resource_resource import (
    ResourceResource as originalResourceResource,
)
from odoo.addons.resource.models.resource import Intervals


def get_planning_hours_info(self, date_start_str, date_stop_str):
    """Override of the original odoo method"""
    date_start = datetime.strptime(date_start_str, DEFAULT_SERVER_DATETIME_FORMAT)
    date_stop = datetime.strptime(date_stop_str, DEFAULT_SERVER_DATETIME_FORMAT)
    planning_slots = self.env["planning.slot"].search(
        [
            ("resource_id", "in", self.ids),
            ("start_datetime", "<=", date_stop),
            ("end_datetime", ">=", date_start),
        ]
    )
    planned_hours_mapped = defaultdict(float)
    start_utc = pytz.utc.localize(date_start)
    stop_utc = pytz.utc.localize(date_stop)
    work_intervals_batch = self.sudo()._get_work_intervals_batch(start_utc, stop_utc)
    for slot in planning_slots:
        if slot.start_datetime >= date_start and slot.end_datetime <= date_stop:
            planned_hours_mapped[slot.resource_id.id] += slot.allocated_hours
        else:
            # if the slot goes over the gantt period, compute the duration only within
            # the gantt period
            ratio = slot.allocated_percentage / 100.0 or 1
            start = max(start_utc, pytz.utc.localize(slot.start_datetime))
            end = min(stop_utc, pytz.utc.localize(slot.end_datetime))

            # REMOVED STUFF
            # if slot.allocation_type == 'planning':
            #     planned_hours_mapped[slot.resource_id.id] +=
            #       (end - start).total_seconds() / 3600
            # else:
            #   for forecast slots, use the conjonction between work intervals and slot.

            interval = Intervals(
                [(start, end, self.env["resource.calendar.attendance"])]
            )
            work_intervals = interval & work_intervals_batch[slot.resource_id.id]
            planned_hours_mapped[slot.resource_id.id] += (
                sum(
                    (stop - start).total_seconds() / 3600
                    for start, stop, _resource in work_intervals
                )
                * ratio
            )
    # Compute employee work hours based on its work intervals.
    work_hours = {
        resource_id: sum(
            (stop - start).total_seconds() / 3600
            for start, stop, _resource in work_intervals
        )
        for resource_id, work_intervals in work_intervals_batch.items()
    }
    return {
        resource.id: {
            "planned_hours": planned_hours_mapped[resource.id],
            "work_hours": work_hours.get(resource.id, 0.0),
            "employee_id": resource.with_context(active_test=False).employee_id.id,
        }
        for resource in self
    }


def patch_account_move_line_methods():
    originalResourceResource._patch_method(
        "get_planning_hours_info", get_planning_hours_info
    )
