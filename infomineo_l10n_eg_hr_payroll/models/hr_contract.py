# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class HRContract(models.Model):
    _inherit = "hr.contract"

    l10n_eg_housing_allowance = fields.Monetary(string="Housing Allowance")
    l10n_eg_language_allowance = fields.Monetary(string="Langauge Allowance")
    insured_salary = fields.Float()
    contract_exchange_rate = fields.Float()
    show_contract_exchange_rate = fields.Boolean(
        related="company_id.show_contract_exchange_rate"
    )
