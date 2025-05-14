# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    housing_type = fields.Selection(
        selection=[("normal", "Normal"), ("social", "Social")],
        groups="hr.group_hr_user",
    )
    housing_surface = fields.Float(string="Surface(m²)", groups="hr.group_hr_user")
    buying_price = fields.Float(groups="hr.group_hr_user")
    abatement_fr_housing = fields.Float(groups="hr.group_hr_user")
    cumul_jours_travailles_pdf = fields.Integer(string="Cumul Jours Travailles")
    cumul_brut_pdf = fields.Float(string="Cumul BRUT")
    cumul_brut_imposable_pdf = fields.Float(string="Cumul BRUT Imposable")
    cumul_net_imposable_pdf = fields.Float(string="Cumul NET Imposable")
    cumul_ir_pdf = fields.Float(string="Cumul IR")
    gross_wage = fields.Monetary(
        related="current_contract_id.gross_wage", groups="hr.group_hr_user"
    )
