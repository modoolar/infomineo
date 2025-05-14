# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Project",
    "summary": "Infomineo Project module",
    "version": "15.0.0.32.1",
    "category": "Project",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "project_enterprise",
        "infomineo_line_of_business",
        "infomineo_rating_survey",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/res_users_views.xml",
        "views/project_task_views.xml",
        "views/rating_rating_views.xml",
        "views/project_project_views.xml",
        "views/project_project_stage_view_form.xml",
        "views/project_views.xml",
        "views/mail_template_views.xml",
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
    ],
    "post_init_hook": "post_init_hook",
    "post_load": "post_load",
    "external_dependencies": {"python": ["openupgradelib", "email-validator"]},
}
