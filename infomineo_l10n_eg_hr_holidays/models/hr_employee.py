# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)


from dateutil.relativedelta import relativedelta

from odoo import models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _get_vals_for_automated_leave_allocation(self, leave_type):
        self.ensure_one()
        vals = super()._get_vals_for_automated_leave_allocation(leave_type)
        allocation_type = vals.get("allocation_type", False)
        is_not_accrual = allocation_type and allocation_type != "accrual"
        is_egypt = self.company_country_code == "EG"
        if is_not_accrual and is_egypt:
            vals["date_to"] = self.first_contract_date + relativedelta(years=3)
        return vals
