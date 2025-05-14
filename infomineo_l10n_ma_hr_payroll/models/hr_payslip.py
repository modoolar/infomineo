# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_worked_day_lines_values(self, domain=None):
        res = super()._get_worked_day_lines_values(domain=domain)
        res_worked_entries = [
            item
            for item in res
            if self._get_working_work_entry_type(item.get("work_entry_type_id", False))
        ]
        for line in res_worked_entries:
            country = self.contract_id.structure_type_id.country_id
            line["number_of_days"] = 26 if country and country.code == "MA" else 30

        return res_worked_entries

    def _get_working_work_entry_type(self, entry_id):
        return self.env["hr.work.entry.type"].browse(entry_id).code == "WORK100"
