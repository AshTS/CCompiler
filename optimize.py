import utils


def optimization_remove_NOP(func):
    to_remove = []

    # Tag all NOP instructions for removal
    for key in func.lines:
        line = func.lines[key]
        if line.command == "NOP":
            to_remove.append(line.i)

    # Move all addresses pointing to lines to be removed to the next valid line
    new_address_aliases = {}
    for address_alias in func.address_aliases:
        i = func.address_aliases[address_alias]
        if i not in to_remove:
            new_address_aliases[address_alias] = i
        else:
            new_address_aliases[address_alias] = utils.get_next(i, to_remove, len(func.lines.values()))
        
    func.address_aliases = new_address_aliases

    # Fix next pointers which point to now empty lines
    for line in func.lines.values():
        new_next = []

        for n in line.next_vals:
            i = func.get_address(n)
            if i not in to_remove:
                new_next.append(n)
            else:
                new_i = utils.get_next(i, to_remove, len(func.lines.values()))

                if new_i == utils.get_next(line.i + 1, to_remove, len(func.lines.values())):
                    new_next.append(new_i)
                else:
                    new_next.append(func.get_label_for(new_i))

        line.next_vals = new_next

    # Remove Deleted Lines
    for i in to_remove:
        del func.lines[i]

    # Rename the lines
    new_lines = {}
    i = 0
    for k in sorted(func.lines.keys()):
        new_lines[k] = i
        i += 1

    # Move all addresses to the renamed lines
    new_address_aliases = {}
    for address_alias in func.address_aliases:
        i = func.address_aliases[address_alias]
        new_address_aliases[address_alias] = new_lines[i]
        
    func.address_aliases = new_address_aliases

    # Move all lines to the renamed lines
    new_lines_func = {}
    
    for line in func.lines.values():
        line.i = new_lines[line.i]
        new_lines_func[line.i] = line

        new_next = []

        for n in line.next_vals:
            if n in func.address_aliases:
                new_next.append(n)
            else:
                if n in new_lines:
                    new_next.append(new_lines[n])

        line.next_vals = new_next

    func.lines = new_lines_func

    return func


def optimization_remove_jump_to_next(func):
    for line in func.lines.values():
        if line.command == "J":
            if func.get_address(line.next_vals[0]) == line.i + 1:
                line.command = "NOP"
        elif line.command.startswith("B"):
            if func.get_address(line.next_vals[0]) == line.i + 1 and func.get_address(line.next_vals[1]) == line.i + 1:
                line.command = "NOP"
    return func


def optimization_remove_unused_variables(func):
    for reg in func.assigned_registers + func.free_registers:
        read, write = func.generate_read_write(reg)

        if len(read) == 0:
            for i in write:
                func.lines[i].command = "NOP"

    return func


def optimize_remove_unreachable_code(func):
    paths = func.get_all_paths(0)
    total = []
    for p in paths:
        total += p

    for line in func.lines.values():
        if line.i not in total:
            line.command = "NOP"

    return func


def optimize_function(func):
    last_lines = []

    func = optimization_remove_NOP(func)

    while last_lines != list(func.lines.values()):
        last_lines = list(func.lines.values())

        func = optimize_remove_unreachable_code(func)
        func = optimization_remove_unused_variables(func)
        func = optimization_remove_jump_to_next(func)
        func = optimization_remove_NOP(func)

    return func


def optimize(prog):
    prog.functions = [optimize_function(func) for func in prog.functions]

    return prog
