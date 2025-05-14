# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    gross_taxable_salary = fields.Float(
        compute="_compute_gross_taxable_salary", store=False
    )
    normal = fields.Boolean()

    def _compute_gross_taxable_salary(self):
        for record in self:
            amount = 0.0
            for line in record.line_ids.filtered(
                lambda r: r.salary_rule_id.include_gross_tax
            ):
                amount += line.amount
            record.gross_taxable_salary = amount
