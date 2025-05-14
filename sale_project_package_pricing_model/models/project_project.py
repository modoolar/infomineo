# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    package_configuration_id = fields.Many2one(
        related="sale_order_id.sale_order_template_id.package_configuration_id",
        store=True,
    )
    package_expiry_datetime = fields.Datetime(
        related="sale_order_id.package_expiry_datetime", store=True
    )
    package_size = fields.Integer(
        related="sale_order_id.sale_order_template_id.package_size", store=True
    )
    consumed_points_count = fields.Float(compute="_compute_consumed_points_count")

    @api.depends("timesheet_ids")
    def _compute_consumed_points_count(self):
        tasks_read_group = self.env["project.task"].read_group(
            [("project_id", "in", self.ids), ("consumed_points", ">", 0.0)],
            ["project_id", "consumed_points"],
            ["project_id"],
            lazy=False,
        )

        mapping = {
            item["project_id"][0]: float(item["consumed_points"])
            for item in tasks_read_group
        }

        for project in self:
            project.consumed_points_count = mapping.get(project.id, 0)

    def action_show_points(self):
        """
        Opens all billable tasks that are related to a particular Project.
        """
        self.ensure_one()

        action = self.env["ir.actions.act_window"]._for_xml_id(
            "project.act_project_project_2_project_task_all"
        )

        action["views"] = [
            (
                self.env.ref(
                    "sale_project_package_pricing_model.project_task_consumed_points_tree_view"
                ).id,
                "tree",
            )
        ]

        billable_tasks = self.task_ids.filtered(lambda x: x.consumed_points)
        if billable_tasks:
            action["domain"] = [("id", "in", billable_tasks.ids)]

            action["context"] = dict(
                self.env.context,
                active_id=self.id,
                active_ids=self.ids,
            )
        else:
            action = {"type": "ir.actions.act_window_close"}

        return action
