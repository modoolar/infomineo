# -*- coding: utf-8 -*-

{
    'name': "Timeoff Remainder",
    'summary': "Send Timeoff Remainder",
    'description': "Send Timeoff remainder e-mail for pending requests to the managers through automated action.",
    "author": "Infomineo",
    "website": "https://infomineo.com",

    'category': 'Human Resources/Time Off',
    'version': '15.0.0.1.0',

    'depends': ['hr_holidays'],
    'data': [
        'data/ir_cron_data.xml',
        'data/timeoff_remainder_email_template.xml',
    ],
    'auto_install': False,
    'application': False,

}
