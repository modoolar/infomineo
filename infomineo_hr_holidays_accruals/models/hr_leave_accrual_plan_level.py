# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)


from odoo import models
from odoo.tools.date_utils import get_timedelta


class AccrualPlanLevel(models.Model):
    _inherit = "hr.leave.accrual.level"

    def _get_addition_value_for_level(self):
        self.ensure_one()
        return get_timedelta(self.start_count, self.start_type)
