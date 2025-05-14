# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class HelpdeskStage(models.Model):
    _inherit = "helpdesk.stage"

    rating_mail_template_id = fields.Many2one(
        "mail.template",
        string="Rating Email Template",
        domain=[("model", "=", "helpdesk.ticket")],
    )
