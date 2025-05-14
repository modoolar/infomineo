# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
import logging
from datetime import datetime

from openupgradelib.openupgrade import column_exists

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    """
    We've created a new field gross wage on contract and employee history,
    and we need to migrate data from wage to gross_wage on history.
    """

    logger = logging.getLogger(__name__)
    logger.info(
        "Pre-migrate 15.0.1.9.0 started: " "Migrating data from wage to gross_wage"
    )
    env = api.Environment(cr, SUPERUSER_ID, {})

    migrate_employee_history_data_to_gross_wage(cr)
    calculate_contract_gross_wage(cr, env)

    logger.info(
        "Pre-migrate 15.0.1.9.0 finished: " "Migrating data from wage to gross_wage"
    )


def migrate_employee_history_data_to_gross_wage(cr):
    if column_exists(cr, "employee_employment_history", "gross_wage"):
        cr.execute("UPDATE employee_employment_history SET gross_wage = wage;")


def calculate_contract_gross_wage(cr, env):
    """
    We need to populate gross_wage with the value from the october payslop
    for every Morocco's employees.
    """
    if column_exists(cr, "hr_contract", "gross_wage"):
        morocco_employees = env["hr.employee"].search(
            [("company_id.account_fiscal_country_id.code", "=", "MA")]
        )

        for employee in morocco_employees:
            october_slip = employee.slip_ids.filtered(
                lambda x: x.date_from
                >= datetime.strptime("2022-10-01", "%Y-%m-%d").date()
                and x.date_to <= datetime.strptime("2022-10-31", "%Y-%m-%d").date()
            )

            if october_slip:
                gross_income = october_slip.line_ids.filtered(
                    lambda x: x.code == "GROSS"
                )
                employee.current_contract_id.gross_wage = (
                    gross_income[0].total if gross_income else -1
                )
