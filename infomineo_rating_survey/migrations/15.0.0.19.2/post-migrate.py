# Copyright (C) 2025 Modoolar <http://www.modoolar.com>
# @author Nikola Rabrenovic <nikola.rabrenovic@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html)

import logging
from collections import defaultdict

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    logger = logging.getLogger(__name__)
    logger.info("Post-migrate script started for deduplicating rating.rating")

    env = api.Environment(cr, SUPERUSER_ID, {})
    Rating = env["rating.rating"]

    ratings = Rating.search([], order="id desc")

    grouped = defaultdict(list)
    duplicates = []

    for rating in ratings:
        key = (
            rating.rating_name_to,
            rating.rated_partner_id.id,
            tuple(sorted(rating.rated_partner_ids.ids)),
            rating.partner_id.id,
            rating.parent_res_name,
            rating.res_name,
        )
        grouped[key].append(rating)

    for key, group in grouped.items():
        if len(group) > 1:
            logger.info(f"Found duplicate group key={key} with {len(group)} records")
            to_delete = group[1:]
            deleted_ids = [r.id for r in to_delete]
            logger.info(f"Deleting duplicates: IDs={deleted_ids}")
            duplicates.extend(deleted_ids)

    if duplicates:
        logger.info(f"Total duplicates to delete: {len(duplicates)}")
        Rating.browse(duplicates).unlink()
    else:
        logger.info("No duplicates found.")

    logger.info("Post-migrate script finished: duplicate ratings removed.")
