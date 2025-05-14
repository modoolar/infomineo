# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)


from odoo import fields, models


class HRLeaveType(models.Model):
    _inherit = "hr.leave.type"

    def get_employees_days(self, employee_ids, date=None):
        if self.env.context.get("test_date_from", False):
            date = fields.Date.to_date(self.env.context.get("test_date_from"))
        return super().get_employees_days(employee_ids, date)
