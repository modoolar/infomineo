# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """"""
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate 15.0.0.16.0 started")
    env = api.Environment(cr, SUPERUSER_ID, {})

    project_query = """SELECT id FROM res_company;"""
    cr.execute(project_query)

    for project in (
        env["project.project"]
        .with_user(SUPERUSER_ID)
        .with_context(allowed_company_ids=[r[0] for r in cr.fetchall()])
        .search([])
    ):
        company_id = project.company_id.id if project.company_id else False
        if (
            not env["ir.sequence"]
            .with_user(SUPERUSER_ID)
            .search(
                [
                    ("code", "=", "project.project.next.task.code.%s" % project.id),
                    ("company_id", "=", company_id),
                ]
            )
        ):
            next_task_no_seq = (
                env["ir.sequence"]
                .with_user(SUPERUSER_ID)
                .create(
                    {
                        "name": "Task Next Code for %s" % project.display_name,
                        "code": "project.project.next.task.code.%s" % project.id,
                        "company_id": company_id,
                    }
                )
            )
            task_query = """
                SELECT
                    count(distinct(id))
                FROM
                    project_task
                WHERE
                    project_id = %s and active = True;
            """
            cr.execute(task_query, (project.id,))
            task_count = cr.fetchone()[0]
            next_task_no_seq.number_next = task_count + 1
            project.next_task_number_sequence_id = next_task_no_seq

    logger.info("Post-migrate 15.0.0.16.0 finished")
