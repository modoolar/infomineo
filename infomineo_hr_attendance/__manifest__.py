# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo HR Attendance",
    "summary": "Infomineo customizations for module HR Attendance",
    "version": "15.0.1.1.0",
    "category": "HR",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["hr_attendance", "infomineo_hr"],
    "data": [
        "security/hr_attendance_security.xml",
        "security/hr_holidays_attendance_security.xml",
        "security/ir.model.access.csv",
        "views/employee_employment_history_views.xml",
        "views/hr_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
