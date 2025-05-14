# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from dateutil.relativedelta import relativedelta

from odoo import _, api, fields, models
from odoo.tools.misc import format_date

from .employee_employment_history import EMPLOYEE_HISTORY_FIELDS


class Employee(models.Model):
    _inherit = "hr.employee"

    tenure = fields.Integer(
        string="Tenure",
        compute="_compute_tenure",
        groups="hr.group_hr_user",
    )
    private_notes = fields.Html(groups="hr.group_hr_manager", translate=True)
    employment_history_ids = fields.One2many(
        comodel_name="employee.employment.history", inverse_name="employee_id"
    )
    hr_team_id = fields.Many2one(comodel_name="hr.team", readonly=False)
    hr_child_team_id = fields.Many2one(
        comodel_name="hr.team", groups="hr.group_hr_user"
    )

    gender = fields.Selection(
        selection_add=[("other", "Diverse")], ondelete={"other": "set null"}
    )

    def _compute_tenure(self):
        for rec in self:
            rec.tenure = (
                relativedelta(fields.Date.today(), rec.first_contract_date).years + 1
            )

    @api.model_create_multi
    def create(self, vals_list):
        result = super().create(vals_list)
        for rec in result:
            rec.generate_reference()
            rec._create_employee_history()

        return result

    def generate_reference(self):
        self.ensure_one()

        self.reference = self.company_id.get_next_employee_sequence()

    def write(self, vals):
        res = super().write(vals)
        for rec in self:
            rec._create_employee_history(vals)

        return res

    def _write(self, vals):
        vals_copy = vals.copy()
        if "work_permit_expiration_date" in vals_copy:
            vals_copy["work_permit_scheduled_activity"] = False
        return super()._write(vals_copy)

    def _create_employee_history(self, vals=None):
        self.ensure_one()

        model_name = self._name
        if model_name not in EMPLOYEE_HISTORY_FIELDS.keys():
            return

        if not vals or any(
            item in EMPLOYEE_HISTORY_FIELDS[model_name] for item in vals
        ):
            employment_history = self.env["employee.employment.history"]
            history_fields = employment_history.get_custom_fields()
            last_entry = employment_history.search([], limit=1, order="id desc")
            if any(self[f_name] != last_entry[f_name] for f_name in history_fields):
                history_vals = self.prepare_employee_employment_history_values(
                    history_fields
                )

                self.env["employee.employment.history"].create(history_vals)

    def prepare_employee_employment_history_values(self, history_fields):
        self.ensure_one()

        employment_values = {
            "employee_id": self.id,
            "effective_date_of_change": fields.Datetime.now(),
        }
        employment_values.update(
            {
                f_name: (
                    self[f_name].id
                    if self._fields[f_name].type == "many2one"
                    else self[f_name]
                )
                for f_name in history_fields
            }
        )
        return employment_values

    @api.model
    def _cron_check_work_permit_validity(self):
        """
        Overridden Odoo's cron to fix error of browsing res.partner table
        with id of a user (should be res.users table instead)
        """
        # Called by a cron
        # Schedule an activity 1 month before the work permit expires
        outdated_days = fields.Date.today() + relativedelta(months=+1)
        nearly_expired_work_permits = self.search(
            [
                ("work_permit_scheduled_activity", "=", False),
                ("work_permit_expiration_date", "<", outdated_days),
            ]
        )
        employees_scheduled = self.env["hr.employee"]
        for employee in nearly_expired_work_permits.filtered(
            lambda employee: employee.parent_id
        ):
            responsible_user_id = employee.parent_id.user_id.id
            if responsible_user_id:
                employees_scheduled |= employee
                # Changed this line res.partner to res.users
                lang = self.env["res.users"].browse(responsible_user_id).lang
                formated_date = format_date(
                    employee.env,
                    employee.work_permit_expiration_date,
                    date_format="dd MMMM y",
                    lang_code=lang,
                )
                employee.activity_schedule(
                    "mail.mail_activity_data_todo",
                    note=_(
                        "The work permit of %(employee)s expires at %(date)s.",
                        employee=employee.name,
                        date=formated_date,
                    ),
                    user_id=responsible_user_id,
                )
        employees_scheduled.write({"work_permit_scheduled_activity": True})
