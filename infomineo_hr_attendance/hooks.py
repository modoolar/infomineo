# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Update Project's project_plan_capacity field on existing project
    """
    from odoo.tools import config

    if not (config.get("test_enable") or config.get("test_file")):
        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    hr_coach_employees_rule = env.ref(
        "infomineo_hr_attendance.hr_coach_pdc_own_employees_rule"
    )
    hr_coach_employees_rule.active = False
