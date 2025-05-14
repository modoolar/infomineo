# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class HrExpenseSheetCompanySwitchWizard(models.TransientModel):
    _name = "hr.expense.sheet.company.switch.wizard"
    _description = "Expense Sheet Company Switch Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Switch to company",
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Switch to currency",
    )

    def switch_company(self):
        active_ids = self._context.get("active_id", self.env["hr.expense.sheet"])
        expense_sheet = self.env["hr.expense.sheet"].browse(active_ids)

        expense_sheet._action_change_company(self.company_id.id, self.currency_id.id)
