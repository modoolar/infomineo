# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    show_additional_bill_fields = fields.Boolean(
        related="company_id.show_additional_bill_fields",
        readonly=False,
        string="Show additional bill fields",
        help="By enabling this setting, "
        "fields 'Serie', 'UUID', 'Payment Method' and "
        "'Voucher type' will be shown on "
        "bills. Currently this is set "
        "and only used for Mexico company.",
    )
