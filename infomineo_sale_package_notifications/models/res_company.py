# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    _DEFAULT_SALES_PACKAGE_NOTIFICATION_THRESHOLD = 1
    _DEFAULT_PROJECT_PACKAGE_NOTIFICATION_THRESHOLD = 1

    sales_package_discuss_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        index=True,
        default=lambda s: s._default_sales_package_discuss_channel(),
    )
    sales_package_notification_threshold = fields.Integer(
        required=True,
        default=lambda s: s._default_sales_package_notification_threshold(),
    )
    project_package_discuss_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        index=True,
        default=lambda s: s._default_project_package_discuss_channel(),
    )
    project_package_notification_threshold = fields.Integer(
        required=True,
        default=lambda s: s._default_project_package_notification_threshold(),
    )

    @api.model
    def _default_sales_package_discuss_channel(self):
        return self.env["mail.channel"].browse(
            int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("infomineo_sale_package_notifications.sales_package_channel")
            )
        )

    @api.model
    def _default_sales_package_notification_threshold(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "infomineo_sale_package_notifications.sales_package_threshold",
                default=self._DEFAULT_SALES_PACKAGE_NOTIFICATION_THRESHOLD,
            )
        )

    @api.model
    def _default_project_package_discuss_channel(self):
        return self.env["mail.channel"].browse(
            int(
                self.env["ir.config_parameter"]
                .sudo()
                .get_param(
                    "infomineo_sale_package_notifications.project_package_channel"
                )
            )
        )

    @api.model
    def _default_project_package_notification_threshold(self):
        return int(
            self.env["ir.config_parameter"]
            .sudo()
            .get_param(
                "infomineo_sale_package_notifications.project_package_threshold",
                default=self._DEFAULT_PROJECT_PACKAGE_NOTIFICATION_THRESHOLD,
            )
        )

    def _get_notifications_chat_channel_for_sales_package(self):
        return (
            self.sales_package_discuss_channel_id
            or self._default_sales_package_discuss_channel()
        )

    def _get_notifications_chat_channel_for_project_package(self):
        return (
            self.project_package_discuss_channel_id
            or self._default_project_package_discuss_channel()
        )
