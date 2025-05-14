# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import http
from odoo.exceptions import UserError
from odoo.http import request
from odoo.tools.misc import get_lang
from odoo.tools.translate import _

from odoo.addons.rating.controllers import main as main_rating
from odoo.addons.survey.controllers import main as main_survey


class RatingSurvey(main_rating.Rating, main_survey.Survey):
    def _prepare_question_html(self, survey_sudo, answer_sudo, **post):
        """Override of the odoo method"""
        if not request.context.get("rating_survey"):
            return super()._prepare_question_html(survey_sudo, answer_sudo, **post)

        survey_data = self._prepare_survey_data(survey_sudo, answer_sudo, **post)

        if answer_sudo.state == "done":
            survey_content = request.env.ref(
                "infomineo_rating_survey.infomineo_survey_fill_form_done"
            )._render(survey_data)
        else:
            survey_content = request.env.ref(
                "survey.survey_fill_form_in_progress"
            )._render(survey_data)

        survey_progress = False
        if (
            answer_sudo.state == "in_progress"
            and not survey_data.get("question", request.env["survey.question"]).is_page
        ):
            if survey_sudo.questions_layout == "page_per_section":
                page_ids = survey_sudo.page_ids.ids
                survey_progress = request.env.ref("survey.survey_progression")._render(
                    {
                        "survey": survey_sudo,
                        "page_ids": page_ids,
                        "page_number": page_ids.index(survey_data["page"].id)
                        + (1 if survey_sudo.progression_mode == "number" else 0),
                    }
                )
            elif survey_sudo.questions_layout == "page_per_question":
                page_ids = (
                    answer_sudo.predefined_question_ids.ids
                    if not answer_sudo.is_session_answer
                    else survey_sudo.question_ids.ids
                )
                survey_progress = request.env.ref("survey.survey_progression")._render(
                    {
                        "survey": survey_sudo,
                        "page_ids": page_ids,
                        "page_number": page_ids.index(survey_data["question"].id),
                    }
                )

        return {
            "survey_content": survey_content,
            "survey_progress": survey_progress,
            "survey_navigation": request.env.ref("survey.survey_navigation")._render(
                survey_data
            ),
        }

    @http.route(
        "/rate/<string:token>/<int:survey_id>/<int:rate>",
        type="http",
        auth="public",
        website=True,
    )
    def action_open_rating_survey(self, token, survey_id, rate, **kwargs):
        assert rate in (1, 2, 3, 4, 5), "Incorrect rating"
        rating = (
            request.env["rating.rating"].sudo().search([("access_token", "=", token)])
        )
        if rating.consumed:
            partner_id = rating.partner_id.id
            rating_email_to = rating.rating_email_to
            rating_name_to = rating.rating_name_to
            rated_partner_id = rating.rated_partner_id.id
            res_model_id = rating.res_model_id.id
            res_id = rating.res_id

            rating = (
                request.env["rating.rating"]
                .sudo()
                .create(
                    {
                        "partner_id": partner_id,
                        "rating_email_to": rating_email_to,
                        "rating_name_to": rating_name_to,
                        "rated_partner_id": rated_partner_id,
                        "res_model_id": res_model_id,
                        "res_id": res_id,
                        "is_internal": False,
                        "rating": rate,
                        "consumed": False,
                    }
                )
            )

        rate_names = {
            5: _("1- very satisfied"),
            4: _("2- satisfied"),
            3: _("3- neutral"),
            2: _("4- dissatisfied"),
            1: _("5- very dissatisfied"),
        }

        lang = rating.partner_id.lang or get_lang(request.env).code
        ratings_data = {
            "rating": rating,
            "token": rating.access_token,
            "rate_names": rate_names,
            "rate": rate,
        }
        survey = request.env["survey.survey"].sudo().browse(survey_id)

        if not survey:
            return request.not_found()

        access_data = self._get_access_data(
            survey.access_token,
            rating.survey_user_input_id.access_token or False,
            ensure_token=False,
        )
        if access_data["validity_code"] is not True:
            return self._redirect_with_error(access_data, access_data["validity_code"])

        survey_sudo, answer_sudo = (
            access_data["survey_sudo"],
            access_data["answer_sudo"],
        )

        if not answer_sudo:
            partner_who_answers = request.env["res.partner"].search(
                [("email", "=", rating.rating_email_to)], limit=1
            )
            try:
                answer_sudo = survey_sudo._create_answer(partner=partner_who_answers)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights("read")
                survey_sudo.with_user(request.env.user).check_access_rule("read")
            except BaseException:
                return request.redirect("/")
            else:
                return request.render("survey.survey_403_page", {"survey": survey_sudo})

        if not answer_sudo.rating_id:
            rating.survey_user_input_id = answer_sudo
            answer_sudo.rating_id = rating

        answer_sudo._mark_in_progress()
        survey_data = self._prepare_survey_data(survey_sudo, answer_sudo)
        ratings_data.update(survey_data)
        return (
            request.env["ir.ui.view"]
            .with_context(lang=lang)
            ._render_template(
                "infomineo_rating_survey.rating_survey_page_submit", ratings_data
            )
        )

    @http.route(
        "/rating/survey/submit/<string:rating_token>/"
        "<string:survey_token>/<string:answer_token>",
        type="json",
        auth="public",
        website=True,
    )
    def action_submit_rating_survey(
        self, rating_token, survey_token, answer_token, **post
    ):
        context = dict(request.context)
        context["rating_survey"] = True
        request.context = context
        vals = self.survey_submit(survey_token, answer_token, **post)

        rating = (
            request.env["rating.rating"]
            .sudo()
            .search([("access_token", "=", rating_token)])
        )
        user_input = (
            request.env["survey.user_input"]
            .sudo()
            .search([("access_token", "=", answer_token)])
        )

        rating.survey_user_input_id = user_input
        user_input.rating_id = rating
        user_input.last_displayed_page_id = False

        res_object = request.env[rating.res_model].sudo().browse(rating.res_id)
        user_input.user_input_line_ids.write(
            {
                "client_contact": res_object._get_client_contact(),
                "requestor_name": res_object._get_requestor_name(),
            }
        )
        if request.httprequest.method == "POST" and post.get("rate"):
            rate = int(post.get("rate"))
            assert rate in (1, 2, 3, 4, 5), "Incorrect rating"
            record_sudo = request.env[rating.res_model].sudo().browse(rating.res_id)
            record_sudo.rating_apply(
                rate, token=rating_token, feedback=post.get("feedback")
            )

        return vals

    def _check_validity(
        self, survey_token, answer_token, ensure_token=True, check_partner=True
    ):
        return super(RatingSurvey, self)._check_validity(
            survey_token, answer_token, ensure_token=ensure_token, check_partner=False
        )
