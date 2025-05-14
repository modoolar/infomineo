# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate 15.0.0.3.0 started")

    env = api.Environment(cr, SUPERUSER_ID, {})
    env["rating.rating"].search([(1, "=", 1)])._compute_rating_text()

    logger.info("Post-migrate 15.0.0.3.0 finished: Update ratings text.")
