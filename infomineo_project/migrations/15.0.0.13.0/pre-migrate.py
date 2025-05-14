# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging

from openupgradelib.openupgrade import column_exists


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Pre-migrate 15.0.0.13.0 started")

    if not column_exists(cr, "project_task", "code"):
        alter_query = """ALTER TABLE project_task ADD COLUMN code varchar"""
        cr.execute(alter_query)
        update_query = """UPDATE project_task SET code = 'TEST'"""
        cr.execute(update_query)

    if not column_exists(cr, "project_task", "current_task_number"):
        alter_query = (
            """ALTER TABLE project_task ADD COLUMN current_task_number integer"""
        )
        cr.execute(alter_query)
        update_query = """UPDATE project_task SET current_task_number = 0"""
        cr.execute(update_query)

    logger.info("Pre-migrate 15.0.0.13.0 finished")
