# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _prepare_line_values(self, line, account_id, date, debit, credit):
        result = super(HrPayslip, self)._prepare_line_values(
            line, account_id, date, debit, credit
        )
        result["department_id"] = line.employee_id.department_id.id
        return result
