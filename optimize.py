def optimization_remove_NOP(func):
    for key in func.lines:
        line = func.lines[key]

        if line.command == "NOP":
            print(line)

    return func

def optimize_function(func):
    last_lines = []

    while last_lines != list(func.lines.values()):
        func = optimization_remove_NOP(func)

        last_lines = list(func.lines.values())

    return func


def optimize(prog):
    prog.functions = [optimize_function(func) for func in prog.functions]

    return prog
