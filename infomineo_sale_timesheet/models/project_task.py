# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.model
    def message_new(self, msg, custom_values=None):
        self_without_check = self.with_context(email_created=True)
        return super(ProjectTask, self_without_check).message_new(
            msg, custom_values=custom_values
        )

    @api.constrains("planned_hours", "sale_line_id")
    def _check_planned_hours_required(self):
        internal_project_type = self.env.ref(
            "hr_timesheet.internal_project_default_stage"
        )
        for task in self:
            if "email_created" not in self._context:
                if (
                    not task.planned_hours
                    and not task.sale_line_id.product_id.service_policy
                    == "delivered_timesheet"
                    and internal_project_type not in task.project_id.type_ids
                    and task.project_id.project_type
                    not in ("internal", "internal_strategic")
                ):
                    raise UserError(_("Please set Internal planned hours"))
