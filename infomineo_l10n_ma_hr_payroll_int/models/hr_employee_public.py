from odoo import fields, models, api


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    start_date = fields.Date(related='employee_id.start_date', readonly=True)