# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    second_sales_person_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('share', '=', False)],",
        related="sale_order_id.second_sales_person_id",
    )
