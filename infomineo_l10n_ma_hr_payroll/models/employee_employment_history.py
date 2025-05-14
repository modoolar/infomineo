# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models

from odoo.addons.infomineo_hr_contract.models.employee_employment_history import (
    EMPLOYEE_HISTORY_FIELDS,
)

EMPLOYEE_HISTORY_FIELDS["hr.contract"].append("gross_wage")


class EmployeeEmploymentHistory(models.Model):
    _inherit = "employee.employment.history"

    gross_wage = fields.Monetary(groups="hr.group_hr_manager")

    @api.model
    def get_custom_fields(self):
        values = super().get_custom_fields()
        values.append("gross_wage")

        return values
