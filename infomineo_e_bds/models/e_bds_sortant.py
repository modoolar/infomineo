# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class EBDSSortant(models.Model):
    _name = "e_bds.sortant"
    _inherit = ["mail.thread"]

    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    e_bds_sortant_line_ids = fields.One2many(
        "e_bds.sortant.line", "e_bds_sortant_id", string="e_bds_sortant_line"
    )
