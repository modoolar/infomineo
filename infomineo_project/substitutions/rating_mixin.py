# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).


from odoo.addons.rating.models.rating_mixin import RatingMixin as originalRatingMixin


def rating_apply(self, rate, token=None, feedback=None, subtype_xmlid=None):
    """Apply a rating given a token. If the current model inherits from
    mail.thread mixin, a message is posted on its chatter. User going through
    this method should have at least employee rights because of rating
    manipulation (either employee, either sudo-ed in public controllers after
    security check granting access).

    :param float rate : the rating value to apply
    :param string token : access token
    :param string feedback : additional feedback
    :param string subtype_xmlid : xml id of a valid mail.message.subtype

    :returns rating.rating record
    """
    rating = None
    if token:
        rating = self.env["rating.rating"].search(
            [("access_token", "=", token)], limit=1
        )
    else:
        rating = self.env["rating.rating"].search(
            [("res_model", "=", self._name), ("res_id", "=", self.ids[0])], limit=1
        )
    if rating and self._name != "helpdesk.ticket":
        rating.write({"rating": rate, "feedback": feedback, "consumed": True})
        if (
            hasattr(self, "message_post")
            and self._name == "project.task"
            and rate == 1
            and rating.rating_email_to == self.client_contact
        ):
            if (
                self.project_id
                and self.project_id.user_id
                and self.project_id.user_id.partner_id
                and self.project_id.user_id.partner_id.email
            ):
                self.with_context(
                    bad_task_rating_notification=True,
                    rating_email=self.project_id.user_id.partner_id.email,
                    rating_name=self.project_id.user_id.partner_id.name,
                ).message_post_with_template(
                    self.env.ref("infomineo_project.bad_task_rating_notification").id,
                    message_type="comment",
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
            if self.manager_qa_id and self.manager_qa_id.email:
                self.with_context(
                    bad_task_rating_notification=True,
                    rating_email=self.manager_qa_id.email,
                    rating_name=self.manager_qa_id.name,
                ).message_post_with_template(
                    self.env.ref("infomineo_project.bad_task_rating_notification").id,
                    message_type="comment",
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
            if self.vp_representative_id and self.vp_representative_id.email:
                self.with_context(
                    bad_task_rating_notification=True,
                    rating_email=self.vp_representative_id.email,
                    rating_name=self.vp_representative_id.name,
                ).message_post_with_template(
                    self.env.ref("infomineo_project.bad_task_rating_notification").id,
                    message_type="comment",
                    subtype_id=self.env["ir.model.data"]._xmlid_to_res_id(
                        "mail.mt_note"
                    ),
                )
        if (
            hasattr(self, "stage_id")
            and self.stage_id
            and hasattr(self.stage_id, "auto_validation_kanban_state")
            and self.stage_id.auto_validation_kanban_state
        ):
            if rating.rating > 2:
                self.write({"kanban_state": "done"})
            else:
                self.write({"kanban_state": "blocked"})
    return rating


def patch_rating_mixin_methods():
    originalRatingMixin._patch_method("rating_apply", rating_apply)
