# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import _, api, models
from odoo.exceptions import UserError


class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    @api.constrains("name")
    def _check_description_mandatory(self):
        for line in self:
            project = line.project_id
            if (
                project
                and project.description_mandatory
                and (not line.name or line.name == "/")
            ):
                raise UserError(_("Description for timesheet line is mandatory."))
