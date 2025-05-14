# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class HrExpense(models.Model):
    _inherit = "hr.expense"

    company_id = fields.Many2one(
        states={"draft": [("readonly", False)], "reported": [("readonly", False)]}
    )
    currency_id = fields.Many2one(states={"reported": [("readonly", False)]})

    analytic_tag_ids = fields.Many2many(compute="_compute_analytic_tags", store=True)

    @api.depends("employee_id")
    def _compute_analytic_tags(self):
        for record in self:
            analytic_default = self.env["account.analytic.default"].search(
                [
                    ("department_id", "=", record.employee_id.department_id.id),
                    ("analytic_tag_ids", "!=", False),
                    "|",
                    ("company_id", "=", record.company_id.id),
                    ("company_id", "=", False),
                ],
                limit=1,
            )
            record.analytic_tag_ids = (
                analytic_default.analytic_tag_ids if analytic_default else False
            )
