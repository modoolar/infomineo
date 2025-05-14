# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo HR Timesheet",
    "summary": "Functional extensions for hr_timesheet module",
    "version": "15.0.0.7.0",
    "category": "HR",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": ["hr_timesheet"],
    "data": [
        "security/ir.model.access.csv",
        "views/project_task_views.xml",
        "views/hr_timesheet_views.xml",
    ],
}
