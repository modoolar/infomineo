# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    l10n_ae_vat_amount_no_retenetion = fields.Monetary(
        compute="_compute_vat_amount_no_retention", string="VAT Amount"
    )

    @api.depends("price_subtotal", "price_total")
    def _compute_vat_amount_no_retention(self):
        for record in self:
            amount = record.price_unit * (1 - (record.discount / 100.0))
            retention = 0.0
            taxes = record.tax_ids._origin.with_context(force_sign=1).compute_all(
                amount,
                quantity=record.quantity,
                currency=record.currency_id,
                product=record.product_id,
                partner=record.partner_id,
                is_refund=record.move_id.move_type in ("out_refund", "in_refund"),
            )
            for tax_vals in taxes["taxes"]:
                tax = self.env["account.tax"].browse([tax_vals["id"]])
                if tax.tax_group_id.is_retention:
                    retention += tax_vals["amount"]
            record.l10n_ae_vat_amount_no_retenetion = (
                record.price_total - record.price_subtotal - retention
            )
