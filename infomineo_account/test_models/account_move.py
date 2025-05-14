# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def add_aditional_tax_totals_fields(self, tax_totals):
        if self.env.context.get("infomineo_test_account"):
            return super().add_aditional_tax_totals_fields(tax_totals)
        return False

    @api.model
    def _get_tax_totals(
        self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    ):
        res = super()._get_tax_totals(
            partner, tax_lines_data, amount_total, amount_untaxed, currency
        )

        keys_to_ignore = {
            "amount_no_retention",
            "amount_retention_diff",
            "formatted_amount_retention_diff",
        }
        for key in keys_to_ignore:
            del res[key]
        return res
