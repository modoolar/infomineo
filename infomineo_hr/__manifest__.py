# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo HR",
    "summary": "Infomineo customizations for module HR",
    "version": "15.0.1.15.5",
    "category": "HR",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["hr"],
    "data": [
        "security/ir.model.access.csv",
        "views/employee_employment_history_views.xml",
        "views/hr_employee_views.xml",
        "views/hr_study_field_views.xml",
        "views/hr_team_views.xml",
        "wizard/change_coach_wizard_views.xml",
        "wizard/hr_departure_wizard_views.xml",
        "views/hr_work_location_views.xml",
        "views/res_users.xml",
    ],
    "post_load": "post_load",
}
