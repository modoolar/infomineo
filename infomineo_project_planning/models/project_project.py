# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _get_default_project_plan_capacity(self):
        return (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("infomineo_project_planning.project_plan_capacity")
        )

    project_plan_capacity = fields.Boolean(
        default=lambda x: x._get_default_project_plan_capacity()
    )
