# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# @author Jelena Bakic <jelena.bakic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    coach_id = fields.Many2one(string="PDC", help="Professional Development Coach")
    hr_team_id = fields.Many2one(comodel_name="hr.team", readonly=True)
    field_of_study_id = fields.Many2one(comodel_name="hr.study.field")
    medical_number = fields.Char()
    reference = fields.Char(readonly=True, index=True)
    work_email = fields.Char(index=True)
    name = fields.Char(index=True)
    full_name = fields.Char()
    short_bio = fields.Html("Short bio")
    probability_of_rehire = fields.Float()

    previous_years_of_experience = fields.Integer(
        string="Previous Years of Experience",
    )
    employee_type = fields.Selection(
        [
            ("employee", "Full Time Employee"),
            ("student", "Part Time Employee"),
            ("trainee", "Intern"),
            ("contractor", "External Contractor"),
            ("freelance", "Fixed Freelancer"),
        ],
    )
    retirement_account_number = fields.Char()
    buddy_id = fields.Many2one(comodel_name="hr.employee")

    @api.depends("address_id")
    def _compute_work_location_id(self):
        super()._compute_work_location_id()
        for employee in self:
            work_location_ids = self.env["hr.work.location"].search(
                [
                    ("address_id", "=", self.address_id.id),
                    ("company_id", "=", self.company_id.id),
                ]
            )
            on_address_location_ids = work_location_ids.filtered(
                lambda x: employee.address_id.country_id.id == x.country_id.id
            )
            employee.work_location_id = (
                on_address_location_ids
                and on_address_location_ids[0].id
                or work_location_ids
                and work_location_ids[0].id
            )

    @api.constrains("probability_of_rehire")
    def _check_probability_of_rehire(self):
        if self.probability_of_rehire > 1 or self.probability_of_rehire < 0:
            raise ValidationError(_("Enter Value Between 0-100."))
