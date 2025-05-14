# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
{
    "name": "Subscriptions Improvements",
    "version": "15.0.1.1.2",
    "category": "Subscription",
    "website": "https://www.modoolar.com/",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "license": "LGPL-3",
    "summary": "Subscriptions Improvements",
    "depends": ["project_sale_subscription", "account"],
    "data": [
        "views/sale_order_views.xml",
        "views/report_invoice.xml",
        "views/sale_subscription_views.xml",
        "views/res_config_settings_views.xml",
        "report/sale_report_templates.xml",
        "wizard/sale_subscription_wizard_views.xml",
    ],
    "assets": {
        "web.assets_qweb": [
            "subscription_improvements/static/src/xml/tax_totals.xml",
        ],
    },
    "post_load": "post_load",
}
