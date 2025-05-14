# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectTaskType(models.Model):
    _inherit = "project.task.type"

    is_new = fields.Boolean()
