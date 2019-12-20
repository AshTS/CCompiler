import targets.demo as language

def convert_register(r):
    if r in language.register_mapping:
        return language.register_mapping[r]

    return r

def call_main():
    result = language.move(convert_register("R1"), 0)
    result += language.move(convert_register("R2"), 0)
    result += language.init_stack()

    result += language.call("_start")
    result += language.call("main")

    result += language.jump("__after")

    return result

def assemble_function(func):
    result = language.set_label(func.name)

    result += language.push_ret()

    for l in func.lines:
        line = func.lines[l]

        for a in func.address_aliases:
            if l == func.address_aliases[a]:
                result += language.set_label(func.name + "_" + a)

        if line.command == "RET":
            result += language.pop_ret()
            result += language.ret()

        elif line.command == "J":
            result += language.jump(func.name + "_" + line.arguments[0]) 

        elif line.command.startswith("MV"):
            result += language.move(convert_register(line.arguments[0]),
                                    convert_register(line.arguments[1]))

        elif line.command.startswith("INIT"):
            result += language.move(convert_register(line.arguments[0]),
                                    convert_register(line.arguments[1]))


        elif line.command.startswith("W"):
            cmd = line.command + "W"
            result += language.write_mem(convert_register(line.arguments[0]),
                                         convert_register(line.arguments[1]),
                                         cmd[1])

        elif line.command == "ADD":
            result += language.add(convert_register(line.arguments[0]),
                                   convert_register(line.arguments[1]),
                                   convert_register(line.arguments[2]))

        elif line.command == "SUB":
            result += language.sub(convert_register(line.arguments[0]),
                                   convert_register(line.arguments[1]),
                                   convert_register(line.arguments[2]))

        elif line.command == "MUL":
            result += language.mul(convert_register(line.arguments[0]),
                                   convert_register(line.arguments[1]),
                                   convert_register(line.arguments[2]))

        elif line.command == "DIV":
            result += language.div(convert_register(line.arguments[0]),
                                   convert_register(line.arguments[1]),
                                   convert_register(line.arguments[2]))

        elif line.command == "BZ":
            result += language.jump_if_zero(func.name + "_" + line.arguments[0],
                                            convert_register(line.arguments[1]))

        elif line.command == "CALL":
            result += language.call(line.arguments[0])

        elif line.command == "BACKUP":
            result += language.push_register(convert_register(line.arguments[0]))

        elif line.command == "RESTORE":
            result += language.pop_register(convert_register(line.arguments[0]))

        elif line.command.startswith("C"):
            result += language.compare(convert_register(line.arguments[0]),
                                       convert_register(line.arguments[1]),
                                       convert_register(line.arguments[2]), line.command[1:])

    return result

def assemble(prog):
    result = call_main()

    for func in prog.functions:
        result += "\n" + language.comment(func.render_name())
        result += assemble_function(func) + "\n"

    result += language.set_label("__after")

    return result + "\n"