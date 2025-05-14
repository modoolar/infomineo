# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import SUPERUSER_ID
from odoo.http import request, route

from odoo.addons.hr_payroll.controllers.main import HrPayroll as HrPayrollMA


class HrPayroll(HrPayrollMA):
    @route(["/print/payslips"], type="http", auth="user")
    def get_payroll_report_print(self, list_ids="", **post):
        request.uid = SUPERUSER_ID

        return super().get_payroll_report_print(list_ids, **post)
