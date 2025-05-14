# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import logging

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Update Default Sales Package Discuss channel for existing companies.
    """

    logger = logging.getLogger(__name__)
    logger.info("Post-init started: Default Sales Discuss channel update.")

    env = api.Environment(cr, SUPERUSER_ID, {})
    default_sales_package_channel = env.ref(
        "infomineo_sale_package_notifications.sales_package_discuss_channel"
    ).id
    default_project_package_channel = env.ref(
        "infomineo_sale_package_notifications.project_discuss_channel"
    ).id

    env["res.company"].search([]).write(
        {
            "sales_package_discuss_channel_id": default_sales_package_channel,
            "sales_package_notification_threshold": env[
                "res.company"
            ]._DEFAULT_SALES_PACKAGE_NOTIFICATION_THRESHOLD,
            "project_package_discuss_channel_id": default_project_package_channel,
            "project_package_notification_threshold": env[
                "res.company"
            ]._DEFAULT_PROJECT_PACKAGE_NOTIFICATION_THRESHOLD,
        }
    )

    config = env["res.config.settings"].create({})
    config.write(
        dict(
            sales_package_discuss_channel_id=default_sales_package_channel,
            sales_package_notification_threshold=env[
                "res.company"
            ]._DEFAULT_SALES_PACKAGE_NOTIFICATION_THRESHOLD,
            project_package_discuss_channel_id=default_project_package_channel,
            project_package_notification_threshold=env[
                "res.company"
            ]._DEFAULT_PROJECT_PACKAGE_NOTIFICATION_THRESHOLD,
        )
    )
    config.execute()

    logger.info("Post-init finished: Default Sales Discuss channel updated.")
