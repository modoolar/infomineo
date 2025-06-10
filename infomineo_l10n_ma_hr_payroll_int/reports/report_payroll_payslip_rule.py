# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval




class ReportPayrollPayslipRule(models.Model):
    _inherit = "report.payroll.payslip.rule"


    def get_amount(self, payslip):
        employee_payroll_table = list()
        report_fields = self._get_type_fields()
        localdict = self._get_localdict(payslip)

        for report_rule in self:
            salary_values = []

            for type_field, value_field in report_fields:
                if report_rule[type_field] == "contract_amount":
                    contract = payslip.contract_id
                    column_value = (
                        contract[report_rule[value_field]]
                        if report_rule[value_field]
                        else 0
                    )

                elif (
                    report_rule[type_field] == "payslip_amount" and report_rule.rule_id
                ):

                    if report_rule[value_field]:
                        payslip_rule = payslip.line_ids.filtered(lambda x: x.code == report_rule[value_field])
                    else:
                        payslip_rule = payslip.line_ids.filtered(
                            lambda x: x.code == report_rule.rule_id.code
                        )
                    if not payslip_rule:
                        column_value = 0
                    else:
                        column_value = payslip_rule.total if payslip_rule else 0

                elif report_rule[type_field] == "python_code":
                    if report_rule[value_field].replace(".", "", 1).isdigit():
                        try:
                            column_value = int(report_rule[value_field])
                        except ValueError:
                            column_value = float(report_rule[value_field])
                    else:
                        try:
                            safe_eval(
                                report_rule[value_field] or 0.0,
                                localdict,
                                mode="exec",
                                nocopy=True,
                            )
                            column_value = float(localdict["result"])
                        except Exception as e:
                            raise UserError(
                                _(
                                    """%s:
                                - Employee: %s
                                - Contract: %s
                                - Payslip: %s
                                - Salary rule: %s (%s)
                                - Error: %s"""
                                )
                                % (
                                    "Wrong quantity defined for:",
                                    localdict["employee"].name,
                                    localdict["contract"].name,
                                    localdict["payslip"].dict.name,
                                    report_rule.name,
                                    report_rule.code,
                                    e,
                                )
                            )
                elif report_rule[type_field] == "number_of_days":
                    work_days_line = payslip.worked_days_line_ids.filtered(
                        lambda x: x.work_entry_type_id.code == "WORK100"
                    )
                    column_value = (
                        work_days_line[0].number_of_days if work_days_line else 0
                    )

                elif report_rule[type_field] == "nothing":
                    column_value = 0

                else:
                    column_value = 0
                salary_values.append(column_value)
            if not report_rule.show_if_zero and salary_values[0] <= 0:
                continue

            employee_payroll_table.append(
                {
                    "sequence": report_rule.sequence,
                    "code": report_rule.code,
                    "name": report_rule.name,
                    "base": salary_values[0],
                    "salary_tax": salary_values[1],
                    "debit": salary_values[2],
                    "credit": salary_values[3],
                    "employer_tax": salary_values[4],
                    "employer_value": salary_values[5],
                    "use_in_total": report_rule.use_in_total,
                }
            )

        return employee_payroll_table

