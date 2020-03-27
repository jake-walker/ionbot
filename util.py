def text_bar(value: int, max: int, empty_symbol: str = "○",
             full_symbol: str = "●"):
    output = full_symbol * value

    if (max - value) > 0:
        output += empty_symbol * (max - value)

    output += " ({}/{})".format(value, max)

    return output
