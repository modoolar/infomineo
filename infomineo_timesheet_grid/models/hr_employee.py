# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    def _get_timesheet_manager_id_domain(self):
        ret = super()._get_timesheet_manager_id_domain()
        group = self.env.ref(
            "infomineo_timesheet_grid.group_timesheet_team_approver",
            raise_if_not_found=False,
        )
        ret[0][2].append(group.id)
        return ret

    timesheet_manager_id = fields.Many2one(domain=_get_timesheet_manager_id_domain)
