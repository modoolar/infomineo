# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Invoicing",
    "summary": "Infomineo specific Invoicing extensions",
    "version": "15.0.0.15.0",
    "category": "Account/Accounting",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "account",
        "infomineo_product",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/account_move_views.xml",
        "views/res_partner_views.xml",
        "views/account_analytic_default_views.xml",
        "views/report_invoice.xml",
        "views/res_bank_views.xml",
        "views/report_templates.xml",
        "wizards/account_move_company_switch_wizard_views.xml",
        "report/wider_header_paper_format.xml",
        "views/res_config_settings_views.xml",
    ],
}
