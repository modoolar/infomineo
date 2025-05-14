# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import models


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_attachment_types(self):
        return {}
