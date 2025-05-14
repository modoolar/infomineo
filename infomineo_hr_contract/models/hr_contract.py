# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .employee_employment_history import EMPLOYEE_HISTORY_FIELDS


class Contract(models.Model):
    _inherit = "hr.contract"

    _FREELANCE_ALLOWED_STATES = ["draft", "cancel"]

    work_permit_number = fields.Char()
    work_permit_expiry_date = fields.Date()
    residency_number = fields.Char()
    residency_expiry_date = fields.Date()
    is_freelance = fields.Boolean(compute="_compute_is_freelance", store=True)

    gross_medical_allowance = fields.Monetary()

    transportation_allowance = fields.Monetary(string="Transportation Allowance")
    other_allowances = fields.Monetary(string="Other Allowances")

    @api.constrains("employee_id", "state")
    def _check_freelance_contract_state(self):
        for contract in self:
            self._freelance_contract_state_validation(
                contract.employee_id, contract.state
            )

    @api.onchange("state", "employee_id")
    def _onchange_state_employee_id(self):
        self._freelance_contract_state_validation(self.employee_id, self.state)

    @api.depends("employee_id.employee_type")
    def _compute_is_freelance(self):
        for contract in self:
            contract.is_freelance = (
                contract.employee_id
                and contract.employee_id.employee_type == "freelance"
            )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for rec in result:
            rec._create_employee_history()

        return result

    def write(self, vals):
        employees = self.env["hr.employee"].browse(
            vals.get("employee_id")
        ) or self.mapped("employee_id")
        self._freelance_contract_state_validation(employees, vals.get("state", ""))

        employees_list = []
        running_contracts = self.filtered(
            lambda x: x.state == "open" and x.employee_id.current_contract_id == x
        )
        if "employee_id" in vals:
            for rec in running_contracts:
                employees_list.append(rec.employee_id)

        res = super().write(vals)

        for rec in running_contracts:
            rec._create_employee_history(vals, employees_list)

        return res

    @api.model
    def _freelance_contract_state_validation(self, employees, state):
        if not (state and employees) or state in self._FREELANCE_ALLOWED_STATES:
            return

        if any(employee.employee_type == "freelance" for employee in employees):
            err_msg = _("State '{state}' is not allowed for freelance contracts.")
            raise UserError(err_msg.format(state=state))

    def _create_employee_history(self, vals=None, employees_list=None):
        if employees_list is None:
            employees_list = list()
        self.ensure_one()

        model_name = self._name
        if model_name not in EMPLOYEE_HISTORY_FIELDS.keys():
            return

        for old_employee in employees_list:
            old_employee._create_employee_history()

        if (not vals and self.employee_id) or any(
            item in EMPLOYEE_HISTORY_FIELDS[model_name] for item in vals
        ):
            self.employee_id._create_employee_history()
