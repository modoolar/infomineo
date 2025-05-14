# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    sale_order_template_id = fields.Many2one(
        default=lambda x: x._get_default_sale_order_template_id()
    )
    order_type = fields.Selection(
        selection_add=[
            ("package", "Package"),
        ],
        ondelete={
            "package": "set default",
        },
    )
    package_expiry_datetime = fields.Datetime(string="Package Expiry Date")
    package_size = fields.Integer()
    consumed_points_count = fields.Float(compute="_compute_consumed_points_count")

    @api.onchange("sale_order_template_id")
    def _onchange_sale_order_template_id(self):
        res = super()._onchange_sale_order_template_id()
        self.package_size = self.sale_order_template_id.package_size

        return res

    def _get_default_sale_order_template_id(self):
        return self.env.ref(
            "sale_package_pricing_model.sale_order_template_empty_default", False
        )

    def action_confirm(self):
        values = self._prepare_confirmation_values()
        for rec in self.filtered(lambda x: x.order_type == "package"):
            rec.package_expiry_datetime = rec._calculate_package_expiry_datetime(
                values.get("date_order")
            )

        return super().action_confirm()

    def _calculate_package_expiry_datetime(self, date_order):
        """
        This method calculates package expiry by taking Order Date
        and adding `package_duration` value from SO Template
        :return: Datetime of a package expiration.
        """
        package_duration = self.sale_order_template_id.package_duration or 0

        return (
            date_order + relativedelta(months=package_duration) if date_order else False
        )

    @api.depends("order_line.consumed_points")
    def _compute_consumed_points_count(self):
        order_lines = self.env["sale.order.line"].read_group(
            [("order_id", "in", self.ids)],
            ["order_id", "consumed_points"],
            ["order_id"],
        )
        amounts = {line["order_id"][0]: line["consumed_points"] for line in order_lines}
        for rec in self:
            rec.consumed_points_count = amounts.get(rec.id, 0)

    def action_show_points(self):
        """
        Button which will be used by other modules to show some view/s
        on which the user can see how the points were spent by showing
        all related models which have spent the points.
        """
