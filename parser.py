from utils import PeekIter
import defines

def report_parse_error(error, tokens):
    token = tokens.peek()

    print("Parse Error %s on line %i, col %i" % (error, token.line, token.col))


class ParseNode:
    def __init__(self, data, children=None):
        self.data = data
        self.children = children if children is not None else []

    def display(self, pre_num=0):
        pre = "  " * pre_num
        print("%s<%s>" % (pre, self.data))
        if len(self.children) != 0:
            print("%s{" % (pre))
            for child in self.children:
                if child is None:
                    print("%s  None", pre)
                else:
                    child.display(pre_num + 1)
            print("%s}" % (pre))


class Scope:
    def __init__(self):
        self.typedefs = []
        self.funcdefs = []
        self.vardefs = []


class ParserContext:
    def __init__(self, tokens):
        self.tokens = tokens
        self.scopes = [Scope()]

    def check_type(self, data):
        for scope in self.scopes:
            if data in scope.typedefs:
                return True

        return False

    def check_func(self, data):
        for scope in self.scopes:
            if data in scope.funcdefs:
                return True

        return False

    def check_var(self, data):
        for scope in self.scopes:
            if data in scope.vardefs:
                return True

        return False

    def push_scope(self, scope):
        self.scopes = [scope] + self.scopes

    def pop_scope(self):
        self.scopes = self.scopes[1:]

    def add_type(self, data):
        self.scopes[0].typedefs.append(data)

    def add_func(self, data):
        self.scopes[0].funcdefs.append(data)

    def add_var(self, data):
        self.scopes[0].vardefs.append(data)


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


def check_raw_type(token, context):
    return (token.data in ["char", "short", "int", "void"]) or context.check_type(token.data)


def parse_identifier(context):
    if check_identifier(context.tokens.peek()):
        return ParseNode(next(context.tokens).data, [])
    else:
        report_parse_error("Expected identifier token", context.tokens)


def parse_type(context):
    t = ""
    if context.tokens.peek().data in ["unsigned", "signed", "struct"]:
        t += next(context.tokens).data + " "

    if not check_raw_type(context.tokens.peek(), context):
        if not check_identifier(context.tokens.peek()):
            report_parse_error("Expected type token", context.tokens)
        else:
            t += next(context.tokens).data
    else:
        t += next(context.tokens).data

    while context.tokens.peek().data == "*":
        t += next(context.tokens).data

    return ParseNode(t, [])


def parse_argument(context):
    return ParseNode("Argument", [parse_type(context), parse_identifier(context)])


def parse_struct_def(context):
    magic = next(context.tokens)
    if magic.data != "struct":
        report_parse_error("Expected 'struct' token", magic)

    children = [parse_identifier(context)]

    if not context.tokens.peek().data == "{":
        report_parse_error("Expected '{' token", context.tokens)
    else:
        next(context.tokens)

    while context.tokens.peek().data != "}":
        children.append(parse_argument(context))

        if context.tokens.peek().data == ";":
            next(context.tokens)
        else:
            break

    if not context.tokens.peek().data == "}":
        report_parse_error("Expected '}' token", context.tokens)
    else:
        next(context.tokens)

    if not context.tokens.peek().data == ";":
        report_parse_error("Expected ';' token", context.tokens)
    else:
        next(context.tokens)

    return ParseNode("StructDef", children)


def parse_variable_declaration(context):
    children = [parse_type(context)]
    children.append(parse_identifier(context))

    if not context.tokens.peek().data == "=":
        report_parse_error("Expected '=' token", context.tokens)
    else:
        next(context.tokens)

    children.append(parse_expression(context))

    return ParseNode("VariableDeclaration", children)


def parse_expression(context, level=15, add=0):
    level += add

    if level == 0:      # Raw Ident, Raw Num, ()
        if check_identifier(context.tokens.peek()):
            return parse_identifier(context)

        elif check_integer(context.tokens.peek()):
            return ParseNode(next(context.tokens).data)

        elif check_string(context.tokens.peek()):
            return ParseNode("String", [ParseNode(next(context.tokens).data)])

        elif context.tokens.peek().data == "(":
            next(context.tokens)

            result = parse_expression(context)

            if not context.tokens.peek().data == ")":
                report_parse_error("Expected ')' token", context.tokens)
            else:
                next(context.tokens)

            return result

        report_parse_error("Expected Expression", context.tokens)

    elif level == 1:    # a++, a--, a(), a[], a., a->
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "++":
            next(context.tokens)
            return ParseNode("PostInc", [result])
        elif context.tokens.peek().data == "--":
            next(context.tokens)
            return ParseNode("PostDec", [result])
        elif context.tokens.peek().data == "(":
            next(context.tokens)

            children = [result]

            while context.tokens.peek().data != ")":
                children.append(parse_expression(context, add=-1))

                if context.tokens.peek().data == ",":
                    next(context.tokens)
                else:
                    break

            if not context.tokens.peek().data == ")":
                report_parse_error("Expected ')' token", context.tokens)
            else:
                next(context.tokens)
            
            return ParseNode("FuncCall", children)
        elif context.tokens.peek().data == "[":
            next(context.tokens)

            children = [result]

            children.append(parse_expression(context))

            if not context.tokens.peek().data == "]":
                report_parse_error("Expected ']' token", context.tokens)
            else:
                next(context.tokens)
            
            return ParseNode("Subscript", children)
        elif context.tokens.peek().data == ".":
            next(context.tokens)

            return ParseNode("Member", [result, parse_identifier(context)])
        elif context.tokens.peek().data == "->":
            next(context.tokens)

            return ParseNode("PtrMember", [result, parse_identifier(context)])
        return result

    elif level == 2:    # ++a, --a, +a, -a, !a, ~a, (type)a, *a, &a
        if context.tokens.peek().data == "++":
            next(context.tokens)
            return ParseNode("PreInc", [parse_expression(context, level)])
        elif context.tokens.peek().data == "--":
            next(context.tokens)
            return ParseNode("PreDec", [parse_expression(context, level)])
        elif context.tokens.peek().data == "+":
            next(context.tokens)
            return ParseNode("UnaryPlus", [parse_expression(context, level)])
        elif context.tokens.peek().data == "-":
            next(context.tokens)
            return ParseNode("UnaryMinus", [parse_expression(context, level)])
        elif context.tokens.peek().data == "!":
            next(context.tokens)
            return ParseNode("LogicalNot", [parse_expression(context, level)])
        elif context.tokens.peek().data == "~":
            next(context.tokens)
            return ParseNode("BitwiseNot", [parse_expression(context, level)])
        elif context.tokens.peek().data == "(" and context.tokens.peek(1).data in defines.type_starting_identifiers:
            next(context.tokens)
            children = [parse_type(context)]

            if not context.tokens.peek().data == ")":
                report_parse_error("Expected ')' token", context.tokens)
            else:
                next(context.tokens)

            children.append(parse_expression(context, level))

            return ParseNode("Cast", children)
        elif context.tokens.peek().data == "*":
            next(context.tokens)
            return ParseNode("Deref", [parse_expression(context, level)])
        elif context.tokens.peek().data == "&":
            next(context.tokens)
            return ParseNode("Reference", [parse_expression(context, level)])
        
        return parse_expression(context, level - 1)

    elif level == 3:    # a*b, a/b, a%b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "*":
            next(context.tokens)
            return ParseNode("Multiply", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "/":
            next(context.tokens)
            return ParseNode("Divide", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "%":
            next(context.tokens)
            return ParseNode("Modulus", [result, parse_expression(context, level)])

        return result

    elif level == 4:    # a+b, a-b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "+":
            next(context.tokens)
            return ParseNode("Addition", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "-":
            next(context.tokens)
            return ParseNode("Subtraction", [result, parse_expression(context, level)])

        return result

    elif level == 5:    # a<<b, a>>b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "<<":
            next(context.tokens)
            return ParseNode("ShiftLeft", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == ">>":
            next(context.tokens)
            return ParseNode("ShiftRight", [result, parse_expression(context, level)])

        return result

    elif level == 6:    # a<b, a<=b, a>b, a>=b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "<":
            next(context.tokens)
            return ParseNode("LessThan", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "<=":
            next(context.tokens)
            return ParseNode("LessThanEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == ">":
            next(context.tokens)
            return ParseNode("GreaterThan", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "<=":
            next(context.tokens)
            return ParseNode("GreaterThanEqual", [result, parse_expression(context, level)])

        return result

    elif level == 7:    # a==b, a!=b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "==":
            next(context.tokens)
            return ParseNode("Equal", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "!=":
            next(context.tokens)
            return ParseNode("NotEqual", [result, parse_expression(context, level)])

        return result

    elif level == 8:    # a&b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "&":
            next(context.tokens)
            return ParseNode("BitwiseAnd", [result, parse_expression(context, level)])

        return result

    elif level == 9:    # a^b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "^":
            next(context.tokens)
            return ParseNode("BitwiseXor", [result, parse_expression(context, level)])

        return result

    elif level == 10:    # a|b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "|":
            next(context.tokens)
            return ParseNode("BitwiseOr", [result, parse_expression(context, level)])

        return result

    elif level == 11:    # a&&b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "&&":
            next(context.tokens)
            return ParseNode("LogicalAnd", [result, parse_expression(context, level)])

        return result

    elif level == 12:    # a||b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "||":
            next(context.tokens)
            return ParseNode("LogicalOr", [result, parse_expression(context, level)])

        return result

    elif level == 13:    # a?b:c
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "?":
            next(context.tokens)
            middle = parse_expression(context)

            if not context.tokens.peek().data == ":":
                report_parse_error("Expected ':' token", context.tokens)
            else:
                next(context.tokens)

            return ParseNode("Ternary", [result, middle, parse_expression(context, level)])

        return result

    elif level == 14:    # a=b, a+=b, a-=b, a*=b, a/=b, a%=b, a<<=b, a>>=b, a&=b, a|=b, a^=b
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "=":
            next(context.tokens)
            return ParseNode("Assignment", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "+=":
            next(context.tokens)
            return ParseNode("AddEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "-=":
            next(context.tokens)
            return ParseNode("SubtractEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "*=":
            next(context.tokens)
            return ParseNode("MultiplyEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "/=":
            next(context.tokens)
            return ParseNode("DivideEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "%=":
            next(context.tokens)
            return ParseNode("ModulusEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "<<=":
            next(context.tokens)
            return ParseNode("ShiftLeftEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == ">>=":
            next(context.tokens)
            return ParseNode("ShiftRightEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "&=":
            next(context.tokens)
            return ParseNode("AndEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "^=":
            next(context.tokens)
            return ParseNode("XorEqual", [result, parse_expression(context, level)])
        elif context.tokens.peek().data == "|=":
            next(context.tokens)
            return ParseNode("OrEqual", [result, parse_expression(context, level)])

        return result

    elif level == 15:    # a,b
        result = parse_expression(context, level - 1)

        children = [result]

        if context.tokens.peek().data == ",":

            while context.tokens.peek().data == ",":
                next(context.tokens)
                children.append(parse_expression(context, level-1))

            return ParseNode("Comma", children)

        return result

    return ParseNode("ERROR", next(context.tokens).data)


def parse_statement(context):
    if context.tokens.peek().data == ";":
        next(context.tokens)
        return ParseNode("NOP", [])
    elif context.tokens.peek().data == "{":
        next(context.tokens)

        children = []

        while context.tokens.peek().data != "}":
            children.append(parse_statement(context))

        next(context.tokens)

        return ParseNode("Compound", children)
    elif context.tokens.peek().data == "return":
        next(context.tokens)

        children = [parse_expression(context)]

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        return ParseNode("Return", children)
    elif context.tokens.peek().data == "while":
        next(context.tokens)

        children = []

        if not context.tokens.peek().data == "(":
            report_parse_error("Expected '(' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_expression(context))

        if not context.tokens.peek().data == ")":
            report_parse_error("Expected ')' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_statement(context))

        return ParseNode("While", children)
    elif context.tokens.peek().data == "if":
        next(context.tokens)

        children = []

        if not context.tokens.peek().data == "(":
            report_parse_error("Expected '(' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_expression(context))

        if not context.tokens.peek().data == ")":
            report_parse_error("Expected ')' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_statement(context))

        while context.tokens.peek().data == "else":
            next(context.tokens)

            statement = "Else"

            sub_children = []

            if context.tokens.peek().data == "if":
                next(context.tokens)
                statement += "If"

                if not context.tokens.peek().data == "(":
                    report_parse_error("Expected '(' token", context.tokens)
                else:
                    next(context.tokens)

                sub_children.append(parse_expression(context))

                if not context.tokens.peek().data == ")":
                    report_parse_error("Expected ')' token", context.tokens)
                else:
                    next(context.tokens)

            sub_children.append(parse_statement(context))

            children.append(ParseNode(statement, sub_children))

            if statement == "Else":
                break

        return ParseNode("If", children)
    elif context.tokens.peek().data == "for":
        next(context.tokens)

        children = []

        if not context.tokens.peek().data == "(":
            report_parse_error("Expected '(' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_expression(context))

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_expression(context))

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_expression(context))

        if not context.tokens.peek().data == ")":
            report_parse_error("Expected ')' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_statement(context))

        return ParseNode("For", children)
    elif context.tokens.peek().data in defines.type_starting_identifiers:
        node = parse_variable_declaration(context)

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        return node
        
    else:
        children = [parse_expression(context)]

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        return ParseNode("ExprCommand", children)


def parse_function_def(context):
    children = [parse_type(context), parse_identifier(context)]

    if not context.tokens.peek().data == "(":
        report_parse_error("Expected '(' token", context.tokens)
    else:
        next(context.tokens)

    while not context.tokens.peek().data == ")":
        children.append(parse_argument(context))

        if context.tokens.peek().data == ",":
            next(context.tokens)
        else:
            break

    if not context.tokens.peek().data == ")":
        report_parse_error("Expected ')' token", context.tokens)
    else:
        next(context.tokens)

    children.append(parse_statement(context))

    return ParseNode("Function", children)


def parse_typedef(context):
    children = []

    magic = next(context.tokens)
    if magic.data != "typedef":
        report_parse_error("Expected 'typedef' token", magic)

    children = [parse_type(context), parse_identifier(context)]

    if not context.tokens.peek().data == ";":
        report_parse_error("Expected ';' token", context.tokens)
    else:
        next(context.tokens)

    return ParseNode("TypeDef", children)


def parse_file(context):
    children = []
    while True:
        try:
            peeked = context.tokens.peek()
        except StopIteration:
            break

        if peeked.data == "struct":
            children.append(parse_struct_def(context))

        elif peeked.data == "typedef":
            children.append(parse_typedef(context))

        else:
            children.append(parse_function_def(context))

    return ParseNode("File", children)


def parse(tokens):
    peekable = PeekIter(tokens)
    context = ParserContext(peekable)

    return parse_file(context)
    