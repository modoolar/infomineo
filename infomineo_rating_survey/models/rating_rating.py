# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, fields, models


class Rating(models.Model):
    _inherit = "rating.rating"

    survey_user_input_id = fields.Many2one(comodel_name="survey.user_input")
    survey_user_input_line_ids = fields.One2many(
        comodel_name="survey.user_input.line",
        related="survey_user_input_id.user_input_line_ids",
    )
    rating_email_to = fields.Char()
    rating_name_to = fields.Char()
    rated_partner_ids = fields.Many2many(
        string="Assigned Partners",
        compute="_compute_rated_partner_ids",
        comodel_name="res.partner",
    )

    @api.model_create_multi
    def create(self, value_list):
        result = super().create(value_list)
        if self._context.get("rating_email"):
            result.write(
                {
                    "rating_email_to": self._context.get("rating_email"),
                    "rating_name_to": self._context.get("rating_name"),
                }
            )
        return result

    def _compute_rated_partner_ids(self):
        for r in self:
            if r.resource_ref and r.resource_ref._name == "project.task":
                r.rated_partner_ids = (
                    r.resource_ref
                    and r.resource_ref.user_ids.mapped("partner_id")
                    or False
                )
            else:
                r.rated_partner_ids = False
