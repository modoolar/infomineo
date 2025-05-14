# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    consumed_points = fields.Float(compute="_compute_consumed_points", store=True)

    @api.depends(
        "project_id.task_ids.translated_words",
        "project_id.task_ids.consumed_points",
        "project_id.task_ids.line_of_business",
        "analytic_line_ids.unit_amount",
        "project_id",
    )
    def _compute_consumed_points(self):
        tasks_read_group = self.env["project.task"].read_group(
            [("sale_line_id", "in", self.ids), ("consumed_points", ">", 0.0)],
            ["sale_line_id", "consumed_points"],
            ["sale_line_id"],
            lazy=False,
        )

        mapping = {
            item["sale_line_id"][0]: float(item["consumed_points"])
            for item in tasks_read_group
        }

        for sol in self:
            sol.consumed_points = mapping.get(sol.id, 0)
