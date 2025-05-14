# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import logging

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Update Default Discuss channel for existing companies.
    """

    logger = logging.getLogger(__name__)
    logger.info("Post-init started: Default Discuss channel update.")

    env = api.Environment(cr, SUPERUSER_ID, {})
    default_contact_channel = env.ref(
        "contacts_certificates.channel_contact_channel"
    ).id

    env["res.company"].search([]).write(
        {
            "contact_discuss_channel_id": default_contact_channel,
            "notification_threshold": env[
                "res.company"
            ]._DEFAULT_NOTIFICATION_THRESHOLD,
        }
    )

    config = env["res.config.settings"].create({})
    config.write(
        dict(
            contact_discuss_channel_id=default_contact_channel,
            notification_threshold=env["res.company"]._DEFAULT_NOTIFICATION_THRESHOLD,
        )
    )
    config.execute()

    logger.info("Post-init finished: Default Discuss channel updated.")
