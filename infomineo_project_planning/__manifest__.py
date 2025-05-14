# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Project Planning",
    "summary": "Infomineo Project Planning module",
    "version": "15.0.0.12.2",
    "category": "Hidden",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "planning_hr_skills",
        "project_forecast",
        "infomineo_hr",
        "infomineo_project_hr",
        "infomineo_planning",
    ],
    "post_init_hook": "post_init_hook",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_config_settings_views.xml",
        "views/project_project_views.xml",
        "views/project_task_views.xml",
        "views/planning_views.xml",
    ],
    "assets": {
        "web.assets_backend": ["infomineo_project_planning/static/src/js/gantt_row.js"],
    },
    "post_load": "post_load",
}
