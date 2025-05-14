# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo HR Holidays Attendance",
    "summary": "Infomineo customizations for module HR Holidays Attendance",
    "version": "15.0.0.6.0",
    "category": "HR",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": [
        "hr_holidays_attendance",
        "infomineo_hr_attendance",
    ],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/hr_employee_views.xml",
    ],
}
