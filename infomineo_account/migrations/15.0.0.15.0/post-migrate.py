# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate 15.0.0.15.0 started")

    alter_query = """UPDATE account_move SET payment_method = x_studio_forma_de_pago;"""
    cr.execute(alter_query)

    logger.info("Post-migrate 15.0.0.15.0 finished")
