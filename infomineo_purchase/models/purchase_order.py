# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def action_change_company(self):
        action = self.env.ref(
            "infomineo_purchase.action_purchase_order_company_switch"
        ).read()[0]
        action["context"] = dict(
            switch_company_ids=(self.env.user.company_ids - self.env.company).ids,
            switch_currency_ids=(self.sudo().env["res.currency"].search([])).ids,
        )
        return action

    def _approval_allowed(self):
        self.ensure_one()
        allowed = super()._approval_allowed()
        return allowed or self.user_has_groups(
            "infomineo_purchase.group_team_approver_purchase"
        )


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    account_analytic_id = fields.Many2one(string="Project Code")
    analytic_tag_ids = fields.Many2many(string="Department")
