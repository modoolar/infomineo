# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import Form
from odoo.tools.misc import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    company_id = fields.Many2one(readonly=False)
    tax_declared = fields.Boolean(string="VAT Declaration")
    serie = fields.Text()
    uuid = fields.Text(string="UUID")
    voucher_type = fields.Text()
    payment_method = fields.Text()
    show_additional_bill_fields = fields.Boolean(
        related="company_id.show_additional_bill_fields"
    )

    def action_change_company(self):
        self.ensure_one()

        action = self.env.ref(
            "infomineo_account.action_account_move_company_switch"
        ).read()[0]
        action["context"] = dict(
            switch_company_ids=(self.env.user.company_ids - self.env.company).ids,
            switch_currency_ids=(self.sudo().env["res.currency"].search([])).ids,
        )

        return action

    def _action_change_company(self, company_id, currency_id):
        self.ensure_one()

        if self.posted_before:
            raise UserError(
                _(
                    "We are not able to change assigned journal "
                    "on invoices that has already been posted before."
                )
            )

        ail_data = self.invoice_line_ids._prepare_currency_switch_lines_data(
            company_id, currency_id
        )
        new_journal = (
            self.sudo()
            .with_context(
                default_company_id=company_id,
                default_move_type=self.move_type,
                default_currency_id=currency_id or False,
            )
            ._get_default_journal()
        )

        invoice_form = Form(
            self.sudo().with_context(default_move_type=self.move_type),
            "account.view_move_form",
        )

        invoice_form.company_id = self.env["res.company"].browse(company_id)
        invoice_form.journal_id = new_journal
        invoice_form.partner_id = self.partner_id
        invoice_form.currency_id = (
            new_journal.currency_id or new_journal.company_id.currency_id
        )

        for __ in enumerate(self.invoice_line_ids):
            invoice_form.invoice_line_ids.remove(0)

        for data in ail_data:
            accounts = (
                data.get("product_id")
                .with_company(company_id)
                .product_tmpl_id.get_product_accounts()
            )
            if not data.get("product_id") and data.get("account_id"):
                accounts["income"] = accounts["expense"] = data.get("account_id")
            partner = self.partner_id.with_company(company_id)
            if (
                self.is_sale_document(include_receipts=True)
                and not accounts["income"]
                or self.is_purchase_document(include_receipts=True)
                and not accounts["expense"]
            ):
                raise ValidationError(
                    _(
                        "Unable to switch to selected company. "
                        "Accounts are not configured on product or on product category."
                    )
                )
            if (
                self.is_sale_document(include_receipts=True)
                and not partner.property_account_receivable_id
                or self.is_purchase_document(include_receipts=True)
                and not partner.property_account_payable_id
            ):
                raise ValidationError(
                    _(
                        "Unable to switch to selected company. "
                        "Accounts are not configured on partner."
                    )
                )
            with invoice_form.invoice_line_ids.new() as ail:
                ail.product_id = data.get("product_id")
                ail.quantity = data.get("quantity")
                ail.product_uom_id = data.get("product_uom_id")
                ail.name = data.get("name")
                ail.price_unit = data.get("price_unit")
                ail.discount = data.get("discount")

        invoice_form.save()

    @api.model
    def _get_tax_totals(
        self, partner, tax_lines_data, amount_total, amount_untaxed, currency
    ):
        res = super()._get_tax_totals(
            partner, tax_lines_data, amount_total, amount_untaxed, currency
        )

        self.add_aditional_tax_totals_fields(res)

        retention_amount = 0.0
        no_retention_amount = 0.0
        for amount_by_group_list in res["groups_by_subtotal"].values():
            for amount_by_group in amount_by_group_list:
                if amount_by_group.get("tax_group_is_retention", False):
                    retention_amount += amount_by_group["tax_group_amount"]
                else:
                    no_retention_amount += amount_by_group["tax_group_amount"]
        res["amount_no_retention"] = no_retention_amount
        res["amount_retention_diff"] = amount_total - retention_amount
        res["formatted_amount_retention_diff"] = formatLang(
            self.env, res["amount_retention_diff"], currency_obj=currency
        )

        return res

    @api.model
    def add_aditional_tax_totals_fields(self, tax_totals):
        """
        Adding field `is_retention` from tax group in the structure.
        """
        tax_totals["groups_by_subtotal"] = {
            k: [
                self._add_tax_fields(group_by_subtotal)
                for group_by_subtotal in groups_by_subtotal
            ]
            for k, groups_by_subtotal in tax_totals["groups_by_subtotal"].items()
        }

    def _add_tax_fields(self, tax_group):
        return dict(
            tax_group,
            tax_group_is_retention=self.env["account.tax.group"]
            .browse(tax_group["tax_group_id"])
            .is_retention,
        )
