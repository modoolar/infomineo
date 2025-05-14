# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models


class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    same_monthly_ratio = fields.Boolean(compute="_compute_same_monthly_ratio")
    recurrency = fields.Char(compute="_compute_recurrency")
    sale_order_ids = fields.One2many(
        comodel_name="sale.order", compute="_compute_sale_order_count"
    )

    @api.depends("recurring_monthly", "recurring_total")
    def _compute_same_monthly_ratio(self):
        for rec in self:
            rec.same_monthly_ratio = rec.recurring_monthly == rec.recurring_total

    @api.depends("template_id")
    def _compute_recurrency(self):
        for sub in self.filtered(lambda x: x.template_id):
            template = sub.template_id
            period_type = dict(template._fields["recurring_rule_type"].selection).get(
                template.recurring_rule_type
            )
            periods = (
                "for %s%s" % (template.recurring_rule_count, period_type[0].lower())
                if template.recurring_rule_boundary == "limited"
                else "until cancelled"
            )
            sub.recurrency = "Every %s%s %s" % (
                template.recurring_interval,
                period_type[0].lower(),
                periods,
            )

        self.filtered(lambda x: not x.template_id).recurrency = ""

    def wizard_action(self):
        self.ensure_one()

        wiz_lines_vals = self._prepare_wizard_lines()

        wizard = self.env["sale.subscription.wizard"].create(
            {"subscription_id": self.id, "option_lines": wiz_lines_vals}
        )

        xmlid = "sale_subscription.wizard_action"
        wizard_action = self.env["ir.actions.act_window"]._for_xml_id(xmlid)

        wizard_action["res_id"] = wizard.id
        wizard_action["context"] = self.env.context
        return wizard_action

    def _prepare_wizard_lines(self):
        self.ensure_one()

        line_vals = []

        for sub_line in self.recurring_invoice_line_ids:
            line_vals.append(
                (
                    0,
                    0,
                    {
                        "product_id": sub_line.product_id.id,
                        "existing_qty": sub_line.quantity,
                        "quantity": 1,
                        "uom_id": sub_line.product_id.uom_id.id,
                    },
                )
            )

        return line_vals

    def partial_invoice_line(
        self, sale_order, option_line, refund=False, date_from=False
    ):
        new_sol = super().partial_invoice_line(
            sale_order=sale_order,
            option_line=option_line,
            refund=refund,
            date_from=date_from,
        )

        new_sol.price_unit = self.pricelist_id.with_context(
            uom=option_line.uom_id.id
        ).get_product_price(
            option_line.product_id,
            option_line.existing_qty + option_line.quantity,
            False,
        )

        return new_sol
