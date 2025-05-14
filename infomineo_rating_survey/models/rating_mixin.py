# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen.meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import api, models


class RatingMixin(models.AbstractModel):
    _inherit = "rating.mixin"

    @api.depends("rating_ids.res_id", "rating_ids.rating")
    def _compute_rating_stats(self):
        ret = super()._compute_rating_stats()
        return ret

    def _get_related_ratings(self, partner):
        if not self._context.get("rating_email", None):
            return self.rating_ids.sudo().filtered(
                lambda x: x.partner_id.id == partner.id and not x.consumed
            )

        email_to = self._context.get("rating_email", None)

        return self.rating_ids.sudo().filtered(
            lambda x: x.rating_email_to == email_to and not x.consumed
        )
