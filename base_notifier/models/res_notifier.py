# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
import logging

from odoo import SUPERUSER_ID, api, fields, models

_logger = logging.getLogger(__name__)


class ResNotifier(models.AbstractModel):
    _name = "res.notifier"
    _description = "Res Notifier"

    _NOTIFICATION_TYPES = dict()

    is_notified = fields.Boolean()

    @api.model
    def set_notification_type(self, type_config):
        self._NOTIFICATION_TYPES.setdefault(self._name, {}).update(type_config)

    @api.model
    def run_notifications_check(self, notification=None):
        # Run single notification if specified in `notification` parameter
        if notification:
            reason, config_data = self._NOTIFICATION_TYPES.get(self._name).get(
                notification
            )
            self._run_all_notifiers(reason, config_data)
            return

        # Otherwise run all notifications for given model
        for reason, config_data in self._NOTIFICATION_TYPES.get(self._name).items():
            self._run_all_notifiers(reason, config_data)

    @api.model
    def _run_all_notifiers(self, reason, config_data):
        super_config_model = self.with_user(SUPERUSER_ID).env[
            config_data.get("ref_model")
        ]

        # Run notifiers with parameters taken from assigned config record
        for ref_model_name in super_config_model.search([]):
            self._run_notifiers(ref_model_name, reason)

        # Run notifiers without config record assigned,
        # with default parameters taken from odoo config
        self._run_notifiers(super_config_model, reason)

    @api.model
    def _run_notifiers(self, config, reason):
        records_to_notify = self._get_records_within_notification_domain(config, reason)

        if not records_to_notify:
            _logger.info(
                "No records for {reason} notifications was found "
                "for {config_name} with ids: {config_ids}.".format(
                    reason=reason, config_name=config._name, config_ids=config.ids
                )
            )
            return

        for notification_type in (
            self._NOTIFICATION_TYPES.get(self._name).get(reason).get("notifications")
        ):
            notify_fnc = "_notify_by_{type}".format(type=notification_type)

            if not hasattr(records_to_notify, notify_fnc):
                _logger.debug(
                    "No implementation for {notify_fnc} method was found "
                    "for {model_name}.".format(
                        notify_fnc=notify_fnc, model_name=self._name
                    )
                )
                continue

            getattr(records_to_notify, notify_fnc)(reason)

        records_to_notify.write({"is_notified": True})

    @api.model
    def _get_records_within_notification_domain(self, config, reason):
        record_getter = "_get_{reason}_notification_records".format(reason=reason)

        if not hasattr(self, record_getter):
            _logger.debug(
                "No implementation for {getter_fnc} method was found "
                "for {model_name}.".format(
                    getter_fnc=record_getter, model_name=self._name
                )
            )
            return

        return getattr(self, record_getter)(config)

    def _notify_by_activity(self, reason):
        responsible_user_getter = "_get_activity_responsible_for_{reason}".format(
            reason=reason
        )
        activity_text_getter = "_get_activity_text_for_{reason}".format(reason=reason)
        date_deadline_getter = "_get_activity_date_deadline_for_{reason}".format(
            reason=reason
        )

        note = getattr(self, activity_text_getter)()

        for record in self:
            responsible_user_id = getattr(record, responsible_user_getter)()

            if responsible_user_id:
                record.activity_schedule(
                    "mail.mail_activity_data_todo",
                    note=note,
                    user_id=responsible_user_id.id,
                    date_deadline=fields.Date.to_string(
                        getattr(record, date_deadline_getter)()
                    ),
                )

    def _notify_by_chat(self, reason):
        config_ref_field = (
            self._NOTIFICATION_TYPES.get(self._name).get(reason).get("ref_field")
        )
        channel_getter = "_get_notifications_chat_channel_for_{reason}".format(
            reason=reason
        )
        channel = getattr(self.mapped(config_ref_field), channel_getter)()

        if not channel:
            _logger.info(
                "No Discuss Channel was found for {reason}.".format(reason=reason)
            )
            return

        for record in self:
            body = getattr(
                record,
                "_get_discuss_channel_notification_for_{reason}".format(reason=reason),
            )()

            channel.message_post(
                body=body,
                message_type="comment",
                subtype_xmlid="mail.mt_comment",
            )

    def _notify_by_mail(self, reason):
        mail_text_getter = "_get_mail_text_for_{reason}".format(reason=reason)

        for record in self:
            if not hasattr(record, mail_text_getter):
                _logger.debug(
                    "No implementation for {getter_fnc} method was found "
                    "for {model_name}.".format(
                        getter_fnc=mail_text_getter, model_name=self._name
                    )
                )
                continue

            mail_body = getattr(record, mail_text_getter)()

            record.message_post(body=mail_body)
