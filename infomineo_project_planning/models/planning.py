# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import os
from datetime import timedelta

from pytz import UTC, utc

from odoo import api, fields, models
from odoo.osv import expression


class PlanningSlot(models.Model):
    _inherit = "planning.slot"
    _check_company_auto = False

    resource_id = fields.Many2one(domain=False)
    department_id = fields.Many2one(group_expand="_read_group_department_id")
    hr_team_id = fields.Many2one(
        related="resource_id.employee_id.hr_team_id", store=True
    )
    allocated_hours = fields.Float(string="Allocated Working Hours")
    project_hr_team_id = fields.Many2one(related="project_id.hr_team_id", store=True)
    category_ids = fields.Many2many(
        compute="_compute_category_ids",
        comodel_name="hr.employee.category",
        string="Tags",
        store=True,
    )
    job_title = fields.Char(store=True)
    user_slot_ids = fields.Boolean(store=False, search="_search_user_slot_ids")

    @api.model
    def _search_user_slot_ids(self, operator, value):
        my_team_slot_ids = self.search(
            [
                "|",
                ("hr_team_id", "=", self.env.user.employee_id.hr_team_id.id),
                ("user_id", "=", self.env.user.id),
            ]
        ).ids
        return [("id", "in", my_team_slot_ids)]

    def write(self, values):
        self = self.with_context(write_from_slot=os.getpid())
        result = super(PlanningSlot, self).write(values)

        for slot in self.filtered(
            lambda s: s.task_id
            and s.task_id.project_id
            and s.task_id.project_id.project_plan_capacity
            and s.resource_id
            and s.resource_id.resource_type == "user"
            and s.user_id
        ):
            if slot.user_id.id not in slot.task_id.sudo().user_ids.ids:
                slot.with_context(
                    task_trough_slot_update=True
                ).task_id.sudo().user_ids = [(4, slot.user_id.id)]
                slot.task_id._task_message_auto_subscribe_notify(
                    {slot.task_id: slot.task_id.sudo().user_ids - self.env.user}
                )

            if slot.start_datetime != slot.task_id.planned_date_begin:
                slot.with_context(
                    task_trough_slot_update=True
                ).task_id.planned_date_begin = slot.start_datetime

            if slot.end_datetime != slot.task_id.planned_date_end:
                slot.with_context(
                    task_trough_slot_update=True
                ).task_id.planned_date_end = slot.end_datetime
        if (
            not self._context.get("write_from_task") == os.getpid()
            and "allocated_hours" in values
        ):
            for rec in self:
                rec.task_id.write({"planned_hours": rec.allocated_hours})
        return result

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        if (
            not self.env["ir.config_parameter"]
            .sudo()
            .get_param("infomineo_project_planning.project_plan_capacity")
        ):
            return super().read_group(
                domain,
                fields,
                groupby,
                offset=offset,
                limit=limit,
                orderby=orderby,
                lazy=lazy,
            )

        self_with_planning_expand = self
        if (
            len(groupby) <= 1
        ):  # feature should work only for the first level of group by
            self_with_planning_expand = self
            if "resource_id" in groupby and lazy:
                self_with_planning_expand = self.with_context(
                    planning_expand_resource=True
                )

                dom = []
                if len(domain) > 2:
                    dom = self._prepare_resource_domain(domain)

                slot_res = (
                    self.env["planning.slot"].search(domain).mapped("resource_id")
                )
                res_res = self.env["resource.resource"].search(dom)
                domain = expression.AND(
                    [
                        domain,
                        [["resource_id", "in", list(set(res_res.ids + slot_res.ids))]],
                    ]
                )
            elif "role_id" in groupby and lazy:
                self_with_planning_expand = self.with_context(planning_expand_role=True)
                domain = expression.AND(
                    [
                        domain,
                        [
                            [
                                "role_id",
                                "in",
                                self.env["planning.role"].sudo().search([]).ids,
                            ]
                        ],
                    ]
                )
            elif "department_id" in groupby and lazy:
                self_with_planning_expand = self.with_context(
                    planning_expand_department=True
                )
                domain = expression.AND(
                    [
                        domain,
                        [
                            [
                                "department_id",
                                "in",
                                self.env["hr.department"].search([]).ids,
                            ]
                        ],
                    ]
                )

        if self.env.user.has_group("infomineo_project_planning.group_staffing_manager"):
            self_with_planning_expand = self_with_planning_expand.sudo()

        return super(PlanningSlot, self_with_planning_expand).read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )

    def _prepare_resource_domain(self, domain):
        def has_domain_field(field_name, domain_list):
            """Check if domain contains a specific field."""
            return any([d[0] == field_name for d in domain_list if isinstance(d, list)])

        def get_field_domain(field_name, domain_list):
            """Get domain entries for a specific field."""
            return [
                d.copy()
                for d in domain_list
                if isinstance(d, list) and d[0] == field_name
            ]

        def map_field_name(domain_entries, new_field):
            """Map old field name to new field name in domain entries."""
            for entry in domain_entries:
                entry[0] = new_field
            return domain_entries

        def handle_user_id_domain(domain_list):
            """Handle special case for user_id domain."""
            user_domain = get_field_domain("user_id", domain_list)
            for entry in user_domain:
                entry[2] = self.env.uid
            return user_domain

        def handle_user_slot_domain():
            """Handle special case for user_slot_ids domain."""
            return [
                "|",
                (
                    "employee_id.hr_team_id",
                    "=",
                    self.env.user.employee_id.hr_team_id.id,
                ),
                ("employee_id.user_id", "=", self.env.user.id),
            ]

        field_mappings = {
            "resource_id": "id",
            "role_id": "employee_id.default_planning_role_id.name",
            "department_id": "employee_id.department_id.name",
            "employee_skill_ids": "employee_id.employee_skill_ids.skill_id.name",
            "employee_skill_ids.skill_id": "employee_id.employee_skill_ids.skill_id",
            "manager_id.user_id": "employee_id.parent_id.user_id",
            "hr_team_id": "employee_id.hr_team_id",
        }

        dom = []

        # Handle standard field mappings
        for old_field, new_field in field_mappings.items():
            if has_domain_field(old_field, domain):
                field_domain = get_field_domain(old_field, domain)
                mapped_domain = map_field_name(field_domain, new_field)
                dom = expression.AND([dom, mapped_domain]) if dom else mapped_domain

        # Handle special case for user_id
        if has_domain_field("user_id", domain):
            user_domain = handle_user_id_domain(domain)
            dom = expression.AND([dom, user_domain]) if dom else user_domain

        # Handle special case for user_slot_ids
        if has_domain_field("user_slot_ids", domain):
            slot_domain = handle_user_slot_domain()
            dom = expression.AND([dom, slot_domain]) if dom else slot_domain

        return dom

    @api.model
    def search_read(
        self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
    ):
        if not self._context.get("show_my_shifts", False) and not self._context.get(
            "my_hr_team_shifts", False
        ):
            domain = expression.OR([domain, [["resource_id", "=", False]]])
        return super().search_read(
            domain=domain,
            fields=fields,
            offset=offset,
            limit=limit,
            order=order,
            **read_kwargs
        )

    def _read_group_resource_id(self, resources, domain, order):
        resources = super()._read_group_resource_id(resources, domain, order)

        dom_tuples = [
            (dom[0], dom[1])
            for dom in domain
            if (isinstance(dom, list) or isinstance(dom, tuple)) and len(dom) == 3
        ]
        if (
            self._context.get("planning_expand_resource")
            and ("start_datetime", "<=") in dom_tuples
            and ("end_datetime", ">=") in dom_tuples
            and ("resource_id", "in") in dom_tuples
        ):
            filter_domain = self._expand_domain_m2o_groupby(domain, "resource_id")
            filter_domain.append(("company_id", "in", self.env.companies.ids))
            return self.env["resource.resource"].search(filter_domain, order=order)

        return resources

    def _read_group_role_id(self, roles, domain, order):
        result = super()._read_group_role_id(roles, domain, order)

        dom_tuples = [
            (dom[0], dom[1])
            for dom in domain
            if (isinstance(dom, list) or isinstance(dom, tuple)) and len(dom) == 3
        ]
        if (
            self._context.get("planning_expand_role")
            and ("start_datetime", "<=") in dom_tuples
            and ("end_datetime", ">=") in dom_tuples
            and ("role_id", "in") in dom_tuples
        ):
            filter_domain = self._expand_domain_m2o_groupby(domain, "role_id")
            return self.env["planning.role"].search(filter_domain, order=order)

        return result

    def _read_group_department_id(self, departments, domain, order):
        dom_tuples = [
            (dom[0], dom[1])
            for dom in domain
            if (isinstance(dom, list) or isinstance(dom, tuple)) and len(dom) == 3
        ]
        if ("start_datetime", "<=") in dom_tuples and (
            "end_datetime",
            ">=",
        ) in dom_tuples:
            if (
                self._context.get("planning_expand_department")
                and ("department_id", "=") in dom_tuples
                or ("department_id", "ilike") in dom_tuples
                or ("department_id", "in") in dom_tuples
            ):
                filter_domain = self._expand_domain_m2o_groupby(domain, "department_id")
                return self.env["hr.department"].search(filter_domain, order=order)
            filters = expression.AND(
                [
                    [("department_id.active", "=", True)],
                    self._expand_domain_dates(domain),
                ]
            )
            return self.env["planning.slot"].search(filters).mapped("department_id")
        return departments

    @api.model
    def _expand_domain_m2o_groupby(self, domain, filter_field=False):
        filter_domain = []
        for dom in domain:
            if dom[0] == filter_field:
                field = self._fields[dom[0]]
                if field.type == "many2one" and len(dom) == 3:
                    if dom[1] in ["=", "in"]:
                        filter_domain = expression.OR(
                            [filter_domain, [("id", dom[1], dom[2])]]
                        )
                    elif dom[1] == "ilike":
                        rec_name = self.env[field.comodel_name]._rec_name
                        filter_domain = expression.OR(
                            [filter_domain, [(rec_name, dom[1], dom[2])]]
                        )
        return filter_domain

    def _get_slot_duration(self):
        """
        Override of the odoo native method.
        """
        self.ensure_one()
        if not self.start_datetime:
            return False

        left_boundary_datetime = utc.localize(self.start_datetime)
        right_boundary_datetime = utc.localize(self.end_datetime)
        work_intervals_per_resource = self.sudo().resource_id._get_work_intervals_batch(
            left_boundary_datetime, right_boundary_datetime
        )
        work_intervals = work_intervals_per_resource[self.resource_id.id]

        if not bool(work_intervals):
            return (self.end_datetime - self.start_datetime).total_seconds() / 3600.0

        interval_hours = 0.0
        for start, stop, _resource in work_intervals:
            int_hours = ((stop - start).total_seconds() / 3600) % 24
            interval_hours += int_hours

        return interval_hours

    @api.onchange("allocated_hours")
    def _onchange_allocated_hours(self):
        for rec in self:
            left_boundary_datetime = utc.localize(rec.start_datetime)
            right_boundary_datetime = utc.localize(
                rec.start_datetime + timedelta(days=31)
            )
            work_intervals_per_resource = (
                rec.resource_id.sudo()._get_work_intervals_batch(
                    left_boundary_datetime, right_boundary_datetime
                )
            )
            work_intervals = work_intervals_per_resource[rec.resource_id.id]

            interval_hours = 0.0
            hours_so_far = 0.0
            start = left_boundary_datetime
            for start, stop, _resource in work_intervals:
                int_hours = ((stop - start).total_seconds() / 3600) % 24
                interval_hours += int_hours
                if rec.allocated_hours <= interval_hours:
                    break
                hours_so_far += int_hours

            end_datetime = start + timedelta(hours=rec.allocated_hours - hours_so_far)
            rec.end_datetime = end_datetime.astimezone(UTC).replace(tzinfo=None)

    def _compute_allocated_hours(self):
        if not self.env.all.towrite.get(self._name):
            super()._compute_allocated_hours()
            return

        new_ids = self.filtered(lambda x: isinstance(x.id, models.NewId))

        if new_ids:
            super(PlanningSlot, new_ids)._compute_allocated_hours()

        end_date_to_write_recs = other_recs = self.env["planning.slot"]

        for rec in self - new_ids:
            rec_towite = self.env.all.towrite.get(self._name).get(rec.id)
            if rec_towite and "end_datetime" in rec_towite:
                end_date_to_write_recs |= rec
            else:
                other_recs |= rec

        super(PlanningSlot, other_recs)._compute_allocated_hours()

        for rec in end_date_to_write_recs:
            percentage_field = self._fields["allocated_percentage"]
            self.env.remove_to_compute(percentage_field, self)
            left_boundary_datetime = utc.localize(rec.start_datetime)
            right_boundary_datetime = utc.localize(
                rec.start_datetime + timedelta(days=31)
            )
            work_intervals_per_resource = (
                rec.resource_id.sudo()._get_work_intervals_batch(
                    left_boundary_datetime, right_boundary_datetime
                )
            )
            work_intervals = work_intervals_per_resource[rec.resource_id.id]

            interval_hours = 0.0
            hours_so_far = 0.0
            start = left_boundary_datetime
            for start, stop, _resource in work_intervals:
                int_hours = ((stop - start).total_seconds() / 3600) % 24
                interval_hours += int_hours
                if rec.allocated_hours <= interval_hours:
                    break
                hours_so_far += int_hours

            end_datetime = start + timedelta(hours=rec.allocated_hours - hours_so_far)
            rec.end_datetime = end_datetime.astimezone(UTC).replace(tzinfo=None)

    def action_unpublish(self):
        """
        We need to allow staffing manager to
        set planning.slot to draft state, since has_group()
        does not care for sudo() we need to add then remove admin
        group from staffing manager.
        """
        if self.env.user.has_group("infomineo_project_planning.group_staffing_manager"):
            planning_group_name = "planning.group_planning_manager"
            planning_group = self.env.ref(planning_group_name)
            if not self.env.user.has_group(planning_group_name):
                self.env.user.groups_id += planning_group
                ret = super().action_unpublish()
                self.env.user.groups_id -= planning_group
                return ret
        return super().action_unpublish()

    @api.depends("employee_id.category_ids")
    def _compute_category_ids(self):
        for r in self:
            r.category_ids = r.employee_id.category_ids.ids

    @api.model_create_multi
    def create(self, vals_list):
        results = super().create(vals_list)
        for rec in results:
            rec.task_id.write({"planned_hours": rec.allocated_hours})
        return results
