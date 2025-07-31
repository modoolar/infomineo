from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _compute_hr_fields_readonly(self):
        return not (
                self.user.has_group("hr.group_hr_manager")
        )

    # def _group_hr_expense_user_domain(self):
    #     super()._group_hr_expense_user_domain()

    parent_id = fields.Many2one(readonly=_compute_hr_fields_readonly)
    coach_id = fields.Many2one(readonly=_compute_hr_fields_readonly)
    expense_manager_id =fields.Many2one(readonly=_compute_hr_fields_readonly)

    leave_manager_id = fields.Many2one(readonly=_compute_hr_fields_readonly)
    timesheet_manager_id = fields.Many2one(readonly=_compute_hr_fields_readonly)
    approval_manager_id = fields.Many2one(readonly=_compute_hr_fields_readonly)

