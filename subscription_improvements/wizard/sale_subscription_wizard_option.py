# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class SaleSubscriptionWizardOption(models.TransientModel):
    _inherit = "sale.subscription.wizard.option"

    sub_template_id = fields.Many2one(related="wizard_id.subscription_id.template_id")
    existing_qty = fields.Float()
