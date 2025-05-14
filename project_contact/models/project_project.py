# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ProjectProject(models.Model):
    _inherit = "project.project"

    contact_id = fields.Many2one(
        comodel_name="res.partner", domain="[('parent_id', '=', partner_id)]"
    )
