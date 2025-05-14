# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrDepartureWizard(models.TransientModel):
    _inherit = "hr.departure.wizard"

    probability_of_rehire = fields.Float()

    @api.constrains("probability_of_rehire")
    def _check_probability_of_rehire(self):
        if self.probability_of_rehire > 1 or self.probability_of_rehire < 0:
            raise ValidationError(_("Enter Value Between 0-100."))

    def action_register_departure(self):
        self.employee_id.probability_of_rehire = self.probability_of_rehire
        super().action_register_departure()
