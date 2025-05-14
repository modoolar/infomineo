# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    _DEFAULT_NOTIFICATION_THRESHOLD = 7

    contact_discuss_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        index=True,
        default=lambda s: s._default_contact_discuss_channel(),
    )
    notification_threshold = fields.Integer(
        required=True, default=lambda s: s._default_notification_threshold()
    )

    @api.model
    def _default_contact_discuss_channel(self):
        return self.env["mail.channel"].browse(
            int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("contacts_certificates.contact_discuss_channel_id")
            )
        )

    @api.model
    def _default_notification_threshold(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "contacts_certificates.notification_threshold",
                default=self._DEFAULT_NOTIFICATION_THRESHOLD,
            )
        )

    def _get_notifications_chat_channel_for_contact_certificate(self):
        return (
            self.contact_discuss_channel_id or self._default_contact_discuss_channel()
        )
