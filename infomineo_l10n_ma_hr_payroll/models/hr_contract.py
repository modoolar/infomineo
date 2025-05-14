# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class Contract(models.Model):
    _inherit = "hr.contract"

    per_employer = fields.Float()
    per_salary = fields.Float()
    meal_allowance = fields.Float()
    representation_allowance = fields.Float()
    merit_bonus = fields.Float(string="Primes de merite")
    gross_wage = fields.Monetary()
