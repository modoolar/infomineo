# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    project_plan_capacity = fields.Boolean(
        default=True,
        config_parameter="infomineo_project_planning.project_plan_capacity",
    )
    task_internal_planned_hours = fields.Float(
        default=5.0,
        config_parameter="infomineo_project_planning.task_internal_planned_hours",
    )
