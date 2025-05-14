# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging
import os
from collections import defaultdict
from datetime import datetime, time, timedelta

import pytz

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def _get_default_task_internal_planned_hours(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("infomineo_project_planning.task_internal_planned_hours")
        )

    planned_hours = fields.Float(
        default=lambda x: x._get_default_task_internal_planned_hours()
    )
    is_available_for_assignment = fields.Boolean(
        compute="_compute_task_is_available_for_assignment"
    )

    def _compute_task_is_available_for_assignment(self):
        for task in self:
            task_slot = (
                self.env["planning.slot"]
                .sudo()
                .search(
                    [("task_id", "=", task.id), ("user_id", "in", task.user_ids.ids)]
                )
            )
            if len(task_slot) > 1:
                msg = _(
                    "There are multiple related planning slots for this task - {task_name}."
                )
                raise ValidationError(msg.format(task_name=task.name))

            task.is_available_for_assignment = (
                any(task.user_ids) and task_slot and task_slot.state == "draft"
            )

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)
        self._update_allocated_hours(results)
        results.filtered(
            lambda r: r.project_id and r.project_id.project_plan_capacity
        )._create_planning_slot()
        return results

    def write(self, values):
        self = self.with_context(write_from_task=os.getpid())
        if self._context.get("task_trough_slot_update"):
            return super().write(values)

        for task in self.filtered(
            lambda r: r.project_id and r.project_id.project_plan_capacity
        ):
            published_slots = self.env["planning.slot"].search(
                [("task_id", "=", task.id), ("state", "=", "published")]
            )
            if published_slots and any(
                restrcted_fields in values
                for restrcted_fields in [
                    "user_ids",
                    "planned_date_begin",
                    "planned_date_end",
                ]
            ):
                msg = _(
                    "Task {task_name} update on dist fields is not allowed. "
                    "Related planning slot for this task has already been published."
                )
                raise UserError(msg.format(task_name=task.name))
        ret = super().write(values)
        if (
            not self._context.get("write_from_slot") == os.getpid()
            and "planned_hours" in values
        ):
            self._update_allocated_hours(self)
        return ret

    def _create_planning_slot(self):
        user_tz = pytz.timezone(self.env.user.tz or "UTC")
        today = datetime.now(user_tz).date()

        for task in self:
            allocated_hours = task.planned_hours or 5
            today_start_datetime = user_tz.localize(
                datetime.combine(today, time(hour=8))
            )
            today_end_datetime = today_start_datetime + timedelta(
                hours=float(allocated_hours)
            )
            def_user = task.mapped("user_ids").ids
            def_resource = (
                self.env["resource.resource"]
                .sudo()
                .search([("user_id", "=", def_user[0])])
                if def_user
                else False
            )

            if def_resource:
                working_days = def_resource.calendar_id.attendance_ids
                today_working_hours = working_days.filtered(
                    lambda x: x.dayofweek == str(today.weekday())
                )
                if today_working_hours:
                    morning_shift = today_working_hours.filtered(
                        lambda x: x.day_period == "morning"
                    )
                    today_start_datetime = morning_shift.hour_from
                    hours = int(today_start_datetime)
                    minutes = int((today_start_datetime - hours) * 60)
                    today_start_datetime = user_tz.localize(
                        datetime(today.year, today.month, today.day, hours, minutes)
                    )
                    break_time = self.calculate_break_time(
                        today_working_hours, today_start_datetime, user_tz, today
                    )
                    today_end_datetime = (
                        today_start_datetime
                        + timedelta(hours=float(allocated_hours))
                        + break_time
                    )
            self.env["planning.slot"].sudo().create(
                {
                    "start_datetime": today_start_datetime.astimezone(pytz.utc).replace(
                        tzinfo=None
                    ),
                    "end_datetime": today_end_datetime.astimezone(pytz.utc).replace(
                        tzinfo=None
                    ),
                    "allocated_hours": allocated_hours,
                    "task_id": task.id,
                    "role_id": False,
                    "resource_id": def_resource.id if def_resource else False,
                    "company_id": task.company_id.id
                    if task.company_id
                    else self.env.company.id,
                }
            )

    @staticmethod
    def calculate_break_time(today_working_hours, today_start_datetime, user_tz, today):
        total_break_time = timedelta(minutes=0)
        attendance_periods = today_working_hours.sorted(lambda a: a.hour_from)
        for i, attendance_period in enumerate(attendance_periods):
            if i == 0:
                break_start = today_start_datetime
                break_end = user_tz.localize(
                    datetime(
                        year=today.year,
                        month=today.month,
                        day=today.day,
                        hour=int(attendance_period.hour_from),
                        minute=int((attendance_period.hour_from % 1) * 60),
                    )
                )
            else:
                prev_attendance_period = attendance_periods[i - 1]
                break_start = user_tz.localize(
                    datetime(
                        year=today.year,
                        month=today.month,
                        day=today.day,
                        hour=int(prev_attendance_period.hour_to),
                        minute=int((prev_attendance_period.hour_to % 1) * 60),
                    )
                )
                break_end = user_tz.localize(
                    datetime(
                        year=today.year,
                        month=today.month,
                        day=today.day,
                        hour=int(attendance_period.hour_from),
                        minute=int((attendance_period.hour_from % 1) * 60),
                    )
                )
            break_duration = break_end - break_start
            total_break_time += break_duration
        return total_break_time

    def action_self_assign(self):
        for task in self.filtered(
            lambda r: r.project_id and r.project_id.project_plan_capacity
        ):
            slot = (
                self.env["planning.slot"]
                .sudo()
                .search([("task_id", "=", task.id), ("state", "=", "draft")], limit=1)
            )
            if not slot:
                _logger.debug(
                    "No slot was found " "for {task_name}.".format(task_name=task.name)
                )
                continue

            slot.sudo().action_send()
            staffing_employees_ids = (
                self.env["hr.employee"]
                .sudo()
                .search(
                    [
                        (
                            "user_id.groups_id",
                            "in",
                            self.env.ref(
                                "infomineo_project_planning.group_staffing_manager"
                            ).ids,
                        ),
                        (
                            "department_id",
                            "in",
                            task.mapped("user_ids.employee_ids.department_id").ids,
                        ),
                    ]
                )
            )

            if not staffing_employees_ids:
                _logger.debug(
                    "No Staffing Managers were found"
                    "for {department_names}.".format(
                        department_names=task.mapped(
                            "user_ids.employee_ids.department_id.name"
                        )
                    )
                )
                continue

            # Trigger _compute_employee_id method to remove employee form slot
            # by setting the resource_type to 'material'
            # because we don't need one when sending email only to Stuffing Managers.
            if slot.resource_id.resource_type == "user":
                slot.resource_id.resource_type = "material"
            slot.sudo().with_context(
                send_notification_to_staffing=True, open_shift_available=False
            )._send_slot(staffing_employees_ids, slot.start_datetime, slot.end_datetime)
            slot.resource_id.resource_type = "user"

    def _update_allocated_hours(self, records):
        slots_grouped_by_task = defaultdict(lambda: self.env["planning.slot"])
        for slot in self.env["planning.slot"].search([("task_id", "in", records.ids)]):
            slots_grouped_by_task[slot.task_id] |= slot
        for task_id, slots in slots_grouped_by_task.items():
            slots.write({"allocated_hours": task_id.planned_hours})
