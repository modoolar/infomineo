# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from freezegun import freeze_time

from odoo import fields
from odoo.tests import Form, TransactionCase


class TestSaleOrder(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrder, cls).setUpClass()

        cls.so_template = cls.env.ref(
            "sale_package_pricing_model.sale_order_template_package"
        )
        cls.partner = cls.env.ref("base.res_partner_1")

        cls.order = cls.init_sale_order(cls.partner)

    @classmethod
    def init_sale_order(cls, partner):
        with Form(
            cls.env["sale.order"].with_context(default_partner_id=partner.id)
        ) as form:
            form.sale_order_template_id = cls.env.ref(
                "sale_package_pricing_model.sale_order_template_package"
            )
            with form.order_line.new() as line:
                line.product_id = cls.env.ref("product.product_order_01")
                line.product_uom_qty = 1
            return form.save()

    def test_expiry_date(self):
        """
        Validating that the expiry date is being calculated when SO is confirmed
        by taking the order date and adding duration from the package config.
        """

        # We will validate this date plus 12 months which is the value
        # written on the `sale_order_template_package`
        with freeze_time("2021-11-10 23:30:00"):
            self.order.action_confirm()

            # Valid expiry date value
            self.assertEqual(
                fields.Datetime.to_string(self.order.package_expiry_datetime),
                "2022-11-10 23:30:00",
                "Expiry date isn't valid.",
            )
