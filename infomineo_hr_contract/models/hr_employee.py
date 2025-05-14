# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from functools import reduce

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    permit_no = fields.Char(
        compute="_compute_longest_contract_info", groups="hr.group_hr_manager"
    )
    work_permit_expiration_date = fields.Date(
        compute="_compute_longest_contract_info",
        groups="hr.group_hr_manager",
        store=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency", related="company_id.currency_id", readonly=True
    )
    current_contract_id = fields.Many2one(
        comodel_name="hr.contract",
        compute="_compute_current_contract_id",
        store=True,
        groups="hr.group_hr_user",
    )
    wage = fields.Monetary(
        related="current_contract_id.wage", readonly=True, groups="hr.group_hr_user"
    )
    residency_number = fields.Char(related="contract_id.residency_number")
    residency_expiry_date = fields.Date(related="contract_id.residency_expiry_date")

    @api.depends(
        "contract_ids.work_permit_number",
        "contract_ids.work_permit_expiry_date",
        "contract_ids.state",
    )
    def _compute_longest_contract_info(self):
        for employee in self:
            longest_contract = employee.contract_ids.filtered(
                lambda x: x.state == "open" and x.work_permit_expiry_date
            )

            sorted_longest_contract = sorted(
                longest_contract, key=lambda x: x.work_permit_expiry_date, reverse=True
            )
            permit_no = ""
            work_permit_expiration_date = False

            if sorted_longest_contract:
                permit_no = sorted_longest_contract[0].work_permit_number
                work_permit_expiration_date = sorted_longest_contract[
                    0
                ].work_permit_expiry_date

            employee.permit_no = permit_no
            employee.work_permit_expiration_date = work_permit_expiration_date

    @api.depends("contract_ids.state")
    def _compute_current_contract_id(self):
        for employee in self:
            contracts = employee._get_first_contracts()
            if contracts:
                employee.current_contract_id = reduce(
                    lambda x, y: x if x.date_start < y.date_start else y,
                    self.env["hr.contract"].search([("employee_id", "=", employee.id)]),
                )
            else:
                employee.current_contract_id = False

    def write(self, vals):
        if "job_id" in vals:
            for rec in self:
                rec.current_contract_id.job_id = vals["job_id"]
        return super().write(vals)

    @api.depends("job_id")
    def _compute_job_title(self):
        ret = super()._compute_job_title()
        for rec in self:
            rec.job_title = "" if not rec.job_id else rec.job_id.name
        return ret
