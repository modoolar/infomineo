# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from datetime import timedelta

from odoo import _, api, fields, models


class ResPartner(models.Model):
    _name = "res.partner"
    _inherit = ["res.partner", "res.notifier"]

    contact_certificate_id = fields.Many2one(
        comodel_name="contact.certificate",
        copy=False,
    )

    @api.model
    def run_contact_certificate_expiry_check(self):
        self.set_notification_type(
            {
                "contact_certificate": {
                    "ref_model": "res.company",
                    "ref_field": "company_id",
                    "notifications": ["activity", "chat"],
                }
            }
        )

        return self.run_notifications_check()

    @api.model
    def _get_contact_certificate_notification_records(self, company):
        time_delta = (
            company.notification_threshold or company._default_notification_threshold()
        )
        threshold = fields.Date.today() + timedelta(days=time_delta)

        return self.search(
            [
                ("is_notified", "=", False),
                (
                    "contact_certificate_id.expiry_date",
                    "<=",
                    threshold,
                ),
                ("company_id", "=", company.id),
            ]
        )

    @api.model
    def _get_activity_text_for_contact_certificate(self):
        return _("Contact`s certificate is about to expire.")

    def _get_activity_responsible_for_contact_certificate(self):
        """HOOK METHOD"""
        self.ensure_one()

        return self.user_id

    def _get_activity_date_deadline_for_contact_certificate(self):
        self.ensure_one()

        return self.contact_certificate_id and self.contact_certificate_id.expiry_date

    @api.model
    def _get_channel_notification_template_for_contact_certificate(self):
        return _(
            "Contact "
            '<a href="{web_base_url}web#model=res.partner&amp;id={partner_id}" '
            'class="o_mail_redirect" data-oe-id="{partner_id}" '
            'data-oe-model="res.partner" target="_blank">{partner_name}</a>'
            " will soon reach expiry date for the certificate."
        )

    def _get_discuss_channel_notification_for_contact_certificate(self):
        self.ensure_one()

        template = self._get_channel_notification_template_for_contact_certificate()

        return template.format(
            web_base_url=self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url"),
            partner_id=self.id,
            partner_name=self.name,
        )
