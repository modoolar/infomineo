# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).


import logging

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Update Helpdesk Ticket User rule.
    """

    logger = logging.getLogger(__name__)
    logger.info("Post-init started: Helpdesk Ticket User rule update.")

    env = api.Environment(cr, SUPERUSER_ID, {})

    helpdesk_ticket_user_rule = env.ref("helpdesk.helpdesk_ticket_user_rule")
    helpdesk_ticket_user_rule.domain_force = '[("user_id","=", user.id)]'

    logger.info("Post-init finished: Helpdesk Ticket User rule updated.")
