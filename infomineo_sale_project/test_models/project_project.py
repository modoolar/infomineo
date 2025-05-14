# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    @api.model
    def _set_project_auto_name(self, vals):
        pass
