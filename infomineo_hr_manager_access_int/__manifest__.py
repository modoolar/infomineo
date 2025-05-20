# -*- coding: utf-8 -*-

{
    'name': "Employees Manager Access",
    'summary': "Employees Manager Access",
    'description': "only the employees manager can change the approvers.",
    "author": "Infomineo",
    "website": "https://infomineo.com",

    'category': 'Human Resources/Employees',
    'version': '15.0.0.1.1',

    'depends': ['hr', 'infomineo_hr', 'hr_holidays', 'hr_expense', 'infomineo_timesheet_grid', 'approvals_matrix'],
    'data': [
        'views/hr_employee_views.xml',
    ],
    'auto_install': False,
    'application': False,

}
