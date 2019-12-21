import utils
import defines
import colors

#
#   Note: For Conversion, This is Little Endian for RAM Storage
#

global_register_aliases = {}

class Line:
    def __init__(self, command, arguments, i, next_vals, program):
        self.command = command
        self.arguments = arguments
        self.i = i
        self.next_vals = next_vals

        self.program = program

        # Fix Possible argument order issues
        if len(self.arguments) > 2 and command in ["ADD", "MUL"]:
            if self.arguments[2].startswith("R") and not self.arguments[1].startswith("R"):
                self.arguments = [self.arguments[0], self.arguments[2], self.arguments[1]]

    def __repr__(self):
        alias = ""

        for k in self.program.address_aliases:
            if self.program.address_aliases[k] == self.i:
                alias += k + ": "

        result =  "%03i %s %s %s%s" % (self.i,
                                            alias.ljust(10),
                                            self.command.rjust(8),
                                            ", ".join([(str(arg)).rjust(5) for arg in self.arguments]).ljust(20),
                                            (", ".join([str(n) for n in self.next_vals]).ljust(10)))

        return " ".join([colors.render_value(val) for val in result.split(" ")])


class Function:
    def __init__(self, name, arguments, ret_type, prog):
        self.current_line = 0
        self.lines = {}

        self.assigned_registers = []
        self.free_registers = []
        self.last_register = 0

        self.assigned_global = []
        self.free_global = []
        self.last_global = 0

        self.last_label = 0

        self.address_aliases = {}

        self.name = name

        self.arguments = arguments
        self.ret_type = ret_type

        self.register_sizes = {}
        self.pointer_register_sizes = {}

        self.aliased_registers = {}
        self.return_register = self.request_register()
        self.aliased_registers["__RETURN"] = self.return_register
        self.register_sizes[self.return_register] = utils.get_size_of_type(self.ret_type)

        self.program = prog

        for arg in self.arguments:
            self.define_variable(arg[1], arg[0], True)

        self.pointer_registers = []

    def get_all_paths(self, start):
        hit = []

        start = self.get_address(start)

        paths = [[start]]
        heads = [start]

        while len(heads) > 0:
            heads = []

            new_paths = []
            for path in paths:
                if path[-1] not in hit:
                    heads.append(path[-1])

                    hit.append(path[-1])

                    for n in self.lines[path[-1]].next_vals:
                        new_path = path + [self.get_address(n)]
                        new_paths.append(new_path)

                    if len(self.lines[path[-1]].next_vals) == 0:
                        new_paths.append(path)
                else:
                    new_paths.append(path)

            paths = new_paths

        return paths


    def generate_read_write(self, reg):
        read = []
        write = []
        for line in self.lines.values():

            if line.command == "CALL":
                if reg == "R0":
                    write.append(line.i)

                func = line.arguments[0]
                num = 1

                for f in self.program.functions:
                    if f.name == func:
                        num = len(f.arguments)

                if reg.startswith("R") and int(reg[1:]) > 0 and int(reg[1:]) <= num: #=======================
                    read.append(line.i)

                continue

            if line.command == "RET":
                if reg == "R0":
                    read.append(line.i)

            # Instructions with no arguments
            if len(line.arguments) == 0:
                continue

            if line.command == "BACKUP" and line.arguments[0] == reg:
                read.append(line.i)
                continue

            if line.command == "RESTORE" and line.arguments[0] == reg:
                write.append(line.i)
                continue

            if line.command in ["W", "WB", "WH"] and reg in line.arguments:
                read.append(line.i)
                continue

            if reg in line.arguments[1:]:
                read.append(line.i)

            # Jump or Branch instructions
            if line.arguments[0] in self.address_aliases:
                continue

            if line.arguments[0] == reg:
                write.append(line.i)

        return read, write


    def get_address(self, addr):
        if addr in self.address_aliases:
            return self.address_aliases[addr]

        return int(addr)

    def get_label_for(self, i):
        for key in self.address_aliases:
            if self.address_aliases[key] == i:
                return key

        else:
            l = self.request_label()
            self.address_aliases[int(i)] = l

            return l

    def get_previous_lines(self, line):
        pass

    def render_name(self):
        return self.ret_type + " " + self.name + "(" + ", ".join(["%s %s" % tuple(v) for v in self.arguments]) + ")"

    def add_line(self, command, arguments, next_vals=None, include_next=True):
        if next_vals is None:
            next_vals = []
        self.lines[self.current_line] = Line(command, arguments, self.current_line, next_vals + ([self.current_line + 1] if include_next else []), self)
        self.current_line += 1

    def request_label(self):
        label = "L%i" % self.last_label
        self.last_label += 1

        return label

    def place_label(self, label=None):
        if label is None:
            label = "L%i" % self.last_label
            self.last_label += 1

        self.address_aliases[label] = self.current_line
        return label

    def define_variable(self, var_name, var_type, is_arg=False):
        self.aliased_registers[var_name] = self.request_register(is_arg)
        self.register_sizes[self.aliased_registers[var_name]] = utils.get_size_of_type(var_type)

    def define_global_variable(self, var_name, var_type):
        self.aliased_registers[var_name] = self.request_global()
        self.register_sizes[self.aliased_registers[var_name]] = utils.get_size_of_type(var_type)

    def assign_variable(self, var_name, other):
        if var_name in self.aliased_registers:
            reg = self.aliased_registers[var_name]
        else:
            reg = var_name

        if reg in self.pointer_registers:
            if other.startswith("R"):
                s = defines.suffix_by_size[self.register_sizes[other]]
            else:
                s = "W"

            if reg in self.pointer_register_sizes:
                s = defines.suffix_by_size[self.pointer_register_sizes[reg]]

            self.add_line("W" + s, [reg, other])

            return 

        self.add_line("MV" + defines.suffix_by_size[self.register_sizes[reg]], [reg, other])

        if other in self.pointer_register_sizes:
            self.pointer_register_sizes[reg] = self.pointer_register_sizes[other]

    def clear_variable(self, var_name):
        if var_name in self.aliased_registers:
            reg = self.aliased_registers[var_name]
        else:
            reg = var_name
        
        self.add_line("MV", [reg, "0"])

    def init_variable(self, var_name):
        if var_name in self.aliased_registers:
            reg = self.aliased_registers[var_name]
        else:
            reg = var_name

        self.add_line("INIT", [reg, "0"])

    def request_register(self, is_arg=False):
        if len(self.free_registers) > 0:
            v, *self.free_registers = self.free_registers
            self.assigned_registers.append(v)
        else:
            self.last_register += 1

            self.assigned_registers.append("R%i" % (self.last_register - 1))

        self.register_sizes[self.assigned_registers[-1]] = 4
        # self.pointer_register_sizes[self.assigned_registers[-1]] = 4

        if not is_arg:
            self.init_variable(self.assigned_registers[-1])

        return self.assigned_registers[-1]

    def request_global(self):
        if len(self.free_global) > 0:
            v, *self.free_global = self.free_global
            self.assigned_global.append(v)
        else:
            self.last_global += 1

            self.assigned_global.append("G%i" % (self.last_global - 1))

        self.register_sizes[self.assigned_global[-1]] = 4

        self.init_variable(self.assigned_global[-1])

        return self.assigned_global[-1]

    def add_return(self):
        self.address_aliases["ret"] = self.current_line
        self.add_line("RET", [])

    def add_jump(self, addr):
        self.add_line("J", [addr], [addr], False)

    def add_conditional_jump(self, inst, addr, cond):
        self.add_line(inst, [addr, cond], [addr])

        
    def __repr__(self):
        return colors.CLEAR + colors.CLEAR + self.ret_type + " " + self.name + "(" + ", ".join(["%s %s" % tuple(v) for v in self.arguments]) + ")" + ":  \n" + "\n".join([str(self.lines[k]) for k in self.lines])

class Program:
    def __init__(self, functions=None):
        self.functions = [] if functions is None else functions

    def add_function(self, function):
        function.program = self
        self.functions.append(function)

    def __repr__(self):
        return "\n\n".join([str(f) for f in self.functions])


def generate_expression(tree, func, left=False):
    if tree.data == "Integer":
        r = func.request_register()
        func.assign_variable(r, tree.children[0].data)
        return r
    elif tree.data == "Char":
        return str(ord(tree.children[0].data[1:-1]))
    elif tree.data == "String":
        return tree.children[1].data

    elif tree.data == "Deref":
        arg0 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        if left:
            func.assign_variable(new_reg, arg0)
            func.pointer_registers.append(new_reg)
        else:
            func.add_line("RW", [new_reg, arg0])

        return new_reg

    elif tree.data == "Cast":
        arg0 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()
        func.register_sizes[new_reg] = utils.get_size_of_type(tree.children[0].data)

        if tree.children[0].data.endswith("*"):
            func.pointer_register_sizes[new_reg] = utils.get_size_of_type(tree.children[0].data[:-1])

        func.assign_variable(new_reg, arg0)

        return new_reg

    # Math Operations

    elif tree.data == "Addition":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("ADD", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "Subtraction":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("SUB", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "Multiply":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("MUL", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "Divide":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("DIV", [new_reg, arg0, arg1])
        return new_reg

    # Assignment and Paired Operations

    elif tree.data == "Assignment":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        func.assign_variable(arg0, arg1)

        return arg1

    elif tree.data == "AddEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("ADD", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "SubtractEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("SUB", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "MultiplyEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("MUL", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "DivideEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("DIV", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "AndEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("AND", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "OrEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("OR", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "XorEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("XOR", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "ShiftLeftEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("RLL", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    elif tree.data == "ShiftRightEqual":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("RRL", [new_reg, arg0, arg1])

        func.assign_variable(arg0, new_reg)
        return new_reg

    # Comparison Operations

    elif tree.data == "Equal":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CE", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "NotEqual":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CNE", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "LessThan":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CL", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "GreaterThan":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CNLE", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "LessThanEqual":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CLE", [new_reg, arg0, arg1])
        return new_reg

    elif tree.data == "GreaterThanEqual":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("CNL", [new_reg, arg0, arg1])
        return new_reg

    # Increment and Decrement Ops

    elif tree.data == "PostInc":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("ADD", [new_reg, arg1, 1])

        func.assign_variable(arg0, new_reg)

        return arg1

    elif tree.data == "PostDec":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("SUB", [new_reg, arg1, 1])

        func.assign_variable(arg0, new_reg)

        return arg1

    elif tree.data == "PreInc":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("ADD", [new_reg, arg1, 1])

        func.assign_variable(arg0, new_reg)

        return new_reg

    elif tree.data == "PreDec":
        arg0 = generate_expression(tree.children[0], func, True)
        arg1 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("SUB", [new_reg, arg1, 1])

        func.assign_variable(arg0, new_reg)

        return new_reg

    # Subscript Operation

    elif tree.data == "Subscript":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("ADD", [new_reg, arg0, arg1])

        if left:
            func.pointer_registers.append(new_reg)
        else:
            func.add_line("RW", [new_reg, new_reg])

        return new_reg

    # Unary Operations

    elif tree.data == "UnaryPlus":
        return generate_expression(tree.children[0], func)

    elif tree.data == "UnaryMinus":
        arg0 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("NOT", [new_reg, arg1])
        func.add_line("ADD", [new_reg, new_reg, "1"])

        return new_reg

    # Shift Operations

    elif tree.data == "ShiftLeft":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("RLL", [new_reg, arg0, arg1])

        return new_reg

    elif tree.data == "ShiftRight":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("RLL", [new_reg, arg0, arg1])

        return new_reg

    # Bitwise Operations

    elif tree.data == "BitwiseNot":
        arg0 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("NOT", [new_reg, arg1])

        return new_reg

    elif tree.data == "BitwiseAnd":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("AND", [new_reg, arg0, arg1])

        return new_reg

    elif tree.data == "BitwiseOr":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("OR", [new_reg, arg0, arg1])

        return new_reg

    elif tree.data == "BitwiseXor":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()

        func.add_line("XOR", [new_reg, arg0, arg1])

        return new_reg

    # Logical Operations

    elif tree.data == "LogicalNot":
        arg0 = generate_expression(tree.children[0], func)

        new_reg = func.request_register()

        func.add_line("CNE", [new_reg, arg1, "0"])
        func.add_line("NOT", [new_reg, new_reg])
        
        return new_reg

    elif tree.data == "LogicalAnd":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()
        new_reg1 = func.request_register()

        func.add_line("CNE", [new_reg, arg0, "0"])
        func.add_line("CNE", [new_reg1, arg1, "0"])
        func.add_line("AND", [new_reg, new_reg, new_reg1])

        return new_reg

    elif tree.data == "LogicalOr":
        arg0 = generate_expression(tree.children[0], func)
        arg1 = generate_expression(tree.children[1], func)

        new_reg = func.request_register()
        new_reg1 = func.request_register()

        func.add_line("CNE", [new_reg, arg0, "0"])
        func.add_line("CNE", [new_reg1, arg1, "0"])
        func.add_line("OR", [new_reg, new_reg, new_reg1])

        return new_reg

    # Comma Operations

    elif tree.data == "Comma":
        last = None
        for child in tree.children:
            last = generate_expression(child, func)

        return last

    # Ternary

    elif tree.data == "Ternary":
        new_reg = func.request_register()

        skip_label = func.request_label()
        else_label = func.request_label()

        cond = generate_expression(tree.children[0], func)
        func.add_conditional_jump("BZ", else_label, cond)

        v = generate_expression(tree.children[1], func)
        func.assign_variable(new_reg, v)
        func.add_jump(skip_label)

        func.place_label(else_label)

        v = generate_expression(tree.children[2], func)
        func.assign_variable(new_reg, v)

        func.place_label(skip_label)

        return new_reg

    # Function Call

    elif tree.data == "FuncCall":
        to_save = func.assigned_registers[:]
        to_save = [v for v in to_save if v != "R0"]

        registers = []

        i = 1
        for child in tree.children[1:]:
            v = generate_expression(child, func)
            r = func.request_register()
            func.add_line("MV", [r, v])
            registers.append(r)

        for reg in to_save:
            func.add_line("BACKUP", [reg])

        i = 1
        for r in registers:
            func.add_line("MV", ["R%i" % i, r])
            i += 1

        func.add_line("CALL", [tree.children[0].data])

        new_reg = func.request_register()
        func.assign_variable(new_reg, "R0")
        
        for reg in reversed(to_save):
            func.add_line("RESTORE", [reg])

        return new_reg

    # Possibly A Variable

    else:
        if tree.data in func.aliased_registers:
            return func.aliased_registers[tree.data]
        else:
            return global_register_aliases[tree.data]


def generate_statement(tree, func):
    if tree.data == "Compound" or tree.data == "Declarations":
        for child in tree.children:
            generate_statement(child, func)
    elif tree.data == "NOP":
        return
    elif tree.data == "Return":
        
        if len(tree.children) > 0:
            func.assign_variable("__RETURN", generate_expression(tree.children[0], func))
        else:
            func.clear_variable("__RETURN")
            
        func.add_jump("ret")
    elif tree.data == "VariableDeclaration":
        var_type = tree.children[0].data
        var_name = tree.children[1].data
    
        func.define_variable(var_name, var_type)

        if len(tree.children) > 2:
            var_value = generate_expression(tree.children[2], func)
            func.assign_variable(var_name, var_value)

    elif tree.data == "ExprCommand":
        generate_expression(tree.children[0], func)

    elif tree.data == "If":
        cond = generate_expression(tree.children[0], func)

        else_label = func.request_label()
        after_label = func.request_label()

        func.add_conditional_jump("BZ", else_label, cond)

        generate_statement(tree.children[1], func)

        func.add_jump(after_label)

        func.place_label(else_label)

        for child in tree.children[2:]:
            if child.data == "Else":
                generate_statement(child.children[0], func)
            elif child.data == "ElseIf":
                else_label = func.request_label()

                func.add_conditional_jump("BZ", else_label, cond)

                cond = generate_expression(child.children[0], func)

                generate_statement(child.children[1], func)

                func.add_jump(after_label)

                func.place_label(else_label)


        func.place_label(after_label)

    elif tree.data == "While":
        start_label = func.request_label()
        skip_label = func.request_label()

        func.place_label(start_label)
        
        cond = generate_expression(tree.children[0], func)
        func.add_conditional_jump("BZ", skip_label, cond)

        generate_statement(tree.children[1], func)

        func.add_jump(start_label)
        func.place_label(skip_label)

    elif tree.data == "For":
        generate_statement(tree.children[0], func)

        start_label = func.request_label()
        skip_label = func.request_label()

        func.place_label(start_label)
        
        cond = generate_expression(tree.children[1], func)
        func.add_conditional_jump("BZ", skip_label, cond)

        generate_statement(tree.children[3], func)

        generate_expression(tree.children[2], func)

        func.add_jump(start_label)
        func.place_label(skip_label)
        

def generate_function(tree):
    arguments = []

    for c in tree.children[2:]:
        if c.data == "Argument":
            arguments.append([c.children[0].data, c.children[1].data])
    f = Function(tree.children[1].data, arguments, tree.children[0].data, None)

    generate_statement(tree.children[-1], f)

    f.add_return()

    return f


def generate_program(tree):
    p = Program()

    start_func = Function("_start", [], "void", p)

    for child in tree.children:
        if child.data == "Function":
            p.add_function(generate_function(child))
        elif child.data == "GlobalVariable":
            var_type = child.children[0].data
            var_name = child.children[1].data
            var_value = generate_expression(child.children[2], start_func)
        
            start_func.define_global_variable(var_name, var_type)
            start_func.assign_variable(var_name, var_value)

            for v in start_func.aliased_registers:
                if start_func.aliased_registers[v].startswith("G"):
                    global_register_aliases[v] = start_func.aliased_registers[v]

    start_func.add_return()
    
    p.add_function(start_func)

    return p

