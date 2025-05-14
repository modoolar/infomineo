# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    Substituting Accounts on Account Move Lines
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Post-migrate 15.0.0.2.0 started: Update contract reference for individuals"
    )

    env = api.Environment(cr, SUPERUSER_ID, {})

    person_parent_contracts = env["res.partner"].search(
        [("is_company", "=", False), ("parent_id", "!=", False)]
    )
    query = "UPDATE res_partner SET ref = replace(ref, '/', '/C/') WHERE id IN %s"
    cr.execute(query, [tuple(person_parent_contracts.ids)])

    person_no_parent_contracts = env["res.partner"].search(
        [("is_company", "=", False), ("parent_id", "=", False)]
    )
    query = "UPDATE res_partner SET ref = 'C/' || ref WHERE id IN %s"
    cr.execute(query, [tuple(person_no_parent_contracts.ids)])

    logger.info(
        "Post-migrate 15.0.0.2.0 finished: Update contract reference for individuals"
    )
