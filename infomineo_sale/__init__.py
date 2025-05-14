# Copyright (C) 2021 Modoolar <http://www.modoolar.com>
# @author Andreja Bicanin <andreja.bicanin@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).
from . import models


def are_we_in_test_mode():
    from odoo.tools import config

    return config.get("test_enable") or config.get("test_file")


if are_we_in_test_mode():
    from . import test_models
    import logging

    logging.getLogger(__name__).debug("Imported test models")
