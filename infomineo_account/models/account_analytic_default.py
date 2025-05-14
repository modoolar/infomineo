# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountAnalyticDefault(models.Model):
    _inherit = "account.analytic.default"

    department_id = fields.Many2one(comodel_name="hr.department", string="Department")
