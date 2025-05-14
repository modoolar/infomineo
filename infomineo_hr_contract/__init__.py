from . import models
from .hooks import post_load


def are_we_in_test_mode():
    from odoo.tools import config

    return config.get("test_enable") or config.get("test_file")


if are_we_in_test_mode():
    from . import test_models
    import logging

    logging.getLogger(__name__).debug("Imported test modules")
