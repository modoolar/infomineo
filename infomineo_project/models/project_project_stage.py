# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import fields, models


class ProjectProjectStage(models.Model):
    _inherit = "project.project.stage"

    is_closed = fields.Boolean()
    rating_mail_template_id = fields.Many2one(
        "mail.template",
        string="Rating Email Template",
        domain=[("model", "=", "project.project")],
    )
