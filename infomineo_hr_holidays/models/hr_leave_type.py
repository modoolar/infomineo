# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class HRLeaveType(models.Model):
    _inherit = "hr.leave.type"

    is_automated_leave_type = fields.Boolean()
    automated_number_of_days = fields.Float(default=0.0)

    def _get_domain_for_automated_accrual_plans(self):
        self.ensure_one()
        return [
            ("time_off_type_id", "=", self.id),
            ("is_automated_leave_accrual_plan", "=", True),
        ]

    @api.model
    def get_days_all_request(self):
        return super(
            HRLeaveType, self.sudo().with_context(view_leave_requests=True)
        ).get_days_all_request()

    def get_automated_accrual_plan_allocation_type_and_number_of_days(
        self, employee_id
    ):
        self.ensure_one()
        ret = {
            "accrual_plan_id": False,
            "allocation_type": "regular",
            "number_of_days": self.automated_number_of_days,
        }
        accrual_plans = self.env["hr.leave.accrual.plan"].search(
            self._get_domain_for_automated_accrual_plans()
        )
        if len(accrual_plans) > 0:
            ret["accrual_plan_id"] = accrual_plans[0].id
            ret["allocation_type"] = "accrual"
        return ret
