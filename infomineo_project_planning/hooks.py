# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import logging

from odoo import SUPERUSER_ID, api

from .substitutions.resource_resource import patch_account_move_line_methods


def post_init_hook(cr, registry):
    """
    Update Project's project_plan_capacity field on existing project
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Post-init hook 15.0.0.1.0 started: Update Project's "
        "project_plan_capacity field on existing project"
    )

    env = api.Environment(cr, SUPERUSER_ID, {})

    projects = env["project.project"].search([])
    projects.write({"project_plan_capacity": True})

    logger.info(
        "Post-init hook 15.0.0.1.0 finished: Update Project's "
        "project_plan_capacity field on existing project"
    )


def post_load():
    patch_account_move_line_methods()
