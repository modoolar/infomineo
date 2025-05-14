# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import json

from odoo import api

from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale_subscription.models.sale_order import SaleOrderLine
from odoo.addons.sale_subscription.models.sale_subscription import SaleSubscription


def are_we_in_test_mode():
    from odoo.tools import config

    return config.get("test_enable") or config.get("test_file")


@api.depends(
    "order_line.tax_id", "order_line.price_unit", "amount_total", "amount_untaxed"
)
def _compute_tax_totals_json(self):
    def compute_taxes(order_line):
        price = order_line.price_unit * (1 - (order_line.discount or 0.0) / 100.0)
        order = order_line.order_id
        return order_line.tax_id._origin.compute_all(
            price,
            order.currency_id,
            order_line.product_uom_qty,
            product=order_line.product_id,
            partner=order.partner_shipping_id,
        )

    account_move = self.env["account.move"]
    for order in self:
        tax_lines_data = account_move._prepare_tax_lines_data_for_totals_from_object(
            order.order_line, compute_taxes
        )
        tax_totals = account_move._get_tax_totals(
            order.partner_id,
            tax_lines_data,
            order.amount_total,
            order.amount_untaxed,
            order.currency_id,
        )
        tax_totals.update(order._prepare_subscription_total_values())
        order.tax_totals_json = json.dumps(tax_totals)


def _update_subscription_line_data(self, subscription):
    """Prepare a dictionnary of values to add or update lines on a subscription."""
    values = list()
    dict_changes = dict()
    for line in self:
        sub_line = subscription.recurring_invoice_line_ids.filtered(
            lambda l: (l.product_id, l.uom_id) == (line.product_id, line.product_uom)
        )
        if sub_line:
            # We have already a subscription line, we need to modify the product quantity
            if len(sub_line) > 1:
                # we are in an ambiguous case
                # to avoid adding information to a random line,
                # in that case we create a new line
                # we can simply duplicate an arbitrary line to that effect
                sub_line[0].copy(
                    {"name": line.display_name, "quantity": line.product_uom_qty}
                )
            else:
                dict_changes.setdefault(sub_line.id, sub_line.quantity)
                # upsell, we add the product to the existing quantity
                dict_changes[sub_line.id] += line.product_uom_qty
        else:
            # we create a new line in the subscription: (0, 0, values)
            values.append(line._prepare_subscription_line_data()[0])

    values += [
        (1, sub_id, {"quantity": dict_changes[sub_id]}) for sub_id in dict_changes
    ]
    return values


def _compute_sale_order_count(self):
    sol = self.env["sale.order.line"]
    if sol.check_access_rights("read", raise_exception=False):
        raw_data = sol.read_group(
            [("subscription_id", "in", self.ids)],
            ["subscription_id", "sale_ids:array_agg(order_id)"],
            ["subscription_id"],
            lazy=False,
        )
        mapped_data = {
            data["subscription_id"][0]: data["sale_ids"] for data in raw_data
        }
    else:
        mapped_data = dict()

    for subscription in self:
        subscription.sale_order_count = (
            len(mapped_data[subscription.id]) if subscription.id in mapped_data else 0
        )
        subscription.sale_order_ids = (
            mapped_data[subscription.id]
            if subscription.id in mapped_data
            else self.env["sale.order"]
        )


def post_load():
    if not are_we_in_test_mode():
        SaleOrder._patch_method("_compute_tax_totals_json", _compute_tax_totals_json)
    SaleOrderLine._patch_method(
        "_update_subscription_line_data", _update_subscription_line_data
    )
    SaleSubscription._patch_method(
        "_compute_sale_order_count", _compute_sale_order_count
    )
