# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    cin = fields.Char(
        string="CIN",
        help="National ID or Resident Card City",
        groups="hr.group_hr_manager",
    )
