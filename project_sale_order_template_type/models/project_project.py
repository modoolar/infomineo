# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    order_type = fields.Selection(
        string="Sale Order Type", related="sale_order_id.order_type", store=True
    )
