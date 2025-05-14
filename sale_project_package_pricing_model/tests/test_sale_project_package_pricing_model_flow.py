# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from datetime import datetime

from odoo.exceptions import UserError
from odoo.tests import Form, TransactionCase


class TestSaleProjectPackagePricingModelFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        """
        Using a demo SO Template and adding a product, that creates
        a Project with a Task, on it. We will create a SO using
        that Template which will create a Project and a Task Related to it.
        """
        super(TestSaleProjectPackagePricingModelFlow, cls).setUpClass()

        cls.package_configuration_line_hours = (
            cls.init_package_configuration_line_words()
        )
        cls.package_configuration_line_words = (
            cls.init_package_configuration_line_hours()
        )

        cls.so_template = cls._init_so_template()

        cls.partner = cls.env.ref("base.res_partner_1")

        cls.order = cls.init_sale_order()
        cls.project = cls.order.order_line.project_id
        cls.task = cls.project.task_ids[0]

    @classmethod
    def init_package_configuration_line_words(cls):
        return cls.env["sale.package.configurator.line"].create(
            cls._prepare_configurator_line_values("generic_words", "words")
        )

    @classmethod
    def init_package_configuration_line_hours(cls):
        return cls.env["sale.package.configurator.line"].create(
            cls._prepare_configurator_line_values("generic_hours", "hours")
        )

    @classmethod
    def _prepare_configurator_line_values(cls, package_line_of_business, reference_uom):
        return {
            "sale_package_configurator_id": cls.env.ref(
                "sale_package_pricing_model.sale_package_configurator_1"
            ).id,
            "package_line_of_business": package_line_of_business,
            "consumption_rate": 10,
            "consumption_points": 1,
            "reference_uom": reference_uom,
        }

    @classmethod
    def _init_so_template(cls):
        product_task_in_project = cls.env["product.product"].create(
            {
                "name": "Task in Project Service",
                "type": "service",
                "service_tracking": "task_in_project",
            }
        )

        so_template = cls.env.ref(
            "sale_package_pricing_model.sale_order_template_package"
        )

        so_template.write(
            {
                "sale_order_template_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": product_task_in_project.name,
                            "product_id": product_task_in_project.id,
                            "product_uom_id": product_task_in_project.uom_id.id,
                            "product_uom_qty": 1,
                        },
                    )
                ],
            }
        )

        return so_template

    @classmethod
    def init_sale_order(cls):
        with Form(
            cls.env["sale.order"].with_context(default_partner_id=cls.partner.id)
        ) as form:
            form.sale_order_template_id = cls.so_template
            order = form.save()
            order.action_confirm()
            order.flush()

            return order

    @classmethod
    def _init_timesheet_line(cls, task):
        timesheet_line = cls.env["account.analytic.line"].create(
            {
                "task_id": task.id,
                "project_id": task.project_id.id,
                "date": datetime.now(),
                "name": "My Timesheet",
                "user_id": cls.env.uid,
                "unit_amount": 1,
            }
        )
        timesheet_line.flush()

        return timesheet_line

    def test_same_so_item_task_aal(self):
        """
        We will create a new SO that will create a new Task
        we will then remove SO Item from the Timesheet Line and
        try to add a SO Item from the previously created SO which
        will raise a constrain that we need to have the same SO Item
        on both Task and its Timesheet Lines.
        """

        new_order = self.init_sale_order()
        task = new_order.order_line.project_id.task_ids[0]
        timesheet_line = self._init_timesheet_line(task)

        # SO Item should be on both objects
        self.assertTrue(timesheet_line.so_line)
        self.assertTrue(task.sale_line_id)

        timesheet_line.so_line = False

        with self.assertRaisesRegex(
            UserError, "The Sale Order Item must be the same as on the Task."
        ):
            timesheet_line.with_context(
                sale_project_package_pricing_model_test=True
            ).so_line = self.task.sale_line_id

    def test_generic_words_type_task(self):
        """
        The default Task is going to be of type `generic_words`. We will then
        log a few Timesheet Lines on it to see whether the calculation of the
        consumed and forecasted points will remain the same. Also we will test
        the validity of the calculation based on the configuration lines, on
        the Task, Project, SO Line and Sale Order.
        """
        self.task.line_of_business = "generic_words"

        # On configuration line is set 10 words are valued 1 points
        # if we set translated_words on Task to be 1000, system should
        # calculate 1000*1/10 = 100
        self.task.translated_words = 2000
        self.assertEqual(self.task.consumed_points, 200)
        self.assertEqual(self.task.forecasted_consumed_points, 200)

        former_consumed_points = self.task.consumed_points
        former_forecasted_consumed_points = self.task.forecasted_consumed_points

        self._init_timesheet_line(self.task)
        self._init_timesheet_line(self.task)

        self.assertEqual(self.task.consumed_points, former_consumed_points)
        self.assertEqual(
            self.task.forecasted_consumed_points, former_forecasted_consumed_points
        )

        # We are going manually set consumed points to 100 and validate
        # that the forecasted points remain the same
        self.task.consumed_points = 100
        self.assertNotEqual(
            self.task.consumed_points,
            former_consumed_points,
            "Consumed Points must be different.",
        )
        self.assertEqual(
            self.task.forecasted_consumed_points, former_forecasted_consumed_points
        )

        # We will input 500 translated words and system should recalculate
        # consumed and forecasted to 50
        self.task.translated_words = 500
        self.assertEqual(self.task.consumed_points, 50)
        self.assertEqual(self.task.forecasted_consumed_points, 50)

        # Project consumed points need to be the same as on the task
        self.assertEqual(self.project.consumed_points_count, self.task.consumed_points)

        # Sale Order Line consumed points need to be the same as on the Project
        self.assertEqual(
            self.order.order_line[0].consumed_points, self.task.consumed_points
        )

        # Sale Order consumed points need to be the same as on the Project
        self.assertEqual(self.order.consumed_points_count, self.task.consumed_points)

    def test_generic_hours_type_task(self):
        """
        The default Task is going to be of type `generic_hours`. We will then
        log a few Timesheet Lines on it to see whether the calculation of the
        consumed and forecasted points change. Also we will test
        the validity of the calculation based on the configuration lines, on
        the Task, Project, SO Line and Sale Order.
        """
        self.task.line_of_business = "generic_hours"

        timesheet_1 = self._init_timesheet_line(self.task)
        timesheet_2 = self._init_timesheet_line(self.task)

        # We logged 30 hours which should translate to 30*1/10=3 consumed points
        timesheet_1.write({"unit_amount": 10})
        timesheet_2.write({"unit_amount": 20})

        self.assertEqual(self.task.consumed_points, 3)
        self.assertEqual(self.task.forecasted_consumed_points, 3)

        # We are going to set manually consumed points to 100 and validate
        # that the forecasted points remain the same
        former_consumed_points = self.task.consumed_points
        former_forecasted_consumed_points = self.task.forecasted_consumed_points

        self.task.consumed_points = 100
        self.assertNotEqual(
            self.task.consumed_points,
            former_consumed_points,
            "Consumed Points must be different.",
        )
        self.assertEqual(
            self.task.forecasted_consumed_points, former_forecasted_consumed_points
        )

        # We will change hours on lines from 30 to 60 hours
        # which should translate to 60*1/10=6 consumed points
        timesheet_1.write({"unit_amount": 20})
        timesheet_2.write({"unit_amount": 40})
        self.assertEqual(self.task.consumed_points, 6)
        self.assertEqual(self.task.forecasted_consumed_points, 6)

        # Project consumed points need to be the same as on the task
        self.assertEqual(self.project.consumed_points_count, self.task.consumed_points)

        # Sale Order consumed points need to be the same as on the Project
        self.assertEqual(self.order.consumed_points_count, self.task.consumed_points)

        # Sale Order Line consumed points need to be the same as on the Project
        self.assertEqual(
            self.order.order_line[0].consumed_points, self.task.consumed_points
        )
