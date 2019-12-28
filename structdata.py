import utils


class Struct:
    def __init__(self, name):
        self.members = {}
        self.member_types = {}
        self.current = 0

        self.name = name

    def add_member(self, name, var_type):
        self.members[name] = self.current
        self.member_types[name] = var_type

        self.current += utils.get_size_of_type(var_type)

    def display_debug(self):
        for member in self.members:
            print(member, self.members[member], self.member_types[member])