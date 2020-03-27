import os
import sys
from logzero import logger

REQUIRED_CONFIG = ["TOKEN", "DYNMAP_URL"]
CONFIG_PREFIX = "CB_"


def _key_to_var(k):
    return CONFIG_PREFIX + k.replace(" ", "_").upper()


def check_required():
    fail = False

    for key in REQUIRED_CONFIG:
        var = _key_to_var(key)
        if os.getenv(var) is None:
            fail = True
            logger.fatal(("Please make sure that the required environment "
                          "variable '{}' is set!").format(var))

    if fail:
        sys.exit(1)


def get_value(key):
    var = _key_to_var(key)
    return os.getenv(var)
