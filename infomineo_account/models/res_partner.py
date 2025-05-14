# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    remove_withholding_tax = fields.Boolean(
        help="Technical field used to decide if "
        "retention tax should be printed on invoice PDF reports."
    )
