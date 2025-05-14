# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    order_type = fields.Selection(
        selection_add=[
            ("package", "Package"),
        ],
        ondelete={
            "package": "set default",
        },
    )
    package_duration = fields.Integer(
        string="Package Duration (Months)", help="Package Duration in Months"
    )
    package_size = fields.Integer(
        string="Package Size (Points)",
        help="Number of Points that goes into the Package",
    )
    package_configuration_id = fields.Many2one(
        comodel_name="sale.package.configurator", index=True
    )
    package_configurator_line_ids = fields.One2many(
        related="package_configuration_id.package_configurator_line_ids",
    )

    @api.model_create_multi
    def create(self, vals_list):
        self._validate_package_configuration(vals_list)

        return super().create(vals_list)

    def write(self, vals):
        self._validate_package_configuration([vals])

        return super().write(vals)

    def _validate_package_configuration(self, vals_list):
        if any(
            vals
            for vals in vals_list
            if self.is_type_package(vals) and not self.has_package_configuration(vals)
        ):
            raise ValidationError(_("You need to specify the package configuration."))

    def is_type_package(self, vals=None):
        return self.check_field_validity("order_type", valid_value="package", vals=vals)

    def has_package_configuration(self, vals=None):
        return self.check_field_validity("package_configuration_id", vals=vals)
