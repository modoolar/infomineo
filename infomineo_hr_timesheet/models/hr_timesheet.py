# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.osv import expression


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    task_id = fields.Many2one(
        domain="[('project_id.allow_timesheets', '=', True), ('project_id', '=?', project_id)]"
    )
    hr_team_id = fields.Many2one(related="employee_id.hr_team_id", store=True)
    hr_child_team_id = fields.Many2one(
        related="employee_id.hr_child_team_id", store=True
    )
    words_count = fields.Integer()

    def _domain_project_id(self):
        res = super()._domain_project_id()

        domain = [("allow_timesheets", "=", True)]
        if not self.user_has_groups("hr_timesheet.group_timesheet_manager"):
            return expression.OR(
                [
                    res,
                    expression.AND(
                        [
                            domain,
                            [
                                "|",
                                "|",
                                "|",
                                ("user_id", "=", self.env.user.id),
                                ("project_director_id", "=", self.env.user.id),
                                (
                                    "other_project_managers_ids",
                                    "in",
                                    [self.env.user.id],
                                ),
                                ("project_users_ids", "in", [self.env.user.id]),
                            ],
                        ]
                    ),
                ]
            )

        return domain

    project_id = fields.Many2one(domain=_domain_project_id)

    def _check_task_state(self, tasks):
        if tasks and any(tasks.filtered(lambda x: x.stage_id.is_new)):
            self._raise_task_state_error()

    @api.model
    def create(self, vals):
        task_id = vals.get("task_id")
        if task_id:
            self._check_task_state(self.env["project.task"].browse(task_id))
        return super().create(vals)

    def write(self, vals):
        self._check_task_state(self.mapped("task_id"))
        return super().write(vals)

    def _raise_task_state_error(self):
        raise UserError(
            _(
                "You cannot create or modify timesheet lines "
                "for a task that is in the 'New' state."
            )
        )
