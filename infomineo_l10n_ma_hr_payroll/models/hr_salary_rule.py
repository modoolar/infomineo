# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    sequence_pdf = fields.Integer(string="PDF Sequence")
    print_on_pdf = fields.Boolean()
    employee_tax_pdf = fields.Float(string="Employee Tax")
    employer_tax_pdf = fields.Float(string="Employer Tax")
    is_salary_debit_pdf = fields.Boolean(string="Is Salary Debit")
    for_employee_pdf = fields.Boolean(string="For Employee")
    for_employer_pdf = fields.Boolean(string="For Employer")
    use_base_pdf = fields.Boolean(string="Use Base Value")
    hide_empty = fields.Boolean(string="Hide if Empty Value")
