# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class SalePackageConfiguratorLine(models.Model):
    _name = "sale.package.configurator.line"
    _description = "Sale Package Configurator Line"
    _order = "package_line_of_business"
    _rec_name = "package_line_of_business"

    sale_package_configurator_id = fields.Many2one(
        comodel_name="sale.package.configurator", index=True, required=True
    )
    package_line_of_business = fields.Selection(
        selection=[
            ("other", "Other"),
        ],
        default="other",
        index=True,
        required=True,
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
