# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Rating Survey",
    "summary": "Functional extensions for rating by survey functionality",
    "version": "15.0.0.19.1",
    "category": "Hidden",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": ["infomineo_rating", "survey"],
    "data": [
        "data/survey_survey.xml",
        "views/rating_template.xml",
        "views/rating_rating_views.xml",
        "views/survey_user_input_line_views.xml",
        "views/survey_survey_view.xml",
    ],
    "assets": {
        "infomineo_rating_survey.rating_survey_assets": [
            "infomineo_rating_survey/static/src/js/survey_form.js",
        ],
    },
    "post_load": "post_load",
}
