# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    line_of_business = fields.Selection(
        selection_add=[
            ("generic_words", "Generic Words"),
            ("generic_hours", "Generic Hours"),
        ],
        ondelete={
            "generic_words": "set default",
            "generic_hours": "set default",
        },
    )
