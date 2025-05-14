# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    analytic_account_id = fields.Many2one(string="Project Code")
    analytic_tag_ids = fields.Many2many(string="Department")
    serie = fields.Text(related="move_id.serie")
    uuid = fields.Text(string="UUID", related="move_id.uuid")
    voucher_type = fields.Text(related="move_id.voucher_type")
    payment_method = fields.Text(related="move_id.payment_method")
    show_additional_bill_fields = fields.Boolean(
        related="move_id.show_additional_bill_fields"
    )

    def _prepare_currency_switch_lines_data(self, company_id, currency_id):
        to_currency = self.env["res.currency"]
        to_company = self.env["res.company"]
        to_date = False

        if currency_id:
            to_currency = self.sudo().env["res.currency"].browse(currency_id)
            to_date = self.sudo().move_id.invoice_date or fields.Date.today()
            to_company = self.sudo().env["res.company"].browse(company_id)

        return [
            {
                "product_id": line.product_id,
                "quantity": line.quantity,
                "product_uom_id": line.product_uom_id,
                "name": line.name,
                "price_unit": line.price_unit
                if not to_currency
                else self.sudo().currency_id._convert(
                    line.price_unit, to_currency, to_company, to_date
                ),
                "discount": line.discount,
                "account_id": line.account_id,
            }
            for line in self
        ]
