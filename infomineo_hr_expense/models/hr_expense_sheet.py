# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tests.common import Form


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    company_id = fields.Many2one(
        states={"draft": [("readonly", False)], "submit": [("readonly", False)]}
    )
    employee_id = fields.Many2one(
        states={"draft": [("readonly", False)], "submit": [("readonly", False)]}
    )
    currency_id = fields.Many2one(
        states={"draft": [("readonly", False)], "submit": [("readonly", False)]}
    )

    def action_change_company(self):
        action = self.env.ref(
            "infomineo_hr_expense.action_hr_expense_sheet_company_switch"
        ).read()[0]
        action["context"] = dict(
            switch_company_ids=(self.env.user.company_ids - self.env.company).ids,
            switch_currency_ids=(self.sudo().env["res.currency"].search([])).ids,
        )
        return action

    def _action_change_company(self, company_id, currency_id):
        self.ensure_one()
        self = self.sudo().with_company(company_id)

        employee = self.env["hr.employee"].search(
            (
                [
                    ("user_id", "=", self.employee_id.user_id.id),
                    ("company_id", "in", [False, company_id]),
                ]
            ),
            limit=1,
        )
        to_company = self.env["res.company"].browse(company_id)
        to_currency = self.env["res.currency"]

        if currency_id:
            to_currency = self.env["res.currency"].browse(currency_id)

        if not employee:
            raise ValidationError(
                _("There is no related employee for selected company.")
            )

        sheet_form = Form(self, "hr_expense.view_hr_expense_sheet_form")

        expense_line_ids = self.expense_line_ids
        new_journal_id = self.with_company(company_id)._default_journal_id()
        new_journal = self.env["account.journal"].browse(new_journal_id)
        new_bank_journal_id = self.with_company(company_id)._default_bank_journal_id()

        sheet_form.company_id = to_company
        sheet_form.journal_id = new_journal
        sheet_form.bank_journal_id = new_bank_journal_id
        sheet_form.employee_id = employee
        sheet_form.currency_id = (
            to_currency or new_journal.currency_id or new_journal.company_id.currency_id
        )

        sheet_form.expense_line_ids.clear()

        for eli in expense_line_ids:
            eli_form = Form(eli.sudo(), "hr_expense.hr_expense_view_form")
            eli_form.company_id = to_company
            eli_form.currency_id = (
                to_currency
                or new_journal.currency_id
                or new_journal.company_id.currency_id
                or to_company.currency_id
            )
            eli_form.unit_amount = (
                eli.unit_amount
                if not to_currency
                else eli.currency_id._convert(
                    eli.unit_amount, to_currency, to_company, fields.Date.today()
                )
            )

            eli_form.save()

            sheet_form.expense_line_ids.add(eli)

        sheet_form.save()
