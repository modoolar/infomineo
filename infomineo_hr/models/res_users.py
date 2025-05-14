# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class User(models.Model):
    _inherit = "res.users"

    medical_number = fields.Char(related="employee_id.medical_number")
    retirement_account_number = fields.Char(
        related="employee_id.retirement_account_number"
    )

    @property
    def SELF_READABLE_FIELDS(self):
        return super().SELF_READABLE_FIELDS + [
            "medical_number",
            "retirement_account_number",
        ]
