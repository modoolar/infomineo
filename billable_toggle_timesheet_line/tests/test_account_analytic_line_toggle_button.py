# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests import TransactionCase


class TestAccountAnalyticLineToggleButton(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Creating a product that is configured to create a Project with a Task
        adding it on a Sale Order, and confirming it to get the created Project.
        """
        super(TestAccountAnalyticLineToggleButton, cls).setUpClass()

        cls.product_task_in_project = cls.env["product.product"].create(
            {
                "name": "Task in Project Service",
                "type": "service",
                "service_tracking": "task_in_project",
            }
        )

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.order = cls.init_sale_order()
        cls.project = cls.order.order_line.project_id
        cls.task = cls.project.task_ids[0]

    @classmethod
    def init_sale_order(cls):
        order = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product_task_in_project.id,
                            "product_uom_qty": 1,
                            "price_unit": 15,
                        },
                    )
                ],
            }
        )
        order.action_confirm()
        order.flush()

        return order

    @classmethod
    def _init_timesheet_line(cls):
        timesheet_line = cls.env["account.analytic.line"].create(
            {
                "task_id": cls.task.id,
                "project_id": cls.project.id,
                "date": datetime.now(),
                "name": "My Timesheet",
                "user_id": cls.env.uid,
                "unit_amount": 1,
            }
        )
        timesheet_line.flush()

        return timesheet_line

    def test_create_new_aal_with_so_line(self):
        """
        When the user adds a new Timesheet line (AAL) to log his time on a task
        for a project that was created from a Sale Order, the toggle button
        (is_billable) needs to be checked because the line is linked to a SOL.
        The value of a previous SOL also needs to be filled.
        """

        # Creating a new log linked to that task
        timesheet = self._init_timesheet_line()

        self.assertTrue(timesheet.is_billable)
        self.assertEqual(timesheet.so_line, timesheet.previous_so_line_id)

    def test_create_new_aal_with_so_line_set_unbillable(self):
        """
        When the user clicks on a toggle button to check it as unbillable,
        the system should make Sale Order Item empty and to hold the value of
        previous Sale Order Item in its field.
        :return:
        """

        # Creating a new log linked to that task
        timesheet = self._init_timesheet_line()

        so_line = timesheet.so_line

        # Check it as unbillable
        timesheet.is_billable = False

        self.assertFalse(timesheet.so_line)
        self.assertEqual(so_line, timesheet.previous_so_line_id)

    def test_create_new_aal_with_no_so_line(self):
        """
        The use case he is when there is a task for a Project that is not linked
        to a Sale Order, it will not have a Sale Order Item on it.
        Therefore when a user create a new Timesheet line it wil also be
        without a Sale Order Item. When the user wants to make that line
        billable, the system should raise an Warning telling the user that
        he needs to manually connect it to a Sale Order Item and
        then the system should automatically set the toggle button to billable
        and all proprietary fields to their valid values.
        """

        project = self.env["project.project"].create(
            {
                "name": "My Project",
                "partner_id": self.partner.id,
                "allow_timesheets": True,
                "timesheet_product_id": self.product_task_in_project.id,
            }
        )
        task = self.env["project.task"].create(
            {
                "name": "My Task",
                "project_id": self.project.id,
                "partner_id": self.partner.id,
            }
        )

        timesheet = self.env["account.analytic.line"].create(
            {
                "task_id": task.id,
                "project_id": project.id,
                "date": datetime.now(),
                "name": "My Timesheet",
                "user_id": self.env.uid,
                "unit_amount": 1,
            }
        )

        self.assertFalse(timesheet.is_billable)
        self.assertFalse(timesheet.so_line)
        self.assertFalse(timesheet.previous_so_line_id)

        with self.assertRaises(
            UserError,
            msg="You need to manually specify Sale Order item on the line, "
            "for which you want to link this work log.",
        ):
            timesheet.is_billable = True

        timesheet.so_line = self.order.order_line
        self.assertTrue(timesheet.is_billable)
        self.assertEqual(timesheet.so_line, timesheet.previous_so_line_id)
