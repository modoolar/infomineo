# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo HR Timesheet Attendance",
    "summary": "Functional extensions for HR Timesheet Attendance",
    "version": "15.0.0.4.0",
    "category": "HR",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": ["hr_timesheet_attendance", "infomineo_hr_attendance"],
    "data": [
        "security/ir.model.access.csv",
        "views/hr_employee_views.xml",
    ],
}
