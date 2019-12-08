def optimization_remove_NOP(func):
    to_remove = []
    prev = {}
    for line in func.lines.values():
        for n in line.next_vals:
            a = func.get_address(n)

            if a in prev:
                prev[a].append(line.i)
            else:
                prev[a] = [line.i]

    for key in func.lines:
        line = func.lines[key]

        if line.command == "NOP":
            for prev_i in prev[line.i] if line.i in prev else []:
                new = []
                for val in func.lines[prev_i].next_vals:
                    if func.get_address(val) == line.i:
                        new.append(line.next_vals[0])
                    else:
                        new.append(val)


                func.lines[prev_i].next_vals = new
                
            to_remove.append(line.i)

    for i in to_remove:
        del func.lines[i]


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
