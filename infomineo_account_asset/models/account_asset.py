# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class AccountAsset(models.Model):
    _inherit = "account.asset"

    reference = fields.Char()
    owner = fields.Char()
    other_information = fields.Char()
    disposed = fields.Boolean()
    analytic_tag_ids = fields.Many2many(readonly=False)
    payment_date = fields.Date()
    show_additional_bill_fields = fields.Boolean(
        related="company_id.show_additional_bill_fields", store=True
    )

    def set_to_close(self, invoice_line_id, date=None):
        self.ensure_one()
        result = super().set_to_close(invoice_line_id, date)
        full_asset = self + self.children_ids
        full_asset.write({"disposed": True})
        return result

    def set_to_running(self):
        result = super().set_to_running()
        self.write({"disposed": False})
        return result

    def write(self, vals):
        res = super().write(vals)
        if vals.get("analytic_tag_ids"):
            for rec in self:
                drafted = rec.depreciation_move_ids.filtered(
                    lambda m: m.state == "draft"
                )
                for draft in drafted:
                    draft.line_ids.analytic_tag_ids = rec.analytic_tag_ids
        return res
