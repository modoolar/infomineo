# COPYRIGHT of Modoolar. See LICENSE file for full copyright and licensing
# details.
from odoo import models


class HrDepartment(models.Model):
    _inherit = "hr.department"

    def name_get(self):
        if not self._context.get("department_with_country_code"):
            return super().name_get()

        return [
            (
                record.id,
                record.name
                + " - "
                + (
                    record.company_id.country_id.name
                    if record.company_id.country_id
                    else ""
                )
                or "",
            )
            for record in self
        ]
