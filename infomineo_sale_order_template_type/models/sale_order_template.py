# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    order_type = fields.Selection(
        selection_add=[
            ("retainer", "Retainer"),
            ("project", "Project"),
            ("flexible", "Flexible"),
            ("mixed", "Mixed"),
        ],
        ondelete={
            "retainer": "set default",
            "project": "set default",
            "flexible": "set default",
            "mixed": "set default",
        },
    )
