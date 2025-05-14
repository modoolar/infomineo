# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_template_id = fields.Many2one(
        default=False,
    )
