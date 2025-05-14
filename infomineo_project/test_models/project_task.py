# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.constrains("user_ids", "project_id")
    def _check_assignees_required(self):
        pass
