# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Vojin Maksimovic <vojin.maksimovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)
from odoo import api, fields, models

EMPLOYEE_HISTORY_FIELDS = {
    "hr.employee": [
        "job_location",
        "department_id",
        "hr_team_id",
        "job_title",
        "parent_id",
        "coach_id",
        "company_id",
        "work_location_id",
    ],
}


class EmployeeEmploymentHistory(models.Model):
    _name = "employee.employment.history"
    _description = "Employee Employment History"
    _order = "effective_date_of_change desc"

    employee_id = fields.Many2one(comodel_name="hr.employee")
    effective_date_of_change = fields.Datetime()
    change_reason = fields.Char(string="Reason for the change")
    work_location_id = fields.Many2one(
        string="Job Location", comodel_name="hr.work.location"
    )
    department_id = fields.Many2one(comodel_name="hr.department")
    hr_team_id = fields.Many2one(comodel_name="hr.team")
    job_title = fields.Char()
    job_id = fields.Many2one(comodel_name="hr.job")
    parent_id = fields.Many2one(string="Manager", comodel_name="hr.employee")
    coach_id = fields.Many2one(
        comodel_name="hr.employee",
        string="PDC",
        help="Professional Development Coach",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        related="employee_id.company_id",
    )

    @api.model
    def get_custom_fields(self):
        return [
            "work_location_id",
            "department_id",
            "hr_team_id",
            "job_title",
            "job_id",
            "parent_id",
            "coach_id",
            "company_id",
        ]
