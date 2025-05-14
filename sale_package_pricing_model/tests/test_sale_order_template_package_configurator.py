# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.exceptions import ValidationError
from odoo.tests import TransactionCase


class TestSaleOrderTemplatePackageConfigurator(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSaleOrderTemplatePackageConfigurator, cls).setUpClass()

    def test_type_package(self):
        """
        We're testing that SO Template of type `package` will
        trigger validation for a required `package_configuration_id` field.
        We need to check create and write of an existing Template.
        """

        # We will create a new SO Template of type `package` with no
        # package_configuration on it.

        template_values = self._prepare_so_template_wo_package_configuration_values()
        with self.assertRaisesRegex(
            ValidationError, "You need to specify the package configuration."
        ):
            self.env["sale.order.template"].create(template_values)

        package_configuration = self.env.ref(
            "sale_package_pricing_model.sale_package_configurator_1"
        )
        template_values["package_configuration_id"] = package_configuration.id

        self.new_so_template_1 = self.env["sale.order.template"].create(template_values)

        # Removing package_configuration and setting order_type to `other`
        self.new_so_template_1.write(
            {
                "package_configuration_id": False,
                "order_type": "other",
            }
        )

        # Setting order_type to `package` to see if it will raise the
        # package_configuration_id missing error

        with self.assertRaisesRegex(
            ValidationError, "You need to specify the package configuration."
        ):
            self.env["sale.order.template"].write(
                {
                    "order_type": "package",
                }
            )

    def _prepare_so_template_wo_package_configuration_values(self):
        return {
            "name": "SO Template Test 2",
            "order_type": "package",
            "package_duration": 24,
            "package_size": 1000,
        }
