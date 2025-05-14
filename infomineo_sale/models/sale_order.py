# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    client_order_ref = fields.Char(string="Client Purchase order No")
    specific_condition = fields.Html(translate=True)
    description = fields.Char(string="Deal name")
    sale_order_template_id = fields.Many2one(required=True)
    second_sales_person_id = fields.Many2one(tracking=True)
