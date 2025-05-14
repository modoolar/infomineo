# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    sales_package_discuss_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        default=lambda s: s.env["res.company"]._default_sales_package_discuss_channel(),
        config_parameter="infomineo_sale_package_notifications.sales_package_channel",
    )
    sales_package_notification_threshold = fields.Integer(
        default=lambda s: s.env[
            "res.company"
        ]._default_sales_package_notification_threshold(),
        config_parameter="infomineo_sale_package_notifications.sales_package_threshold",
    )
    project_package_discuss_channel_id = fields.Many2one(
        comodel_name="mail.channel",
        default=lambda s: s.env[
            "res.company"
        ]._default_project_package_discuss_channel(),
        config_parameter="infomineo_sale_package_notifications.project_package_channel",
    )
    project_package_notification_threshold = fields.Integer(
        default=lambda s: s.env[
            "res.company"
        ]._default_project_package_notification_threshold(),
        config_parameter="infomineo_sale_package_notifications.project_package_threshold",
    )
