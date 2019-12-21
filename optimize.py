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
                line.arguments = []
        elif line.command.startswith("B") and line.command != "BACKUP":
            if func.get_address(line.next_vals[0]) == line.i + 1 and func.get_address(line.next_vals[1]) == line.i + 1:
                line.command = "NOP"
                line.arguments = []
    return func


def optimization_remove_unused_variables(func):
    for reg in func.assigned_registers + func.free_registers:
        read, write = func.generate_read_write(reg)
        
        if len(read) == 0:
            for i in write:
                func.lines[i].command = "NOP"
                func.lines[i].arguments = []

    return func


def optimize_remove_unreachable_code(func):
    paths = func.get_all_paths(0)
    total = []
    for p in paths:
        total += p

    for line in func.lines.values():
        if line.i not in total:
            line.command = "NOP"
            line.arguments = []

    return func


def optimize_empty_initalizations(func):
    for line in func.lines.values():
        if line.command != "INIT":
            continue

        paths = func.get_all_paths(line.i)

        reg = line.arguments[0]
        read, write = func.generate_read_write(reg)

        inited_after = []

        for path in paths:
            for p in path[1:]:
                if func.lines[p].command == "INIT":
                    inited_after.append(func.lines[p].arguments[0])
                if p in read:
                    break
                if p in write:
                    if func.lines[p].command == "MV" and func.lines[p].arguments[1] not in inited_after:
                        line.arguments[1] = func.lines[p].arguments[1]
                        func.lines[p].command = "NOP"
                        func.lines[p].arguments = []

    return func


def optimize_unused_writes(func):
    for line in func.lines.values():
        if line.command in ["RESTORE", "INIT", "CALL"]:
            continue

        if len(line.arguments) == 0 or not line.arguments[0].startswith("R"):
            continue

        reg = line.arguments[0]
        read, write = func.generate_read_write(reg)

        if line.i not in write:
            continue

        paths = func.get_all_paths(line.i)

        can_replace = True

        for path in paths:
            for p in path[1:]:
                if p in read:
                    can_replace = False
                if p in write:
                    break

        if can_replace:
            line.command = "NOP"
            line.arguments = []


    return func


def optimize_backing_up_registers(func):
    for line in func.lines.values():
        if line.command == "BACKUP":
            i = line.i

            while not (func.lines[i].command == "RESTORE" and func.lines[i].arguments == line.arguments):
                i += 1

            reads, _ = func.generate_read_write(line.arguments[0])

            paths = func.get_all_paths(i)

            is_read_later = False

            for path in paths:
                for p in path:
                    if p in reads:
                        is_read_later = True

            if not is_read_later:
                line.command = "NOP"
                line.arguments = []

                func.lines[i].command = "NOP"
                func.lines[i].arguments = []

    return func


def optimize_move_chain(func):
    for line in func.lines.values():
        if line.command not in ["INIT", "MV"]:
            continue
        
        paths = func.get_all_paths(line.i)

        reg = line.arguments[0]
        val = line.arguments[1]
        read, write = func.generate_read_write(reg)

        inited_after = []

        if val.startswith("R") or val.startswith("G"):
            continue

        for path in paths:
            for p in path[1:]:
                if func.lines[p].command == "INIT":
                    inited_after.append(func.lines[p].arguments[0])
                if p in read:
                    if func.lines[p].command in ["INIT", "MV"]:
                        if len(func.lines[p].arguments) > 1 and func.lines[p].arguments[1] == reg:
                            func.lines[p].arguments[1] = val
                if p in write:
                    break


    return func


def optimize_function(func):
    last_lines = []

    func = optimization_remove_NOP(func)

    while last_lines != list(func.lines.values()):
        last_lines = list(func.lines.values())

        func = optimize_backing_up_registers(func)
        func = optimization_remove_NOP(func)

        func = optimize_move_chain(func)
        func = optimization_remove_NOP(func)

        func = optimize_empty_initalizations(func)
        func = optimization_remove_NOP(func)

        func = optimize_unused_writes(func)
        func = optimization_remove_NOP(func)

        func = optimize_backing_up_registers(func)
        func = optimization_remove_NOP(func)

        func = optimize_remove_unreachable_code(func)
        func = optimization_remove_NOP(func)

        func = optimization_remove_unused_variables(func)
        func = optimization_remove_NOP(func)

        func = optimization_remove_jump_to_next(func)
        func = optimization_remove_NOP(func)

    return func


def optimize(prog):
    prog.functions = [optimize_function(func) for func in prog.functions]

    return prog
