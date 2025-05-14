# Copyright (C) 2020 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import SUPERUSER_ID, api


def load_config(env):
    config = env["res.config.settings"].create({})
    config.write(
        dict(
            group_subtask_project=True,
            group_project_stages=True,
            group_sale_order_template=True,
            group_discount_per_so_line=True,
            group_warning_sale=True,
            group_proforma_sales=True,
        )
    )
    config.execute()


def post_init_hook(cr, registry):  # pragma: no cover
    env = api.Environment(cr, SUPERUSER_ID, {})

    load_config(env)
