# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models


class ReportHrPayrollPayslip(models.AbstractModel):
    _name = "report.hr_payroll.report_payslip_lang"

    @api.model
    def _get_report_values(self, docids, data=None):
        payslips = self.env["hr.payslip"].browse(docids)

        return {
            "doc_ids": docids,
            "doc_model": "hr.payslip",
            "data": data,
            "docs": payslips,
            "get_employee_salary_data": self.get_employee_salary_data,
            "get_employee_net_salary": self.get_employee_net_salary,
            "get_total_salary_values": self.get_total_salary_values,
            "get_payslip_working_days": self.get_payslip_working_days,
            "get_base_total": self.get_base_total,
            "get_salary_net_impossible": self.get_salary_net_impossible,
            "get_yearly_salary_summary": self.get_yearly_salary_summary,
            "get_number_of_charges": self.get_number_of_charges,
        }

    @api.model
    def get_employee_salary_data(self, payslip):
        payslip.ensure_one()

        report_rules = self.env["report.payroll.payslip.rule"].search(
            [
                ("struct_id", "=", payslip.struct_id.id),
                ("company_id", "=", payslip.company_id.id),
            ]
        )
        employee_payroll_table = report_rules.get_amount(payslip)

        employee_payroll_table.sort(key=lambda e: e["sequence"])
        return employee_payroll_table

    @api.model
    def get_employee_net_salary(self, payslip):
        payslip.ensure_one()

        net_salary_line = payslip.line_ids.filtered(lambda x: x.code == "NET")
        return round(net_salary_line.total, 2) if net_salary_line else 0

    @api.model
    def get_total_salary_values(self, employee_salary_table):
        totals = dict(
            debit=0,
            credit=0,
            employer_value=0,
        )
        for item in employee_salary_table:
            if "use_in_total" in item and not item["use_in_total"]:
                continue
            if item["code"] == "GROSS":
                totals["debit"] = item["debit"]
            totals["credit"] += item["credit"]
            totals["employer_value"] += item["employer_value"]

        return totals

    @api.model
    def get_payslip_working_days(self, payslip):
        payslip.ensure_one()

        working_days = 0

        if payslip.worked_days_line_ids:
            line = payslip.worked_days_line_ids[0]
            working_days = line.number_of_days

        return working_days

    @api.model
    def get_base_total(self, payslip):
        payslip.ensure_one()

        net_salary_line = payslip.line_ids.filtered(lambda x: x.code == "TXG")
        return net_salary_line.total if net_salary_line else 0

    @api.model
    def get_salary_net_impossible(self, payslip):
        payslip.ensure_one()

        salary_net_impossible = payslip.line_ids.filtered(lambda x: x.code == "SALTH")
        return salary_net_impossible.total if salary_net_impossible else 0

    def get_yearly_salary_summary(self, employee):
        current_year = fields.Date.today().year
        salary_summery = {
            "cumul_jours_travailles": 0,
            "cumul_brut": 0,
            "cumul_brut_imposable": 0,
            "cumul_net_imposable": 0,
            "cumul_ir": 0,
        }

        if current_year == 2022:
            payslips = self.env["hr.payslip"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("date_from", ">=", "2022-07-01"),
                    ("date_to", "<=", "2022-12-31"),
                ]
            )
            salary_summery[
                "cumul_jours_travailles"
            ] += employee.cumul_jours_travailles_pdf
            salary_summery["cumul_brut"] += employee.cumul_brut_pdf
            salary_summery["cumul_brut_imposable"] += employee.cumul_brut_imposable_pdf
            salary_summery["cumul_net_imposable"] += employee.cumul_net_imposable_pdf
            salary_summery["cumul_ir"] += employee.cumul_ir_pdf
        else:
            payslips = self.env["hr.payslip"].search(
                [
                    ("employee_id", "=", employee.id),
                    ("date_from", ">=", str(current_year) + "-01-01"),
                    ("date_to", ">=", str(current_year) + "-12-31"),
                ]
            )
        for payslip in payslips:
            salary_table = self.get_employee_salary_data(payslip)
            salary_totals = self.get_total_salary_values(salary_table)
            total_debit = salary_totals["debit"]
            salary_summery["cumul_jours_travailles"] += self.get_payslip_working_days(
                payslip
            )
            salary_summery["cumul_brut"] += total_debit
            salary_summery["cumul_brut_imposable"] += self.get_base_total(payslip)
            salary_summery["cumul_net_imposable"] += self.get_salary_net_impossible(
                payslip
            )
            itd_line = payslip.line_ids.filtered(lambda x: x.code == "ITD")
            salary_summery["cumul_ir"] += itd_line.total if itd_line else 0

        return salary_summery

    @api.model
    def get_number_of_charges(self, employee):
        employee.ensure_one()

        marital_bonus = 1 if employee.marital == "married" else 0
        return employee.children + marital_bonus
