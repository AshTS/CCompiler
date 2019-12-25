register_mapping = {"R0": "R13", 
"R1": "R3",
"R2": "R4",
"R3": "R5",
"R4": "R6",
"R5": "R7",
"R6": "R8",
"R7": "R9",
"R8": "R10",
"R9": "R11",
"R10": "R12"}

STRING_DATA_OFFSET = 16

def jump(addr):
    return "J %s\n" % addr


def call(addr):
    return "JL R1, %s\n" % addr


def ret():
    return "J R1\n"


def set_label(label):
    return "%s:\n" % label


def move(dest, source):
    return "ADD %s, R0, %s\n" % (dest, source)


def comment(c):
    return "# %s\n" % c


def write_mem(addr, val, size):
    if size in ["H", "W"]:
        size = "W"

    return "S%s %s, %s\n" % (size, addr, val)


def read_mem(addr, val, size):
    if size in ["H", "W"]:
        size = "W"

    return "R%s %s, %s\n" % (size, addr, val)


def compare(result, arg0, arg1, comparison):
    return "C%s %s, %s, %s\n" % (comparison.upper(), result, arg0, arg1)


def add(result, arg0, arg1):
    if not arg0.startswith("R"):
        return "ADD %s, %s, %s\n" % (result, arg1, arg0)
    return "ADD %s, %s, %s\n" % (result, arg0, arg1)


def sub(result, arg0, arg1):
    return "SUB %s, %s, %s\n" % (result, arg0, arg1)


def mul(result, arg0, arg1):
    if not arg0.startswith("R"):
        return "ADD %s, %s, %s\n" % (result, arg1, arg0)
    return "MUL %s, %s, %s\n" % (result, arg0, arg1)


def div(result, arg0, arg1):
    return "DIV %s, %s, %s\n" % (result, arg0, arg1)


def jump_if_zero(addr, arg):
    return "CE R15, %s, 0\nJF R15, %s\n" % (arg, addr)


def push_register(reg):
    return "SUB R2, R2, 2\nSW R2, %s\n" % reg


def pop_register(reg):
    return "RW %s, R2\nADD R2, R2, 2\n" % reg


def get_register_stack_offset(offset):
    pass


def write_register_stack_offset(offset,reg):
    pass


def push_ret():
    return push_register("R1") + move("R1", "0")


def pop_ret():
    return pop_register("R1")


def init_stack():
    return move("R2", 0x1000)


def add_data(data):
    result = "~"
    
    for d in data:
        result += " %02X" % d

    return result


def initalize():
    total = init_stack()

    total += move("R15", 0xFFFE)
    total += move("R14", 0xF000)
    total += write_mem("R15", "R14", "W")

    return total


def allocate(destination, size):
    total = move("R15", 0xFFFE)
    total += read_mem("R15", "R14", "W")
    total += add("R14", "R14", size)
    total += write_mem("R15", "R14", "W")
    total += sub("R14", "R14", size)
    total += move(destination, "R14")

    return total


def free(loc):
    return ""
