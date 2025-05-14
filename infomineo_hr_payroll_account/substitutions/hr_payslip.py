# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.addons.hr_payroll_account.models.hr_payroll_account import (
    HrPayslip as originalHrPayslip,
)


def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
    existing_lines = (
        line_id
        for line_id in line_ids
        if line_id["name"] == line.name
        and line_id["account_id"] == account_id
        and line_id["department_id"] == line.employee_id.department_id.id
        and line_id["analytic_account_id"]
        == (
            line.salary_rule_id.analytic_account_id.id
            or line.slip_id.contract_id.analytic_account_id.id
        )
        and (
            (line_id["debit"] > 0 and credit <= 0)
            or (line_id["credit"] > 0 and debit <= 0)
        )
    )
    return next(existing_lines, False)


def patch_hr_payslip_methods():
    originalHrPayslip._patch_method("_get_existing_lines", _get_existing_lines)
