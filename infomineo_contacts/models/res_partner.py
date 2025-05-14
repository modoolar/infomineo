# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# @author Petar Najman <petar.najman@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.constrains("parent_id", "company_type")
    def _check_is_child_company(self):
        """
        Restrict creating a child company of another company.
        """
        for partner in self:
            if partner.parent_id and partner.company_type == "company":
                raise ValidationError(
                    _("You can't have a company as a child of another company.")
                )
