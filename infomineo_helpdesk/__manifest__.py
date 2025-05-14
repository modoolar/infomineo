# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo Helpdesk",
    "summary": "Infomineo customizations for module Helpdesk",
    "version": "15.0.1.5.7",
    "category": "Helpdesk",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["helpdesk", "infomineo_rating"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/mail_template_data.xml",
        "views/helpdesk_views.xml",
        "views/helpdesk_stage_views.xml",
        "views/helpdesk_team_views.xml",
        "views/rating_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
