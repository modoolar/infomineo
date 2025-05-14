# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class HREmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    cumul_jours_travailles_pdf = fields.Integer(
        string="Cumul Jours Travailles", readonly=True
    )
    cumul_brut_pdf = fields.Float(string="Cumul BRUT", readonly=True)
    cumul_brut_imposable_pdf = fields.Float(
        string="Cumul BRUT Imposable", readonly=True
    )
    cumul_net_imposable_pdf = fields.Float(string="Cumul NET Imposable", readonly=True)
    cumul_ir_pdf = fields.Float(string="Cumul IR", readonly=True)
