# -*- coding: utf-8 -*-

{
    'name': "Survey Remainder",
    'summary': "Auto-send Surveys and Remainders",
    'description': "Auto-send Surveys and Remainders.",
    "author": "Infomineo",
    "website": "https://infomineo.com",

    'category': 'Marketing/Surveys',
    'version': '15.0.0.1.0',

    'depends': ['survey'],
    'data': [
        'data/ir_cron_data.xml',
        'views/survey_survey_views.xml',
    ],
    'auto_install': False,
    'application': False,

}
