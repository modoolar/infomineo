# Copyright (C) 2024 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)


from odoo import models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    def _add_skip_days_context(self):
        if self.env.context.get("test_date_from", False):
            return super()._add_skip_days_context()
        return self
