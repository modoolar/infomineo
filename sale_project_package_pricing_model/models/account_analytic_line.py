# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, models
from odoo.exceptions import ValidationError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def _get_uom(self):
        """
        Method used to get UOM from the AAL or if missing
        will use the encode_uom from project (related from company)
        """
        self.ensure_one()

        return (
            self.product_uom_id
            if self.product_uom_id
            else self.project_id.timesheet_encode_uom_id
        )

    @api.constrains("so_line")
    def _constrains_so_line(self):
        """
        Forbid the user to have different Sale Order Item
        on Timesheet Lines and on their Task.
        """
        for record in self:
            if (
                record.so_line
                and record.task_id.sale_line_id
                and record.so_line != record.task_id.sale_line_id
            ):
                raise ValidationError(
                    _("The Sale Order Item must be the same as on the Task.")
                )
