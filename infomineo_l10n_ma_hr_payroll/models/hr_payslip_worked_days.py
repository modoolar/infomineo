# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models


class HrPayslipWorkedDays(models.Model):
    _inherit = "hr.payslip.worked_days"

    number_of_days = fields.Float(default=lambda x: x._get_default_number_of_days())

    @api.model
    def _get_default_number_of_days(self):
        country_id = self.env.context.get("country_id")

        return (
            26
            if country_id and self.env["res.country"].browse(country_id).code == "MA"
            else 30
        )
