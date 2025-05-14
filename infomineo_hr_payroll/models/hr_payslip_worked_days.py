# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = "hr.payslip.worked_days"

    amount = fields.Monetary(string="Computed Amount")
    manual_amount = fields.Monetary(
        string="Amount", compute="_compute_manual_amount", readonly=False, store=True
    )

    @api.depends(
        "is_paid",
        "number_of_hours",
        "payslip_id",
        "contract_id.wage",
        "payslip_id.sum_worked_hours",
    )
    def _compute_amount(self):
        manuals_entered = self.filtered(lambda x: x.manual_amount > 0)
        for rec in manuals_entered:
            rec.amount = rec.manual_amount
        return super(HrPayslipWorkedDays, self - manuals_entered)._compute_amount()

    @api.depends("payslip_id.contract_id.wage")
    def _compute_manual_amount(self):
        for rec in self:
            rec.manual_amount = (
                rec.manual_amount
                if rec.manual_amount > 0
                else rec.payslip_id.contract_id.wage
            )
