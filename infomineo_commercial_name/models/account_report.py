# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

from odoo import api, models


class AccountReport(models.AbstractModel):
    _inherit = "account.report"

    @api.model
    def _get_options_partner_domain(self, options):
        ret = super()._get_options_partner_domain(options)
        if options.get("commercial_names"):
            commercial_name_ids = [
                int(commercial_name) for commercial_name in options["commercial_names"]
            ]
            ret.append(("partner_id.commercial_name_id", "in", commercial_name_ids))
        return ret

    def _init_filter_partner(self, options, previous_options=None):
        ret = super()._init_filter_partner(options, previous_options)
        options["commercial_names"] = (
            previous_options and previous_options.get("commercial_names") or []
        )
        selected_commercial_name_ids = [
            int(commercial_name) for commercial_name in options["commercial_names"]
        ]
        selected_commercial_names = (
            selected_commercial_name_ids
            and self.env["partner.commercial.name"].browse(selected_commercial_name_ids)
            or self.env["partner.commercial.name"]
        )
        options["selected_commercial_name"] = selected_commercial_names.mapped("name")
        return ret

    def _set_context(self, options):
        ret = super()._set_context(options)
        if options.get("commercial_names"):
            ret["commercial_names"] = self.env["partner.commercial.name"].browse(
                [
                    int(commercial_name)
                    for commercial_name in options["commercial_names"]
                ]
            )
        return ret
