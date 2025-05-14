# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from odoo import api, fields, models


class HolidaysRequest(models.Model):
    _inherit = "hr.leave"

    active_employee = fields.Boolean(store=True)

    @api.model
    def read_group(
        self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True
    ):
        result = super().read_group(
            domain,
            fields,
            groupby,
            offset=offset,
            limit=limit,
            orderby=orderby,
            lazy=lazy,
        )
        if "active_employee" not in groupby:
            return result

        for entry in filter(lambda r: "active_employee" in r, result):
            entry["active_employee"] = (
                "Active" if entry["active_employee"] else "Archive"
            )
        return result
