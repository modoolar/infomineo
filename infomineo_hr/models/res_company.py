# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import _, fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    employee_sequence_id = fields.Many2one(
        comodel_name="ir.sequence", index=True, readonly=True
    )

    def get_next_employee_sequence(self):
        self.ensure_one()

        if not self.employee_sequence_id:
            self._create_employee_sequence()

        return self.employee_sequence_id.next_by_id()

    def _create_employee_sequence(self):
        self.ensure_one()
        self.employee_sequence_id = (
            self.env["ir.sequence"]
            .sudo()
            .create(self._prepare_employee_sequence_data())
        )

    def _prepare_employee_sequence_data(self):
        self.ensure_one()
        return {
            "name": "{} {}".format(self.name, _("Employee sequence")),
            "implementation": "standard",
            "code": f"res.company.employee.sequence.code.{self.id}",
            "prefix": f"{self.id}",
            "padding": 3,
            "use_date_range": False,
            "number_increment": 1,
            "number_next_actual": 1,
        }
