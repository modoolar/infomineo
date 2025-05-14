# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate 15.0.0.9.0 started")

    rating_query = """UPDATE rating_rating SET consumed = TRUE ;"""
    cr.execute(rating_query)

    logger.info("Post-migrate 15.0.0.9.0 finished")
