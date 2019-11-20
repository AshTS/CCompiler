class Line:
    def __init__(self, command, arguments, i, next_vals, program):
        self.command = command
        self.arguments = arguments
        self.i = i
        self.next_vals = next_vals

        self.program = program

    def __repr__(self):
        alias = ""

        for k in self.program.address_aliases:
            if self.program.address_aliases[k] == self.i:
                alias = k + ":"

        return "%03i %s %s %s%s" % (self.i, alias.ljust(10), self.command.rjust(8), 
                                   ", ".join([(str(arg)).rjust(5) for arg in self.arguments]).ljust(20),
                                   ", ".join([str(n) for n in self.next_vals]))


class Function:
    def __init__(self, name, arguments, ret_type):
        self.current_line = 0
        self.lines = {}

        self.assigned_registers = []
        self.free_registers = []
        self.last_register = 0

        self.last_label = 0

        self.address_aliases = {}

        self.name = name

        self.arguments = arguments
        self.ret_type = ret_type


    def add_line(self, command, arguments, next_vals=None, include_next=True):
        if next_vals is None:
            next_vals = []
        self.lines[self.current_line] = Line(command, arguments, self.current_line, next_vals + ([self.current_line + 1] if include_next else []), self)
        self.current_line += 1


    def place_label(self):
        label = "L%i" % self.last_label
        self.last_label += 1

        self.address_aliases[label] = self.current_line
        return label

    def request_register(self):
        if len(self.free_registers) > 0:
            v, *self.free_registers = self.free_registers
            self.assigned_registers.append(v)
        else:
            self.last_register += 1

            self.assigned_registers.append("R%i" % (self.last_register - 1))
        return self.assigned_registers[-1]

    def add_return(self):
        self.address_aliases["ret"] = self.current_line
        self.add_line("RET", [])

        
    def __repr__(self):
        return self.ret_type + " " + self.name + "(" + ", ".join(["%s %s" % tuple(v) for v in self.arguments]) + ")" + ":\n" + "\n".join([str(self.lines[k]) for k in self.lines])

class Program:
    def __init__(self, functions=None):
        self.functions = [] if functions is None else functions

    def add_function(self, function):
        self.functions.append(function)

    def __repr__(self):
        return "\n\n".join([str(f) for f in self.functions])


def generate_expression(tree, func):
    if tree.data == "Integer":
        return tree.children[0].data


def generate_statement(tree, func):
    if tree.data == "Compound":
        for child in tree.children:
            generate_statement(child, func)
    elif tree.data == "NOP":
        return
    elif tree.data == "Return":
        
        if len(tree.children) > 0:
            func.add_line("MV", ["RET", generate_expression(tree.children[0], func)])
        else:
            func.add_line("MV", ["RET", "0"])
            
        func.add_line("J", ["ret"], ["ret"], False)
    else:
        func.add_line("HELLO", [])


def generate_function(tree):
    arguments = []

    for c in tree.children[2:]:
        if c.data == "Argument":
            arguments.append([c.children[0].data, c.children[1].data])

    f = Function(tree.children[1].data, arguments, tree.children[0].data)

    generate_statement(tree.children[-1], f)

    f.add_return()

    return f


def generate_program(tree):
    p = Program()

    for child in tree.children:
        if child.data == "Function":
            p.add_function(generate_function(child))

    return p

