from odoo import fields, models, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    start_date = fields.Date('Start Date', compute='_compute_start_date', store=True)

    @api.depends('contract_ids', 'contract_ids.date_start')
    def _compute_start_date(self):
        for r in self:
            if r.contract_ids:
                contracts = r.contract_ids.sorted(key=lambda r: r.create_date)
                first_contract_id = contracts[0]

                r.start_date = first_contract_id.date_start
            else:
                r.start_date = None