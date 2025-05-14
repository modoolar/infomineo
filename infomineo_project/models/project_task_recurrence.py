# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import models


class ProjectTaskRecurrence(models.Model):
    _inherit = "project.task.recurrence"

    def _new_task_values(self, task):
        self.ensure_one()
        ret = super(ProjectTaskRecurrence, self)._new_task_values(task)
        if not ret.get("user_ids", False):
            ret["user_ids"] = task.user_ids.ids
        return ret
