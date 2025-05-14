# Copyright (C) 2022 Modoolar <http://www.modoolar.com>
# @author Dejan Mirosavljevic <dejan.mirosavljevic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

import base64

from odoo import api, fields, models
from odoo.modules.module import get_resource_path

RATING_LIMIT_SATISFIED = 5
RATING_LIMIT_GOOD = 4
RATING_LIMIT_OK = 3
RATING_LIMIT_BAD = 2
RATING_LIMIT_MIN = 1


class Rating(models.Model):
    _inherit = "rating.rating"

    rating_text = fields.Selection(
        selection_add=[
            ("good", "2- satisfied"),
            ("bad", "4- dissatisfied"),
            ("top", "1- very satisfied"),
            ("ok", "3- neutral"),
            ("ko", "5- very dissatisfied"),
        ]
    )

    def _compute_rating_image(self):
        for rating in self:
            try:
                image_path = get_resource_path(
                    "infomineo_rating",
                    "static/src/img",
                    rating._get_rating_image_filename(),
                )
                rating.rating_image = (
                    base64.b64encode(open(image_path, "rb").read())
                    if image_path
                    else False
                )
            except OSError:
                rating.rating_image = False

    def _get_rating_image_filename(self):
        self.ensure_one()
        if self.rating >= RATING_LIMIT_SATISFIED:
            rating_int = 5
        elif self.rating >= RATING_LIMIT_GOOD:
            rating_int = 4
        elif self.rating >= RATING_LIMIT_OK:
            rating_int = 3
        elif self.rating >= RATING_LIMIT_BAD:
            rating_int = 2
        elif self.rating >= RATING_LIMIT_MIN:
            rating_int = 1
        else:
            rating_int = 0
        return "rating_%s.png" % rating_int

    @api.depends("rating")
    def _compute_rating_text(self):
        for rating in self:
            if rating.rating >= RATING_LIMIT_SATISFIED:
                rating.rating_text = "top"
            elif rating.rating >= RATING_LIMIT_GOOD:
                rating.rating_text = "good"
            elif rating.rating >= RATING_LIMIT_OK:
                rating.rating_text = "ok"
            elif rating.rating >= RATING_LIMIT_BAD:
                rating.rating_text = "bad"
            elif rating.rating >= RATING_LIMIT_MIN:
                rating.rating_text = "ko"
            else:
                rating.rating_text = "none"
