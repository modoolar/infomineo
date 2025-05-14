# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    is_closed = fields.Boolean(related="stage_id.is_closed")
    is_cancelling = fields.Boolean(related="stage_id.is_cancelling")
