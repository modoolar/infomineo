# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models
from odoo.tools import formatLang


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_recurring = fields.Boolean(compute="_compute_is_recurring")
    amount_total_net_first_year = fields.Monetary(
        compute="_compute_subscription_amount_all"
    )
    amount_total_gross_first_year = fields.Monetary(
        compute="_compute_subscription_amount_all"
    )
    amount_total_after_first_year = fields.Monetary(
        compute="_compute_subscription_amount_all"
    )
    upsell_subscription_id = fields.Many2one(
        comodel_name="sale.subscription", compute="_compute_upsell_subscription_id"
    )

    @api.depends("order_line.is_recurring")
    def _compute_is_recurring(self):
        for order in self:
            order.is_recurring = any(order.order_line.mapped("is_recurring"))

    @api.depends("order_line.price_total")
    def _compute_subscription_amount_all(self):
        for order in self:
            amount_total_gross_first_year = (
                amount_total_net_first_year
            ) = amount_total_after_first_year = 0.0
            # subtotal_recurring
            for line in order.order_line:
                template = line.product_id.subscription_template_id
                if not line.is_recurring:
                    amount_total_gross_first_year += line.price_total
                    amount_total_net_first_year += line.price_subtotal
                elif line.is_recurring and line.subscription_duration == "limited":
                    amount_total_gross_first_year += (
                        template.recurring_rule_count * line.recurring_tax_monthly
                        if template.recurring_rule_count <= 12
                        else 12 * line.recurring_tax_monthly
                    )
                    amount_total_net_first_year += (
                        template.recurring_rule_count * line.recurring_monthly
                        if template.recurring_rule_count <= 12
                        else 12 * line.recurring_monthly
                    )
                    amount_total_after_first_year += (
                        (template.recurring_rule_count - 12)
                        * line.recurring_tax_monthly
                        if template.recurring_rule_count > 12
                        else 0
                    )
                elif line.is_recurring and line.subscription_duration == "unlimited":
                    amount_total_gross_first_year += 12 * line.recurring_tax_monthly
                    amount_total_net_first_year += 12 * line.recurring_monthly
                    amount_total_after_first_year += (
                        (template.recurring_rule_count - 12)
                        * line.recurring_tax_monthly
                        if template.recurring_rule_count > 12
                        else 0
                    )
            order.update(
                {
                    "amount_total_gross_first_year": amount_total_gross_first_year,
                    "amount_total_net_first_year": amount_total_net_first_year,
                    "amount_total_after_first_year": amount_total_after_first_year,
                }
            )

    def _compute_upsell_subscription_id(self):
        for sale in self:
            subscription_id = sale.filtered(
                lambda x: x.is_recurring and x.subscription_management == "upsell"
            ).mapped("order_line.subscription_id")
            sale.upsell_subscription_id = (
                subscription_id if subscription_id else self.env["sale.subscription"]
            )

    def _prepare_subscription_total_values(self):
        return {
            "amount_total_net_first_year": formatLang(
                self.env,
                self.amount_total_net_first_year,
                currency_obj=self.currency_id,
            ),
            "amount_total_gross_first_year": formatLang(
                self.env,
                self.amount_total_gross_first_year,
                currency_obj=self.currency_id,
            ),
            "amount_total_after_first_year": formatLang(
                self.env,
                self.amount_total_after_first_year,
                currency_obj=self.currency_id,
            ),
            "is_recurring": self.is_recurring,
            "subscription_management": self.subscription_management,
        }

    def update_existing_subscriptions(self):
        res = super().update_existing_subscriptions()

        subscriptions_lines = self.order_line.mapped(
            "subscription_id.recurring_invoice_line_ids"
        ).sudo()
        for subscriptions_line in subscriptions_lines:
            subscriptions_line.onchange_product_quantity()
        return res

    def use_existing_project(self):
        """
        Instead of creating a new project from an upsell Sale Order,
        we will use the existing one if the configuration is set that way.
        :return:
        """
        self.ensure_one()
        upsell_existing_project = self.env["ir.config_parameter"].get_param(
            "subscription_improvements.upsell_existing_project", False
        )
        return (
            bool(upsell_existing_project) and self.subscription_management == "upsell"
        )
