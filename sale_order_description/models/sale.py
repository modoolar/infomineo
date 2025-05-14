# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Petar Najman <petar.najman@modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    description = fields.Char(index=True)
