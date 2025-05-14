# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class AccrualPlan(models.Model):
    _inherit = "hr.leave.accrual.plan"

    is_automated_leave_accrual_plan = fields.Boolean()
