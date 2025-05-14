# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import uuid
from datetime import timedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestContactCertificates(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.company_a = cls.env["res.company"].create({"name": "C_A"})
        cls.company_b = cls.env["res.company"].create({"name": "C_B"})

        cls.partner_a = cls.env["res.partner"].create(
            {
                "name": "P_A",
                "company_id": cls.company_a.id,
                "user_id": cls.env.ref("base.partner_admin").id,
            }
        )
        cls.partner_b = cls.env["res.partner"].create(
            {
                "name": "P_B",
                "company_id": cls.company_a.id,
                "user_id": cls.env.ref("base.partner_admin").id,
            }
        )
        cls.partner_c = cls.env["res.partner"].create(
            {
                "name": "P_C",
                "company_id": cls.company_b.id,
                "user_id": cls.env.ref("base.partner_admin").id,
            }
        )
        cls.partner_d = cls.env["res.partner"].create(
            {
                "name": "P_D",
                "company_id": False,
                "user_id": cls.env.ref("base.partner_admin").id,
            }
        )
        cls.default_notification_channel = cls.env.ref(
            "contacts_certificates.channel_contact_channel"
        )

    def test_expired_contact_certificates_notifications(self):
        """
        Test expired contact certificates is set on partner on creation
        """

        self.partner_a.contact_certificate_id = self.env["contact.certificate"].create(
            {
                "name": str(uuid.uuid4()),
                "expiry_date": fields.Date.today() + timedelta(days=3),
            }
        )
        self.partner_b.contact_certificate_id = self.env["contact.certificate"].create(
            {
                "name": str(uuid.uuid4()),
                "expiry_date": fields.Date.today() + timedelta(days=9),
            }
        )
        self.partner_c.contact_certificate_id = self.env["contact.certificate"].create(
            {
                "name": str(uuid.uuid4()),
                "expiry_date": fields.Date.today() + timedelta(days=4),
            }
        )
        self.partner_d.contact_certificate_id = self.env["contact.certificate"].create(
            {
                "name": str(uuid.uuid4()),
                "expiry_date": fields.Date.today() + timedelta(days=5),
            }
        )

        self.assertFalse(
            self.has_notifications(
                self.partner_a.name,
                self.partner_a.activity_ids,
                self.partner_a.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_a.name, self.partner_a.id
            ),
        )
        self.assertFalse(
            self.has_notifications(
                self.partner_b.name,
                self.partner_b.activity_ids,
                self.partner_b.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_b.name, self.partner_b.id
            ),
        )
        self.assertFalse(
            self.has_notifications(
                self.partner_c.name,
                self.partner_c.activity_ids,
                self.partner_c.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_c.name, self.partner_c.id
            ),
        )
        self.assertFalse(
            self.has_notifications(
                self.partner_d.name,
                self.partner_d.activity_ids,
                self.default_notification_channel.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_d.name, self.partner_d.id
            ),
        )

        self.env["res.partner"].run_contact_certificate_expiry_check()

        self.assertTrue(
            self.has_notifications(
                self.partner_a.name,
                self.partner_a.activity_ids,
                self.partner_a.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_a.name, self.partner_a.id
            ),
        )
        self.assertFalse(
            self.has_notifications(
                self.partner_b.name,
                self.partner_b.activity_ids,
                self.partner_b.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_b.name, self.partner_b.id
            ),
        )
        self.assertTrue(
            self.has_notifications(
                self.partner_c.name,
                self.partner_c.activity_ids,
                self.partner_c.company_id.contact_discuss_channel_id.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_c.name, self.partner_c.id
            ),
        )
        self.assertTrue(
            self.has_notifications(
                self.partner_d.name,
                self.partner_d.activity_ids,
                self.default_notification_channel.message_ids,
            ),
            "Paretner {}-{} has notifications".format(
                self.partner_d.name, self.partner_d.id
            ),
        )

    def has_notifications(self, partner_name, activity_ids, message_ids):
        return any(
            activity.note == "<p>Contact`s certificate is about to expire.</p>"
            for activity in activity_ids
        ) and any(
            "{}</a> will soon reach expiry date for the certificate.</p>".format(
                partner_name
            )
            in message.body
            for message in message_ids
        )
