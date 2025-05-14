# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    @api.constrains("planned_hours", "sale_line_id")
    def _check_planned_hours_required(self):
        pass
