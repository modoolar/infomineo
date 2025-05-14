# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    def init(self):
        super().init()
        self._cr.execute(
            """
            update ir_model_access
            set perm_unlink = true
            where id in (
                select res_id from ir_model_data
                where model = 'ir.model.access'
                and name = 'access_account_analytic_line_user'
                and module = 'hr_timesheet'
            );
            """
        )
