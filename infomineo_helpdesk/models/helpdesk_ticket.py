# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, models, tools


class HelpdeskTicket(models.Model):
    _inherit = "helpdesk.ticket"

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)

        if "partner_email" in fields:
            result["partner_email"] = self.env.user.partner_id.email

        if "partner_phone" in fields:
            result["partner_phone"] = self.env.user.partner_id.phone

        return result

    def write(self, vals):
        ret = super(HelpdeskTicket, self).write(vals)
        if vals.get("stage_id", False):
            self._send_ticket_rating_mail()
        return ret

    def _send_ticket_rating_mail(self):
        for ticket in self:
            rating_template = ticket.stage_id.rating_mail_template_id
            if rating_template:
                ticket.rating_send_request(
                    rating_template, lang=ticket.partner_id.lang, force_send=True
                )

    def rating_send_request(
        self,
        template,
        lang=False,
        subtype_id=False,
        force_send=True,
        composition_mode="comment",
        notif_layout=None,
    ):
        notif_layout = "infomineo_rating_survey.mail_notification_light"
        if self.create_uid and self.create_uid.email:
            super(
                HelpdeskTicket,
                self.with_context(
                    rating_email=self.create_uid.email,
                    rating_name=self.create_uid.name,
                ),
            ).rating_send_request(
                template,
                lang=lang,
                subtype_id=subtype_id,
                force_send=force_send,
                composition_mode=composition_mode,
                notif_layout=notif_layout,
            )

    def _get_image_path(self):
        return "/infomineo_rating/static/src/img/rating_%s.png" % (
            int(self.rating_last_value),
        )

    # ------------------------------------------------------------
    # Rating Mixin
    # ------------------------------------------------------------
    def rating_apply(self, rate, token=None, feedback=None, subtype_xmlid=None):
        rating = super(HelpdeskTicket, self).rating_apply(
            rate, token=token, feedback=feedback, subtype_xmlid=subtype_xmlid
        )
        if rating:
            if hasattr(self, "message_post"):
                feedback = tools.plaintext2html(feedback or "")
                author_id = self.create_uid.partner_id
                self.message_post(
                    body=_(
                        "<img src='/infomineo_rating/static/src/img/rating_%s.png' "
                        "alt=':%s/5' "
                        "style='width:18px;height:18px;float:left;margin-right: 5px;'/>%s"
                    )
                    % (rate, rate, feedback),
                    subtype_xmlid=subtype_xmlid or "mail.mt_comment",
                    author_id=author_id and author_id.id or None
                    # None will set the default author in mail_thread.py
                )
            recipients = [
                recipient
                for recipient in (
                    self.user_id and self.user_id.partner_id.email,
                    self.team_id and self.team_id.helpdesk_team_manager_id.email,
                )
                if recipient
            ]
            for recipient in recipients:
                template = self.env.ref(
                    "infomineo_helpdesk.ticket_rating_result_notification"
                )
                template.with_context(email_to=recipient).send_mail(
                    self.id, force_send=True
                )
        return rating
