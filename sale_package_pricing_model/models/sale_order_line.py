# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    consumed_points = fields.Float(compute="_compute_consumed_points", store=True)

    def _compute_consumed_points(self):
        self.consumed_points = 0

    @api.constrains("product_id")
    def _package_product_constrains(self):
        """
        There can be only one SOL on SO product of type `package`.
        """

        for sol in self:
            if len(sol.order_id.order_line.filtered(lambda x: x.is_package())) > 1:
                raise ValidationError(
                    _("You can only have one package product per Sale Order.")
                )

    def is_package(self):
        """
        Checks whether the line has a product of type `package`.
        """
        self.ensure_one()

        return self.product_id.product_tmpl_id.is_package
