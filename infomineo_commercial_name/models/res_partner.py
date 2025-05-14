# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    commercial_name_id = fields.Many2one("partner.commercial.name")
