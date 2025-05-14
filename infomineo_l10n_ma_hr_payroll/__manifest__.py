# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo Morocco - HR Contract",
    "summary": "Infomineo specific extensions for Morocco HR Contract.",
    "version": "15.0.1.17.0",
    "category": "HR",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "hr_payroll",
        "infomineo_hr_contract",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_rule_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_contract_views.xml",
        "views/hr_payroll_views.xml",
        "views/report_payslip_templates.xml",
        "views/report_payroll_payslie_rule_views.xml",
        "views/employee_employment_history_views.xml",
        "views/report_payslip_paperformat.xml",
    ],
    "external_dependencies": {"python": ["openupgradelib"]},
}
