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

        return "%03i %s %s %s%s" % (self.i, alias.ljust(7), self.command.rjust(8), 
                                   ", ".join([(str(arg)).rjust(5) for arg in self.arguments]).ljust(20),
                                   ", ".join([str(n) for n in self.next_vals]))


class Program:
    def __init__(self):
        self.current_line = 0
        self.lines = {}

        self.assigned_registers = []
        self.free_registers = []
        self.last_register = 0

        self.address_aliases = {"ONE": 1}

    def add_line(self, command, arguments, next_vals=None):
        if next_vals is None:
            next_vals = []
        self.lines[self.current_line] = Line(command, arguments, self.current_line, next_vals + [self.current_line + 1], self)
        self.current_line += 1

    def request_register(self):
        if len(self.free_registers) > 0:
            v, *self.free_registers = self.free_registers
            self.assigned_registers.append(v)
        else:
            self.last_register += 1

            self.assigned_registers.append("R%i" % (self.last_register - 1))
        return self.assigned_registers[-1]
        
    def __repr__(self):
        return "\n".join([str(self.lines[k]) for k in self.lines])


def generate_program(tree):
    p = Program()

    p.add_line("MOV", ["R1", p.request_register()])
    p.add_line("JMP", ["3"])
    p.add_line("MOV", [p.request_register(), "2"])
    p.add_line("ADD", ["R3", p.request_register()])

    return p

