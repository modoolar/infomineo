# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    order_type = fields.Selection(
        selection=[
            ("other", "Other"),
        ],
        default="other",
        index=True,
    )

    @api.onchange("sale_order_template_id")
    def _onchange_sale_order_template_id(self):
        self.order_type = self.sale_order_template_id.order_type
