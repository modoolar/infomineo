# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api

from odoo.addons.account.models.account_move import (
    AccountMoveLine as originalAccountMoveLine,
)


@api.depends("product_id", "account_id", "partner_id", "date")
def _compute_analytic_tag_ids(self):
    for record in self:
        if not record.exclude_from_invoice_tab or not record.move_id.is_invoice(
            include_receipts=True
        ):
            rec = self.env["account.analytic.default"].account_get(
                product_id=record.product_id.id,
                partner_id=record.partner_id.commercial_partner_id.id
                or record.move_id.partner_id.commercial_partner_id.id,
                account_id=record.account_id.id,
                user_id=record.env.uid,
                date=record.date,
                company_id=record.move_id.company_id.id,
                department_id=record.department_id.id,
            )
            if rec:
                record.analytic_tag_ids = rec.analytic_tag_ids


def patch_account_move_line_methods():
    originalAccountMoveLine._patch_method(
        "_compute_analytic_tag_ids", _compute_analytic_tag_ids
    )
