# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    line_of_business = fields.Selection(
        selection_add=[
            ("business_research", "Business Research"),
            ("expert_network", "Expert Network"),
            ("graphic_design", "Graphic Design"),
            ("management", "Management"),
        ],
        ondelete={
            "business_research": "set default",
            "expert_network": "set default",
            "graphic_design": "set default",
            "management": "set default",
        },
        tracking=True,
    )
