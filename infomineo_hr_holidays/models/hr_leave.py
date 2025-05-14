# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class HRLeave(models.Model):
    _inherit = "hr.leave"

    hr_team_id = fields.Many2one(related="employee_id.hr_team_id", store=True)

    @api.depends("state", "employee_id", "department_id")
    def _compute_can_approve(self):
        super()._compute_can_approve()
        for holiday in self:
            holiday.can_approve = holiday._can_approve_or_refuse()

    def action_approve(self):
        if any(not record._can_approve_or_refuse() for record in self):
            raise UserError(_("You must be Time off Manager to approve this leave."))
        return super().action_approve()

    def action_validate(self):
        current_user = self.env.user
        if current_user.has_group("hr_holidays.group_hr_holidays_manager") or not self:
            return super().action_validate()
        raise UserError(_("You must be the Time Off Manager to validate this leave."))

    def _can_approve_or_refuse(self):
        current_user = self.env.user
        if current_user.has_group("hr_holidays.group_hr_holidays_manager"):
            return True

        if current_user.id == self.employee_id.leave_manager_id.id:
            return True

        if current_user.employee_id.id == self.employee_id.id:
            return False

        return current_user.employee_id.hr_team_id == self.employee_id.hr_team_id

    def action_refuse(self):
        if any(not record._can_approve_or_refuse() for record in self):
            raise UserError(_("You must be Time off Manager to refuse this leave."))
        return super().action_refuse()
