# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models

from odoo.addons.sale_subscription.models.sale_subscription import INTERVAL_FACTOR


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    is_recurring = fields.Boolean(related="product_id.recurring_invoice")
    subscription_duration = fields.Selection(
        related="product_id.subscription_template_id.recurring_rule_boundary"
    )
    recurrency = fields.Char(compute="_compute_recurrency", store=True)
    subtotal_recurring = fields.Monetary(compute="_compute_recurrency", store=True)
    recurring_monthly = fields.Float(
        compute="_compute_recurrency",
        string="Monthly Recurring Revenue",
        digits=(16, 5),
        store=True,
    )
    recurring_tax_monthly = fields.Float(
        compute="_compute_recurrency",
        string="Monthly Recurring Revenue",
        digits=(16, 5),
        store=True,
    )

    @api.depends("product_id", "price_total")
    def _compute_recurrency(self):
        for sol in self.filtered(lambda x: x.is_recurring):
            template = sol.product_id.subscription_template_id
            period_type = dict(template._fields["recurring_rule_type"].selection).get(
                template.recurring_rule_type
            )
            periods = (
                "for %s%s" % (template.recurring_rule_count, period_type[0].lower())
                if template.recurring_rule_boundary == "limited"
                else "until cancelled"
            )

            ratio = (
                INTERVAL_FACTOR[template.recurring_rule_type]
                / template.recurring_interval
            )

            sol.update(
                {
                    "recurring_monthly": sol.price_subtotal * ratio if template else 0,
                    "recurring_tax_monthly": sol.price_total * ratio if template else 0,
                    "recurrency": "Every %s%s %s"
                    % (template.recurring_interval, period_type[0].lower(), periods),
                    "subtotal_recurring": sol.price_subtotal
                    * template.recurring_rule_count
                    / template.recurring_interval,
                }
            )

        self.filtered(lambda x: not x.is_recurring).update(
            {
                "recurrency": "One time payment",
                "subtotal_recurring": 0,
                "recurring_monthly": 0,
            }
        )

    def _timesheet_service_generation(self):
        for sol in self.filtered(lambda x: x.order_id.use_existing_project()):
            sol.link_to_existing_project()

        return super()._timesheet_service_generation()

    def link_to_existing_project(self):
        self.ensure_one()

        first_so = self.subscription_id.sale_order_ids.filtered(
            lambda x: x.subscription_management == "create"
        )
        matching_line = first_so.order_line.filtered(
            lambda x: x.product_id == self.product_id
        )
        if matching_line:
            self.project_id = (
                matching_line.project_id
                if matching_line.project_id
                else self.env["project.project"]
            )
