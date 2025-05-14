# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models

from odoo.addons.infomineo_hr.models.employee_employment_history import (
    EMPLOYEE_HISTORY_FIELDS,
)

EMPLOYEE_HISTORY_FIELDS.update(
    {
        "hr.contract": [
            "employee_id",
            "wage",
        ]
    }
)
EMPLOYEE_HISTORY_FIELDS["hr.employee"].append("current_contract_id")


class EmployeeEmploymentHistory(models.Model):
    _inherit = "employee.employment.history"

    currency_id = fields.Many2one(
        comodel_name="res.currency",
        related="company_id.currency_id",
        groups="hr.group_hr_manager",
    )
    current_contract_id = fields.Many2one(
        string="Contract",
        comodel_name="hr.contract",
        groups="hr.group_hr_manager",
    )
    wage = fields.Monetary(groups="hr.group_hr_manager")

    @api.model
    def get_custom_fields(self):
        values = super().get_custom_fields()
        values.extend(["current_contract_id", "wage"])

        return values
