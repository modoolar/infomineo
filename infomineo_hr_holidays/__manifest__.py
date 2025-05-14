# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo HR Holidays",
    "summary": "Infomineo customizations for module HR Holidays",
    "version": "15.0.0.6.3",
    "category": "HR",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["infomineo_hr_holidays_accruals", "hr_contract", "infomineo_hr"],
    "data": [
        "security/security.xml",
        "views/hr_leave_views.xml",
        "views/hr_leave_type_views.xml",
        "views/hr_leave_allocation_views.xml",
        "views/hr_leave_accrual_views.xml",
        "views/hr_holidays_views.xml",
    ],
}
