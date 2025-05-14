# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
{
    "name": "Contacts Certificates",
    "summary": "Extensions around Contacts application",
    "category": "Sales/CRM",
    "version": "15.0.0.2.0",
    "license": "LGPL-3",
    "author": "Modoolar",
    "website": "https://modoolar.com",
    "depends": [
        "base_notifier",
        "contacts",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/mail_channel_data.xml",
        "data/res_users_data.xml",
        "views/res_config_settings_views.xml",
        "views/res_partner_views.xml",
    ],
    "post_init_hook": "post_init_hook",
}
