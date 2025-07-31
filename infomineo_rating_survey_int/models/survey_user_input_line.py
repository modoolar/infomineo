from odoo import api, fields, models


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    category_id = fields.Many2many(
        'res.partner.category',
        string='Tags',
        compute='_compute_category_id',
        inverse='_inverse_category_id',
        store=False
    )

    def _compute_category_id(self):
        for record in self:
            record.category_id = record.partner_id.category_id if record else False

    def _inverse_category_id(self):
        for record in self:
            if record.partner_id:
                record.partner_id.category_id = record.category_id


