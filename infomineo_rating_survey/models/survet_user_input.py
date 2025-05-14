# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import fields, models


class SurveyUserInput(models.Model):
    _inherit = "survey.user_input"

    rating_id = fields.Many2one(comodel_name="rating.rating")
