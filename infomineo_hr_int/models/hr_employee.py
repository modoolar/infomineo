from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.onchange('job_id')
    def update_contract_job_position(self):
        for employee in self:
            if employee.contract_id:
                employee.contract_id.job_id = employee.job_id