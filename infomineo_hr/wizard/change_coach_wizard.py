# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ChangeCoachWizard(models.TransientModel):
    _name = "change.coach.wizard"
    _description = "Change Coach Wizard"

    user_id = fields.Many2one(
        comodel_name="res.users",
        string="PDC",
        domain="[('employee_ids', '!=', False)]",
    )

    manager_id = fields.Many2one(
        comodel_name="res.users",
        string="Manager",
        domain="[('employee_ids', '!=', False)]",
    )

    def change_coach(self):
        active_id = self._context.get("active_id")
        employee = self.env["hr.employee"].browse(active_id)
        coach_id = manager_id = self.env["hr.employee"]

        if self.user_id:
            coach_id = self.sudo().user_id.employee_id.search(
                [("user_id", "=", self.user_id.id)]
            )

        if self.manager_id:
            manager_id = self.sudo().user_id.employee_id.search(
                [("user_id", "=", self.manager_id.id)]
            )

        if coach_id and coach_id != employee.coach_id:
            employee.sudo().write({"coach_id": coach_id.id})

        if manager_id and manager_id != employee.parent_id:
            employee.sudo().write({"parent_id": manager_id.id})
            if manager_id.user_id != employee.expense_manager_id:
                employee.sudo().write({"expense_manager_id": manager_id.user_id.id})

            if manager_id.user_id != employee.timesheet_manager_id:
                employee.sudo().write({"timesheet_manager_id": manager_id.user_id.id})

            if manager_id.user_id != employee.approval_manager_id:
                employee.sudo().write({"approval_manager_id": manager_id.user_id.id})
