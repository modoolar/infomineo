# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class HelpdeskTeam(models.Model):
    _inherit = "helpdesk.team"

    helpdesk_team_manager_id = fields.Many2one("res.partner")
