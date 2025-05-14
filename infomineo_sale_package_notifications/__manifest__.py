# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Infomineo Sale Package Expiry Notifications",
    "summary": "Infomineo specific extensions around Sale Package pricing model",
    "version": "15.0.0.1.0",
    "category": "Sale",
    "license": "LGPL-3",
    "author": "Modoolar",
    "maintainers": "Modoolar",
    "website": "https://modoolar.com",
    "depends": ["sale_package_pricing_model", "base_notifier"],
    "data": [
        "data/sale_order_data.xml",
        "data/project_project_data.xml",
        "data/mail_channel_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
