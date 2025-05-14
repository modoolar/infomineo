# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from odoo import models

from .rating import (
    RATING_LIMIT_BAD,
    RATING_LIMIT_GOOD,
    RATING_LIMIT_OK,
    RATING_LIMIT_SATISFIED,
)


class RatingParentMixin(models.AbstractModel):
    _inherit = "rating.parent.mixin"

    def rating_get_grades(self, domain=None):
        data = self._rating_get_repartition(domain=domain)
        res = dict.fromkeys(["great", "good", "okay", "not okay", "bad"], 0)
        for key in data:
            if key >= RATING_LIMIT_SATISFIED:
                res["great"] += data[key]
            elif key >= RATING_LIMIT_GOOD:
                res["good"] += data[key]
            elif key >= RATING_LIMIT_OK:
                res["okay"] += data[key]
            elif key >= RATING_LIMIT_BAD:
                res["not okay"] += data[key]
            else:
                res["bad"] += data[key]
        return res
