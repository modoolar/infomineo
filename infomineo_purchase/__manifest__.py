# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Infomineo Purchase",
    "summary": "Functional extensions around purchase application",
    "version": "15.0.0.3.8",
    "category": "Operations/Purchase",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "depends": ["purchase"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/purchase_order_views.xml",
        "wizards/purchase_order_company_switch_wizard_views.xml",
    ],
}
