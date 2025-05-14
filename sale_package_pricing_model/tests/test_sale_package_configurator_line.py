# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.tests import TransactionCase


class TestSalePackageConfiguratorLine(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super(TestSalePackageConfiguratorLine, cls).setUpClass()

        cls.new_config_line = cls.init_package_config_line()

    @classmethod
    def init_package_config_line(cls):
        # The new line will have value of 10 points per 200 words
        return cls.env.ref(
            "sale_package_pricing_model.sale_package_configurator_line_translation"
        )

    def test_new_line_valid_ratio(self):
        """
        We've are testing if the new config line has a ratio of 0.05
        """

        self.assertEqual(self.new_config_line.consumption_ratio, 0.05)

    def test_new_line_zero_ratio(self):
        """
        We've are testing if the new config line has a ratio of 0
        if we put rate of 0 (division by 0 case)
        """
        self.new_config_line.consumption_rate = 0

        self.assertEqual(self.new_config_line.consumption_ratio, 0)
