# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    previous_so_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        compute="_compute_is_billable",
        string="Previous Sale Order Item",
        store=True,
    )
    is_billable = fields.Boolean(
        compute="_compute_is_billable", inverse="_inverse_is_billable", store=True
    )
    so_line = fields.Many2one(
        inverse="_inverse_so_line",
    )

    @api.depends("so_line")
    def _compute_is_billable(self):
        return self._calculate_billable_from_so_line()

    def _inverse_is_billable(self):
        self._calculate_billable_from_is_billable()

    def _inverse_so_line(self):
        self._calculate_billable_from_so_line()

    @api.depends(
        "task_id.sale_line_id",
        "project_id.sale_line_id",
        "employee_id",
        "project_id.allow_billable",
        "is_billable",
    )
    def _compute_so_line(self):
        res = super()._compute_so_line()
        self._calculate_billable_from_is_billable()

        return res

    def _calculate_billable_from_so_line(self):
        """
        Triggered when so_line is changed
        """
        for rec in self:
            if rec.so_line:
                rec.update({"is_billable": True, "previous_so_line_id": rec.so_line})
            else:
                rec.is_billable = False

    def _calculate_billable_from_is_billable(self):
        """
        Triggered when is_billable is changed
        """
        for rec in self:
            if rec.is_billable and rec.so_line:
                rec.previous_so_line_id = rec.so_line

            if not rec.is_billable:
                rec.so_line = False
            else:
                if rec.previous_so_line_id:
                    rec.so_line = rec.previous_so_line_id
                else:
                    raise UserError(
                        _(
                            "You need to manually specify Sale Order item "
                            "on the line, for which you want to link this work log."
                        )
                    )

    @api.model
    def web_read_group(
        self,
        domain,
        fields,
        groupby,
        limit=None,
        offset=0,
        orderby=False,
        lazy=True,
        expand=False,
        expand_limit=None,
        expand_orderby=False,
    ):
        result = super().web_read_group(
            domain,
            fields,
            groupby,
            limit=limit,
            offset=offset,
            orderby=orderby,
            lazy=lazy,
            expand=expand,
            expand_limit=expand_limit,
            expand_orderby=expand_orderby,
        )

        if "is_billable" not in groupby:
            return result

        for g in result.get("groups"):
            if g.get("is_billable"):
                g.update({"is_billable": "Billable"})
            else:
                g.update({"is_billable": "Non Billable"})

        return result
