# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo HR Contract",
    "summary": "Infomineo customizations for module HR Contract",
    "version": "15.0.1.5.1",
    "category": "HR",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["hr_contract", "infomineo_hr"],
    "data": [
        "views/hr_contract_views.xml",
        "views/hr_employee_views.xml",
        "views/employee_employment_history_views.xml",
    ],
    "post_load": "post_load",
}
