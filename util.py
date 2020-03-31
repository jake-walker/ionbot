"""Various utility functions."""


def text_bar(value: int, max: int, empty_symbol: str = "○",
             full_symbol: str = "●"):
    """Create a text progress bar.

    Args:
        value (int): The current value to be shown on the progress bar.
        max (int): The maximum value that the progress bar goes up to.
        empty_symbol (str, optional): The symbol that is used for an empty
            progress bar section. Defaults to "○".
        full_symbol (str, optional): The symbol that is used for a full
            progress bar section. Defaults to "●".
    """
    output = full_symbol * value

    if (max - value) > 0:
        output += empty_symbol * (max - value)

    output += " ({}/{})".format(value, max)

    return output
