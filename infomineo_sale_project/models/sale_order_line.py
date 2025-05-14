# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        """
        Set user_id on project.project to be empty when
        project is created from sale order
        """
        result = super()._timesheet_create_project_prepare_values()
        result["user_id"] = False
        result["privacy_visibility"] = "followers"
        return result
