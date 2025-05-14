# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class HREmployee(models.Model):
    _inherit = "hr.employee"

    @api.depends(
        "contract_ids.work_permit_number",
        "contract_ids.work_permit_expiry_date",
        "contract_ids.state",
    )
    def _compute_longest_contract_info(self):
        """
        Skip computation in test mode in order to pass Odoo tests for
        work entries generation performance (test_work_entries_generation_perf)
        :return:
        """
        for employee in self:
            employee.permit_no = ""
            employee.work_permit_expiration_date = False
