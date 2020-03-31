"""Configuration for the bot."""

import os
import sys
from logzero import logger

# List of required config variables
REQUIRED_CONFIG = ["TOKEN", "DYNMAP_URL"]
# The prefix set before environment variables
CONFIG_PREFIX = "CB_"


def _key_to_var(k):
    return CONFIG_PREFIX + k.replace(" ", "_").upper()


def check_required():
    """Function to check that all the required config variables are set."""
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
    """Get a configuration environment variable.

    Args:
        key (str): The name of the configuration variable to get the value of.

    Returns:
        str: The value of the environment variable.
    """
    var = _key_to_var(key)
    return os.getenv(var)
