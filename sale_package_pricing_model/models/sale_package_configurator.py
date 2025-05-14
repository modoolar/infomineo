# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
import collections

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SalePackageConfigurator(models.Model):
    _name = "sale.package.configurator"
    _description = "Sale Package Configurator"

    name = fields.Char(required=True)
    package_configurator_line_ids = fields.One2many(
        comodel_name="sale.package.configurator.line",
        inverse_name="sale_package_configurator_id",
    )

    @api.constrains("package_configurator_line_ids")
    def _constrains_package_line_of_business(self):
        for rec in self:
            lob_occurences = collections.Counter(
                rec.package_configurator_line_ids.mapped("package_line_of_business")
            )
            if any(x for x in lob_occurences if lob_occurences[x] > 1):
                raise ValidationError(
                    _("You can't have multiple lines of the same Line of Business.")
                )
