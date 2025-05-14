# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["sale.order", "res.notifier"]

    @api.model
    def run_sales_package_expiry_check(self):
        self.set_notification_type(
            {
                "sales_package": {
                    "ref_model": "res.company",
                    "ref_field": "company_id",
                    "notifications": ["activity", "chat"],
                }
            }
        )

        return self.run_notifications_check()

    @api.model
    def _get_sales_package_notification_records(self, company):
        time_delta = (
            company.sales_package_notification_threshold
            or company._default_sales_package_notification_threshold()
        )
        threshold = fields.Date.today() + relativedelta(months=+time_delta)
        orders_within_threshold = self.search(
            [
                ("is_notified", "=", False),
                (
                    "order_type",
                    "=",
                    "package",
                ),
                (
                    "package_expiry_datetime",
                    "<=",
                    threshold,
                ),
                ("company_id", "=", company.id),
            ]
        )

        orders_with_consumed_points = self.search(
            [
                ("is_notified", "=", False),
                ("order_type", "=", "package"),
                ("consumed_points_count", "!=", False),
                ("company_id", "=", company.id),
            ]
        ).filtered(
            lambda s: float_compare(
                s.consumed_points_count, s.package_size * 0.8, precision_digits=4
            )
            >= 0
        )

        return orders_within_threshold | orders_with_consumed_points

    @api.model
    def _get_activity_text_for_sales_package(self):
        return _("Sales package is about to expire.")

    def _get_activity_responsible_for_sales_package(self):
        self.ensure_one()

        return self.user_id

    def _get_activity_date_deadline_for_sales_package(self):
        self.ensure_one()

        return self.package_expiry_datetime

    @api.model
    def _get_channel_notification_template_for_sales_package(self):
        return _(
            "Sales order "
            '<a href="{web_base_url}web#model=sale.order&amp;id={order_id}" '
            'class="o_mail_redirect" data-oe-id="{order_id}" '
            'data-oe-model="sale.order" target="_blank">{order_name}</a>'
            " will soon reach package expiry date."
        )

    def _get_discuss_channel_notification_for_sales_package(self):
        self.ensure_one()

        template = self._get_channel_notification_template_for_sales_package()

        return template.format(
            web_base_url=self.env["ir.config_parameter"]
            .sudo()
            .get_param("web.base.url"),
            order_id=self.id,
            order_name=self.name,
        )
