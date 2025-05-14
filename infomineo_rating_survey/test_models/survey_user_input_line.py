# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    def update_survey_data(self):
        if self.env.context.get("infomineo_test_infomineo_rating_survey", False):
            super().create()
        return
