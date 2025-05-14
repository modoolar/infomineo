# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_show_points(self):
        """
        Opens all billable tasks that are related to a particular Sale Order.
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

        billable_tasks = self.sudo().project_ids.task_ids.filtered(
            lambda x: x.consumed_points
        )
        if billable_tasks:
            action["domain"] = [("id", "in", billable_tasks.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}

        return action
