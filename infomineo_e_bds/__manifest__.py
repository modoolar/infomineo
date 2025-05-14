# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "e-BDS",
    "version": "15.0.0.4.0",
    "category": "Human Resources/Employees",
    "author": "BHECO SERVICES, Modoolar",
    "website": "http://www.bhecoservices.com, http://www.modoolar.com",
    "license": "LGPL-3",
    "depends": ["base", "hr_payroll"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
        "views/hr_payroll_views.xml",
        "views/e_bds_view.xml",
        "views/hr_salary_rule_views.xml",
        "wizard/e_bds_wizard_view.xml",
    ],
}
