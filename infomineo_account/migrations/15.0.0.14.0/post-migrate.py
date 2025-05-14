# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Pre-migrate 15.0.0.14.0 started")

    alter_query = """UPDATE account_move SET serie = x_studio_serie_1,
    voucher_type = x_studio_tipo_de_comprobante, uuid = "x_studio_text_field_NoWAJ";"""
    cr.execute(alter_query)

    logger.info("Pre-migrate 15.0.0.14.0 finished")
