# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class ResUsers(models.Model):
    _inherit = "res.users"

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)

        if result and self._context.get("create_partner_from_employee"):
            acc = self.env["account.account"].search(
                [("code", "=", "443800"), ("company_id.country_id.code", "=", "MA")]
            )
            result.filtered(lambda r: r.company_id.country_id.code == "MA").mapped(
                "partner_id"
            ).write({"property_account_payable_id": acc.id})

        return result

    def write(self, values):
        if (
            "company_ids" in values
            and values["company_ids"]
            and isinstance(values["company_ids"][0], tuple)
        ):
            self._validate_user_is_employed_in_companies(
                values.get("company_ids")[0][-1]
            )

        return super().write(values)

    def _validate_user_is_employed_in_companies(self, company_ids):
        self.ensure_one()

        if not self._context.get("ui_companies_update", False):
            return

        if any(
            not self.env["hr.employee"]
            .sudo()
            .search([("user_id", "=", self.id), ("company_id", "=", cid)])
            for cid in (company_ids if type(company_ids) is list else [company_ids])
        ):
            msg = _("You can only add companies where {user_name} is employee.")
            raise ValidationError(msg.format(user_name=self.name))
