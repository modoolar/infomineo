# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
import logging


def migrate(cr, version):
    """
    Update job_title field on hr_employee based on the name of related hr_job.
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Post-migrate 15.0.1.4.3 started: "
        "Migrating data from hr_job.name to hr_employee.job_title"
    )
    query = """
        UPDATE hr_employee hre SET job_title = (
        SELECT name FROM hr_job WHERE id = hre.job_id);
    """
    cr.execute(query)

    logger.info(
        "Post-migrate 15.0.1.4.3 finished: "
        "Migrating data from hr_job.name to hr_employee.job_title"
    )
