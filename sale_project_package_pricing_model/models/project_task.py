# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProjectTask(models.Model):
    _inherit = "project.task"

    consumed_points = fields.Float(
        compute="_compute_consumed_points",
        readonly=False,
        tracking=True,
        store=True,
    )
    forecasted_consumed_points = fields.Float(
        compute="_compute_forecasted_consumed_points", store=True
    )

    @api.depends("translated_words", "timesheet_ids.unit_amount", "line_of_business")
    def _compute_consumed_points(self):
        self._calculate_consumed_points(f_name="consumed_points")

    @api.depends("translated_words", "timesheet_ids.unit_amount", "line_of_business")
    def _compute_forecasted_consumed_points(self):
        self._calculate_consumed_points(f_name="forecasted_consumed_points")

    def _calculate_consumed_points(self, f_name):
        cancelled_tasks = self.filtered(lambda x: x.stage_id.is_cancelling)
        cancelled_tasks.update(
            {
                f_name: 0,
            }
        )
        for task in self - cancelled_tasks:
            configuration = task.project_id.package_configuration_id
            configuration_line = configuration.package_configurator_line_ids.filtered(
                lambda x: x.package_line_of_business == task.line_of_business
            )
            if (
                configuration
                and not configuration_line
                and task.line_of_business
                and task.line_of_business != "other"
            ):
                raise ValidationError(
                    _("Missing Configuration for this Line of Business.")
                )
            if configuration_line.reference_uom == "hours":
                # Timesheets may be stored in a different unit of measure, so first
                # we convert all of them to the reference unit
                # if the timesheet has no product_uom_id then we take the one of the project
                consu_points = configuration_line.consumption_ratio * sum(
                    timesheet_line.unit_amount * timesheet_line._get_uom().factor_inv
                    for timesheet_line in task.timesheet_ids.filtered(
                        lambda x: x.so_line
                        and x.so_line == x.task_id.sale_line_id
                        and x.unit_amount
                    )
                )
                # Now convert to the proper unit of measure set in the settings
                task[f_name] = (
                    consu_points * task.project_id.timesheet_encode_uom_id.factor
                )
            elif configuration_line.reference_uom == "words":
                task[f_name] = (
                    configuration_line.consumption_ratio * task.translated_words
                )
