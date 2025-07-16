# -*- coding: utf-8 -*-

{
    'name': "Morocco Payslip Printout",
    'summary': "Fixing for Morocco Payslip Printout",
    'description': "Fixing for Morocco Payslip Printout.",
    "author": "Infomineo",
    "website": "https://infomineo.com",

    'category': 'HR',
    'version': '15.1.0.1.0',

    'depends': ['infomineo_l10n_ma_hr_payroll', 'hr'],
    'data': [
        'views/hr_employee_views.xml',
        'views/hr_payslip_views.xml',
        'views/report_payroll_payslie_rule_views.xml',
        'views/report_payslip_templates.xml',
    ],
    'auto_install': False,
    'application': False,

}
