import settings

CLEAR = u"\u001b[0m"

YELLOW = u"\u001b[33;1m"
BLUE = u"\u001b[34;1m"
CYAN = u"\u001b[36;1m"
MAGENTA = u"\u001b[35;1m"
GREEN = u"\u001b[32;1m"
RED = u"\u001b[31;1m"

__CURRENT__ = CLEAR

def change_color(color):
    global __CURRENT__

    if color != __CURRENT__:
        __CURRENT__ = color
        if settings.USE_COLORS:
            print(color)


def render_value(val):
    val = str(val)

    if not settings.USE_COLORS:
        return val

    if val == "":
        return val

    try:
        int(val)
        return BLUE + val + CLEAR
    except ValueError:
        pass

    if val == ",":
        return val

    if "," in val:
        return ",".join([render_value(v) for v in val.split(",")])
        

    if val.startswith("R"):
        for c in val:
            if c.isnumeric():
                return CYAN + val + CLEAR
        return MAGENTA + val + CLEAR

    for c in val:
        if c.isnumeric():
            return GREEN + val + CLEAR

    if val.upper() == val:
        return MAGENTA + val + CLEAR

    return GREEN + val + CLEAR