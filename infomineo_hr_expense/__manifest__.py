# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo HR Expense",
    "summary": "Functional extensions for hr expense module",
    "version": "15.0.0.3.0",
    "category": "HR",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "hr_expense",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/hr_expense_sheet_company_switch_wizard_views.xml",
        "views/hr_expense_views.xml",
        "views/res_users_views.xml",
        "views/hr_employee_views.xml",
    ],
}
