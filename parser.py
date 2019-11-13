from utils import PeekIter

def report_parse_error(error, token):
    print("Parse Error %s on line %i, col %i" % (error, token.line, token.col))
    raise ValueError()

class ParseNode:
    def __init__(self, data, children=None):
        self.data = data
        self.children = children if children is not None else []

    def display(self, pre_num=0):
        pre = "\t" * pre_num
        print("%s<%s>" % (pre, self.data))
        if len(self.children) != 0:
            print("%s{" % (pre))
            for child in self.children:
                if child is None:
                    print("%s\tNone", pre)
                child.display(pre_num + 1)
            print("%s}" % (pre))


def check_integer(token):
    data = token.data

    num_chars = [str(i) for i in range(10)]

    for c in data:
        if not c in num_chars:
            return False

    return True


def check_string(token):
    data = token.data

    return data.startswith('"') and data.endswith('"')


def check_identifier(token):
    data = token.data

    first_chars = ([chr(ord('a') + i) for i in range(26)] + [chr(ord('A') + i) for i in range(26)] + ["_"])
    remaining_chars = first_chars + [str(i) for i in range(10)]

    if not data[0] in first_chars:
        return False

    for c in data[1:]:
        if not c in remaining_chars:
            return False

    return True


def check_raw_type(token):
    return token.data in ["char", "short", "int", "void"]

def parse_identifier(tokens):
    if check_identifier(tokens.peek()):
        return ParseNode(next(tokens).data, [])
    else:
        report_parse_error("Expected identifier token", next(tokens))


def parse_type(tokens):
    t = ""
    if tokens.peek().data == "unsigned":
        t += next(tokens).data + " "
    elif tokens.peek().data == "struct":
        t += next(tokens).data + " "

    if not check_raw_type(tokens.peek()):
        if not check_identifier(tokens.peek()):
            report_parse_error("Expected type token", next(tokens))
        else:
            t += next(tokens).data
    else:
        t += next(tokens).data

    while tokens.peek().data == "*":
        t += next(tokens).data

    return ParseNode(t, [])


def parse_argument(tokens):
    return ParseNode("Argument", [parse_type(tokens), parse_identifier(tokens)])

def parse_struct_def(tokens):
    magic = next(tokens)
    if magic.data != "struct":
        report_parse_error("Expected 'struct' token", magic)

    children = [parse_identifier(tokens)]

    if not tokens.peek().data == "{":
        report_parse_error("Expected '{' token", next(tokens))
    else:
        next(tokens)

    while tokens.peek().data != "}":
        children.append(parse_argument(tokens))

        if tokens.peek().data == ";":
            next(tokens)
        else:
            break

    if not tokens.peek().data == "}":
        report_parse_error("Expected '}' token", next(tokens))
    else:
        next(tokens)

    if not tokens.peek().data == ";":
        report_parse_error("Expected ';' token", next(tokens))
    else:
        next(tokens)

    return ParseNode("StructDef", children)

def parse_function_def(tokens):
    return None

def parse_typedef(tokens):
    children = []

    magic = next(tokens)
    if magic.data != "typedef":
        report_parse_error("Expected 'typedef' token", magic)

    children = [parse_type(tokens), parse_identifier(tokens)]

    if not tokens.peek().data == ";":
        report_parse_error("Expected ';' token", next(tokens))
    else:
        next(tokens)

    return ParseNode("TypeDef", children)

def parse_file(tokens):
    children = []
    while True:
        try:
            peeked = tokens.peek()
        except StopIteration:
            break

        if peeked.data == "struct":
            children.append(parse_struct_def(tokens))

        elif peeked.data == "typedef":
            children.append(parse_typedef(tokens))

        else:
            children.append(parse_function_def(tokens))

    return ParseNode("File", children)

def parse(tokens):
    peekable = PeekIter(tokens)

    return parse_file(peekable)
    