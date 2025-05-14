# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class Planning(models.Model):
    _inherit = "planning.slot"

    hr_team_id = fields.Many2one(related="employee_id.hr_team_id", store=True)
    hr_child_team_id = fields.Many2one(
        related="employee_id.hr_child_team_id", store=True
    )
