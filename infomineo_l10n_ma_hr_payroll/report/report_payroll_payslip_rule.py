# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

REPORT_PAYSLIP_RULE_SELECTION = [
    ("contract_amount", "Amount from Contract"),
    ("payslip_amount", "Amount from Payslip"),
    ("python_code", "Python Code"),
    ("number_of_days", "Number of Days"),
    ("nothing", "Nothing"),
]


class ReportPayrollPayslipRule(models.Model):
    _name = "report.payroll.payslip.rule"
    _order = "sequence, id"
    _description = "Report Payroll Payslip Rule"

    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    name = fields.Char()
    code = fields.Char()

    struct_id = fields.Many2one(
        comodel_name="hr.payroll.structure", required=True, index=True
    )
    rule_id = fields.Many2one(comodel_name="hr.salary.rule", required=False, index=True)
    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda x: x.env.user.company_id,
        index=True,
    )
    base_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    base_value = fields.Char()
    salarie_taux_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    salarie_taux_value = fields.Char()
    salarie_gains_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    salarie_gains_value = fields.Char()
    salarie_retenue_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    salarie_retenue_value = fields.Char()
    employeur_taux_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    employeur_taux_value = fields.Char()
    employeur_charge_type = fields.Selection(selection=REPORT_PAYSLIP_RULE_SELECTION)
    employeur_charge_value = fields.Char()
    show_if_zero = fields.Boolean()
    use_in_total = fields.Boolean(default=True)

    @api.onchange("rule_id")
    def _onchange_rule_id(self):
        self.name = self.rule_id.name if self.rule_id else ""
        self.code = self.rule_id.code if self.rule_id else ""

    @api.constrains("struct_id", "rule_id", "company_id")
    def _check_unique_rule(self):
        domain = [
            ("rule_id", "in", self.rule_id.ids),
            ("struct_id", "in", self.struct_id.ids),
        ]
        fields = ["rule_id", "struct_id", "company_id"]
        groupby = ["rule_id", "struct_id", "company_id"]
        records = self.read_group(domain, fields, groupby, lazy=False)

        error_message_lines = []
        for rec in records:
            if rec["__count"] != 1:
                error_message_lines.append(_(" - Rule: %s", rec["rule_id"][1]))
        if error_message_lines:
            raise UserError(
                _(
                    "The combination of Payroll Structs and Rules must"
                    " be unique across a company.\nFollowing combination"
                    " contains duplicates(already exists):\n"
                )
                + "\n".join(error_message_lines)
            )

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

    def _get_localdict(self, payslip):
        localdict = payslip._get_localdict()

        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update(
                {
                    "result": None,
                    "result_qty": 1.0,
                    "result_rate": 100,
                    "result_name": False,
                }
            )
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                # set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                # sum the amount for its salary category
                localdict = rule.category_id._sum_salary_rule_category(
                    localdict, tot_rule - previous_amount
                )

        return localdict

    def _get_type_fields(self):
        """
        The position of the name of the field
        corresponds with the column number.
        """
        return [
            ("base_type", "base_value"),
            ("salarie_taux_type", "salarie_taux_value"),
            ("salarie_gains_type", "salarie_gains_value"),
            ("salarie_retenue_type", "salarie_retenue_value"),
            ("employeur_taux_type", "employeur_taux_value"),
            ("employeur_charge_type", "employeur_charge_value"),
        ]
