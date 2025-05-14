# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models


class SurveyInvite(models.TransientModel):
    _inherit = "survey.invite"

    def _prepare_answers(self, partners, emails):

        existing_answers = self.env["survey.user_input"].search(
            [
                "&",
                ("survey_id", "=", self.survey_id.id),
                "|",
                ("partner_id", "in", partners.ids),
                ("email", "in", emails),
            ]
        )
        existing_user_inputs = {
            x.id: (x.partner_id.id, x.email) for x in existing_answers
        }
        existing_answers.write({"partner_id": self.env["res.partner"], "email": ""})

        answers = super()._prepare_answers(partners, emails)

        for existing_answer in existing_answers:
            existing_answer.write(
                {
                    "partner_id": existing_user_inputs[existing_answer.id][0],
                    "email": existing_user_inputs[existing_answer.id][1],
                }
            )

        return answers
