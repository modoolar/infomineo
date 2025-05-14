# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class SurveySurvey(models.Model):
    _inherit = "survey.survey"

    new_when_re_shared = fields.Boolean(
        string="Re-Share New",
        help="""When checked, the survey will always
                send new instance even if already answered,
                instead of retrying and rewriting existing survey input""",
    )
