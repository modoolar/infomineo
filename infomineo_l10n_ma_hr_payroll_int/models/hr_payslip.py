from odoo import fields, models, api


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    start_date = fields.Date(string='Start Date', compute='_compute_start_date')

    @api.depends('employee_id')
    def _compute_start_date(self):
        for r in self:
            if r.employee_id:
                r.start_date = r.employee_id.start_date
                print('testtt')
            else:
                r.start_date = None
                print('heeey')
