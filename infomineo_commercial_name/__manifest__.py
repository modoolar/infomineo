# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Commercial Name",
    "summary": "Commercial name extension for partner and account report",
    "version": "15.0.0.2.0",
    "category": "Account/Accounting",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "account_reports",
    ],
    "data": [
        "security/ir.model.access.csv",
        "view/res_partner_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "infomineo_commercial_name/static/src/js/account_report.js",
        ],
        "web.assets_qweb": [
            "account_reports/static/src/xml/**/*",
        ],
    },
}
