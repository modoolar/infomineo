# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ContactCertificate(models.Model):
    _name = "contact.certificate"
    _description = "Contact Certificate"

    active = fields.Boolean(default=True)
    name = fields.Char(required=True, index=True, string="Number")
    expiry_date = fields.Date()

    _sql_constraints = [
        (
            "unique_name",
            "unique (name)",
            "Same Certificate Number already exists.",
        )
    ]

    def write(self, vals):
        if "name" in vals or "expiry_date" in vals:
            partners_to_reset = self.env["res.partner"].search(
                [("contact_certificate_id", "in", self.ids)]
            )
            partners_to_reset.write({"is_notified": False})

        return super().write(vals)
