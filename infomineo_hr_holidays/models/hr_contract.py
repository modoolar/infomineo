# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, models


class HrContract(models.Model):
    _inherit = "hr.contract"

    @api.onchange("state")
    def _process_automated_leave_allocation(self):
        if self.state == "open":
            self.employee_id._create_automated_leave_allocation()
            self.employee_id._process_allocations()
        if self.state in ["cancel", "close"]:
            self.employee_id._delete_automated_leave_allocation()
