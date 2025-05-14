# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import fields, models
from odoo.tests.common import Form


class PurchaseOrderCompanySwitchWizard(models.TransientModel):
    _name = "purchase.order.company.switch.wizard"
    _description = "Purchase Order Company Switch Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Switch to company",
        required=True,
    )
    currency_id = fields.Many2one(
        comodel_name="res.currency",
        string="Switch to currency",
    )

    def switch_company(self):
        active_ids = self._context.get("active_id", False)
        order = self.env["purchase.order"].browse(active_ids)

        purchase_form = Form(order.sudo(), "purchase.purchase_order_form")

        for index, _ in enumerate(order.order_line):
            with purchase_form.order_line.edit(index) as line:
                if line.account_analytic_id.company_id:
                    line.account_analytic_id = self.env["account.analytic.account"]

                if self.currency_id and line.currency_id != self.currency_id:
                    to_date = purchase_form.date_order or fields.Date.today()
                    line.price_unit = line.currency_id._convert(
                        line.price_unit, self.currency_id, self.company_id, to_date
                    )

        purchase_form.company_id = self.company_id
        purchase_form.save()
