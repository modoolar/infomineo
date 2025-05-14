# Copyright (C) 2023 Modoolar <http://www.modoolar.com>
# @author Mladen Meseldzija <mladen Meseldzija@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo.addons.rating.models.rating_mixin import RatingMixin as originalRatingMixin


def rating_get_access_token(self, partner=None):
    """Return access token linked to existing ratings, or create a new rating
    that will create the asked token. An explicit call to access rights is
    performed as sudo is used afterwards as this method could be used from
    different sources, notably templates."""
    self.check_access_rights("read")
    self.check_access_rule("read")
    if not partner:
        partner = self.rating_get_partner_id()
    rated_partner = self.rating_get_rated_partner_id()

    # Extracted get/hook method for related ratings
    ratings = self._get_related_ratings(partner)

    if not ratings:
        rating = (
            self.env["rating.rating"]
            .sudo()
            .create(
                {
                    "partner_id": partner.id,
                    "rated_partner_id": rated_partner.id,
                    "res_model_id": self.env["ir.model"]._get_id(self._name),
                    "res_id": self.id,
                    "is_internal": False,
                }
            )
        )
    else:
        rating = ratings[0]
    return rating.access_token


def patch_rating_mixin_methods():
    originalRatingMixin._patch_method(
        "rating_get_access_token", rating_get_access_token
    )
