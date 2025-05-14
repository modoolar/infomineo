# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class HrContractEmployeeReport(models.Model):
    _inherit = "hr.contract.employee.report"

    job_title = fields.Char(readonly=True)
    mobile_phone = fields.Char(group_operator="max", readonly=True)
    parent_id = fields.Many2one("hr.employee", "Manager", readonly=True)
    departure_date = fields.Char(group_operator="max", readonly=True)
    first_contract_date = fields.Char(group_operator="max", readonly=True)

    def _query(self, fields="", from_clause="", outer=""):
        fields += """
            , e.job_title AS job_title
            , e.mobile_phone AS mobile_phone
            , e.departure_date AS departure_date
            , e.first_contract_date AS first_contract_date
            , e.parent_id AS parent_id"""

        return super()._query(fields, from_clause, outer)
