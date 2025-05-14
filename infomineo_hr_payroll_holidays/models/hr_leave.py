# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains("date_from", "date_to", "employee_id")
    def _check_payslip_generated(self):
        if not self.env.user.has_group("base.group_user"):
            return super(HrLeave, self)._check_payslip_generated()
