# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).


from odoo import api, fields, models


class SurveyUserInputLine(models.Model):
    _inherit = "survey.user_input.line"

    rating_id = fields.Many2one(
        related="user_input_id.rating_id",
        string="Rating Ref",
        store=True,
        readonly=True,
    )
    create_date = fields.Datetime(string="Submitted on", readonly=True)
    rated_partner_id = fields.Many2one(
        related="rating_id.rated_partner_id",
        string="Assigned to",
        store=True,
        readonly=True,
    )
    partner_id = fields.Many2one(
        related="rating_id.partner_id", string="Customer", store=True, readonly=True
    )
    parent_res_name = fields.Char(
        related="rating_id.parent_res_name", store=True, readonly=True
    )
    parent_res_model = fields.Char(
        related="rating_id.parent_res_model", store=True, readonly=True
    )
    res_name = fields.Char(related="rating_id.res_name", store=True, readonly=True)
    rating = fields.Float(related="rating_id.rating", store=True, readonly=True)
    rating_text = fields.Char(
        compute="_compute_rating_text",
        store=True,
    )
    rating_email_to = fields.Char(
        related="rating_id.rating_email_to",
        store=True,
        readonly=True,
        string="Sent By Email",
    )
    rating_name_to = fields.Char(
        related="rating_id.rating_name_to", store=True, readonly=True, string="Rated by"
    )
    consumed = fields.Boolean(related="rating_id.consumed", store=True, readonly=True)
    client_contact = fields.Char(readonly=True)
    requestor_name = fields.Char(readonly=True)
    surveyed_by = fields.Char(readonly=True)
    rated_partner_ids = fields.Many2many(
        string="Assigned Partners",
        compute="_compute_rated_user_ids",
        comodel_name="res.partner",
    )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        result.update_survey_data()
        return result

    def update_survey_data(self):
        for rec in self:
            if not rec.rating_name_to:
                rec.write(
                    {
                        "surveyed_by": rec.user_input_id.partner_id.name or "",
                        "client_contact": rec.user_input_id.email or "",
                        "answer_score": rec.answer_score,
                        "answer_is_correct": rec.answer_is_correct,
                    }
                )

    def _compute_rated_user_ids(self):
        for r in self:
            r.rated_partner_ids = (
                r.rating_id.resource_ref
                and r.rating_id.resource_ref.user_ids.mapped("partner_id")
                or False
            )

    @api.depends("rating_id.rating_text")
    def _compute_rating_text(self):
        for r in self:
            string_value = dict(r.rating_id._fields["rating_text"].selection).get(
                r.rating_id.rating_text
            )
            r.rating_text = string_value

    def fill_missing_rating_info(self):
        for record in self.filtered(
            lambda r: not r.rating_name_to or not r.rating_email_to
        ):
            record.rating_name_to, record.rating_email_to = (
                record.rating_name_to or record.rating_email_to or "N/A",
                record.rating_email_to or record.rating_name_to or "N/A",
            )
