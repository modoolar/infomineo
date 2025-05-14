# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class WorkLocation(models.Model):
    _inherit = "hr.work.location"

    country_id = fields.Many2one(comodel_name="res.country")
