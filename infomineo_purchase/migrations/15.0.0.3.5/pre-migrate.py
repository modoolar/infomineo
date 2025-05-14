# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Andreja Bićanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
import logging

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """Remove old res_group 'View own purchase orders' from rule_group_rel table"""

    env = api.Environment(cr, SUPERUSER_ID, {})

    logger = logging.getLogger(__name__)
    logger.info("Pre-migrate 15.0.0.3.5 started")

    own_purchase_orders_group = env.ref(
        "infomineo_purchase.group_own_purchase_order", raise_if_not_found=False
    )

    if own_purchase_orders_group:
        cr.execute(
            """DELETE FROM rule_group_rel WHERE group_id = %s;""",
            (own_purchase_orders_group.id,),
        )
        logger.info("Record '%s' is removed from database", own_purchase_orders_group)

    logger.info("Pre-migrate 15.0.0.3.5 finished")
