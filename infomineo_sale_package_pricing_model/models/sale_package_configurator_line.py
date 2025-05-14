# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class SalePackageConfiguratorLine(models.Model):
    _inherit = "sale.package.configurator.line"

    package_line_of_business = fields.Selection(
        selection_add=[
            ("translation", "Translation"),
            ("business_research", "Business Research"),
            ("expert_network", "Expert Network"),
            ("graphic_design", "Graphic Design"),
            ("management", "Management"),
        ],
        ondelete={
            "translation": "set default",
            "business_research": "set default",
            "expert_network": "set default",
            "graphic_design": "set default",
            "management": "set default",
        },
    )
    consumption_rate = fields.Integer(required=True)
    consumption_points = fields.Integer(required=True)
    consumption_ratio = fields.Float(compute="_compute_consumption_ratio", store=True)
    reference_uom = fields.Selection(
        selection=[
            ("hours", "Hours"),
            ("words", "Words"),
        ],
        required=True,
    )

    @api.depends("consumption_points", "consumption_rate")
    def _compute_consumption_ratio(self):
        for rec in self:
            if rec.consumption_rate == 0:
                rec.consumption_ratio = 0
            else:
                rec.consumption_ratio = rec.consumption_points / rec.consumption_rate
