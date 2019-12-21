from utils import PeekIter
from utils import check_integer as check_integer_raw
from utils import check_float as check_float_raw
import defines
from errors import report_parse_error


class ParseNode:
    def __init__(self, data, children=None, pos=(0, 0, "[unknown]")):
        self.data = data
        self.children = children if children is not None else []
        self.col, self.line, self.file = pos

    def display(self, pre_num=0):
        pre = "  " * pre_num

        pos_str = "[%i:%i %s]" % (self.line, self.col, self.file) if self.file != "[unknown]" else ""

        print("%s<%s>\t\t%s" % (pre, self.data, pos_str))
        if len(self.children) != 0:
            print("%s{" % (pre))
            for child in self.children:
                if child is None:
                    print("%s  None" % pre)
                else:
                    child.display(pre_num + 1)
            print("%s}" % (pre))


class Scope:
    def __init__(self):
        self.typedefs = {}
        self.funcdefs = []
        self.vardefs = []
        self.vartypes = {}


class ParserContext:
    def __init__(self, tokens):
        self.tokens = tokens
        self.scopes = [Scope()]
        self.all_strings = ""
        self.string_map = {}

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

    def get_type(self, data):
        for scope in self.scopes:
            if data in scope.typedefs:
                return scope.typedefs[data]

        return None

    def get_var_type(self, data):
        for scope in self.scopes:
            if data in scope.vartypes:
                return scope.vartypes[data]

        return None

    def push_scope(self, scope):
        self.scopes = [scope] + self.scopes

    def pop_scope(self):
        self.scopes = self.scopes[1:]

    def add_type(self, data, value):
        self.scopes[0].typedefs[data] = value

    def add_func(self, data):
        self.scopes[0].funcdefs.append(data)

    def add_var(self, data, data_type):
        self.scopes[0].vardefs.append(data)
        self.scopes[0].vartypes[data] = data_type


def check_string(token):
    data = token.data

    return data.startswith('"') and data.endswith('"')


def check_integer(token):
    return check_integer_raw(token.data)


def check_float(token):
    return check_float_raw(token.data)


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
    return (token.data in defines.type_starting_identifiers) or context.check_type(token.data)


def parse_identifier(context):
    if check_identifier(context.tokens.peek()):
        t = context.tokens.peek()
        return ParseNode(next(context.tokens).data, [], (t.col, t.line, t.file))
    else:
        report_parse_error("Expected identifier token", context.tokens)


def parse_type(context):
    result = ""

    if context.tokens.peek().data == "static":
        result += " " + next(context.tokens).data

    if context.tokens.peek().data == "const":
        result += next(context.tokens).data

    if context.tokens.peek().data in ["signed", "unsigned"]:
        v = " " + next(context.tokens).data
        result += v

        if context.tokens.peek().data not in ["int", "short", "char"]:
            report_parse_error("Cannot apply modifier '%s' to type '%s'" % (v.strip(), context.tokens.peek().data), context.tokens)

    elif context.tokens.peek().data == "struct":
        result += " " + next(context.tokens).data

        if context.tokens.peek().data in ["int", "short", "char", "float", "void"]:
            report_parse_error("Type '%s' cannot be a struct" % (context.tokens.peek().data), context.tokens)

    if not check_identifier(context.tokens.peek()):
        report_parse_error("Expected Type", context.tokens)
    else:
        if context.check_type(context.tokens.peek().data):
            result += " " + context.get_type(context.tokens.peek().data)
            next(context.tokens)
        else:
            result += " " + next(context.tokens).data

    while context.tokens.peek().data == "*":
        result += next(context.tokens).data

    if context.tokens.peek().data == "[":
        result += "*"
        next(context.tokens)

        if context.tokens.peek().data != "]":  
            report_parse_error("Expected ']' token", context.tokens)
        else:
            next(context.tokens)
        

    return ParseNode(result.strip(), [])


def parse_argument(context):
    return ParseNode("Argument", [parse_type(context), parse_identifier(context)])


def parse_struct_value(context):
    children = []

    if not context.tokens.peek().data == "{":
        report_parse_error("Expected '{' token", context.tokens)
    else:
        next(context.tokens)

    while context.tokens.peek().data != "}":
        children.append(parse_expression(context, add=-1))

        if context.tokens.peek().data == ",":
            next(context.tokens)
        else:
            break

    if not context.tokens.peek().data == "}":
        report_parse_error("Expected '}' token", context.tokens)
    else:
        next(context.tokens)

    return ParseNode("StructValue", children)


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
    declarations = []
    
    raw_type = parse_type(context)

    while True:
        children = [ParseNode(raw_type.data)]

        children.append(parse_identifier(context))

        if context.tokens.peek().data == "=":
            next(context.tokens)

            children.append(parse_expression(context, add=-1))
            children.append(ParseNode(""))

        elif context.tokens.peek().data == "[":
            next(context.tokens)

            children[0].data += "*"

            children.append(ParseNode(""))
            children.append(ParseNode("ArraySize", [parse_expression(context, 0)]))

            if not context.tokens.peek().data == "]":
                report_parse_error("Expected ']' token", context.tokens)
            else:
                next(context.tokens)
            
        context.add_var(children[1].data, children[0].data)

        declarations.append(ParseNode("VariableDeclaration", children))

        if context.tokens.peek().data == ",":
            next(context.tokens)

        else:
            break
        

    if len(declarations) == 1:
        return declarations[0]
    else:
        return ParseNode("Declarations", declarations)


def parse_expression(context, level=15, add=0):
    level += add

    if level == 0:      # Struct, Raw Ident, Raw Num, ()
        if context.tokens.peek().data == "{":
            return parse_struct_value(context)
        
        elif context.tokens.peek().data.startswith("'"):
            data = ParseNode("Char", [ParseNode(next(context.tokens).data)])
            return data

        elif check_identifier(context.tokens.peek()):
            return parse_identifier(context)

        elif check_integer(context.tokens.peek()):
            t = context.tokens.peek()
            return ParseNode("Integer", [ParseNode(next(context.tokens).data)], (t.col, t.line, t.file))

        elif check_float(context.tokens.peek()):
            t = context.tokens.peek()
            return ParseNode("Float", [ParseNode(next(context.tokens).data)], (t.col, t.line, t.file))

        elif check_string(context.tokens.peek()):
            t = context.tokens.peek()
            ptr = len(context.all_strings)
            context.all_strings += t.data[1:-1] + chr(0)
            return ParseNode("String", [ParseNode(next(context.tokens).data), ParseNode(str(ptr))], (t.col, t.line, t.file))

        elif context.tokens.peek().data == "(":
            next(context.tokens)

            result = parse_expression(context)

            if not context.tokens.peek().data == ")":
                report_parse_error("Expected ')' token", context.tokens)
            else:
                next(context.tokens)

            return result
        
        print(context.tokens.peek())

        report_parse_error("Expected Expression", context.tokens)

    elif level == 1:    # a++, a--, a(), a[], a., a->
        identifier = check_identifier(context.tokens.peek())
        result_token = context.tokens.peek()
        result = parse_expression(context, level - 1)

        if context.tokens.peek().data == "(" and identifier:
            if not context.check_func(result.data):
                report_parse_error("Undefined Function Identifier '%s'" % result.data, context.tokens, result_token)

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
            
            return ParseNode("FuncCall", children, (result_token.col, result_token.line, result_token.file))

        if identifier and not context.check_var(result.data):
                report_parse_error("Undefined Variable Identifier '%s'" % result.data, context.tokens, result_token)

        if context.tokens.peek().data == "++":
            next(context.tokens)
            return ParseNode("PostInc", [result])
        elif context.tokens.peek().data == "--":
            next(context.tokens)
            return ParseNode("PostDec", [result])
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
        elif context.tokens.peek().data == "(" and check_raw_type(context.tokens.peek(1), context):
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
        context.push_scope(Scope())
        next(context.tokens)

        children = []

        while context.tokens.peek().data != "}":
            children.append(parse_statement(context))

        next(context.tokens)

        context.pop_scope()

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
    elif context.tokens.peek().data == "continue":
        next(context.tokens)

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        return ParseNode("Continue", [])
    elif context.tokens.peek().data == "break":
        next(context.tokens)

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        return ParseNode("Break", [])
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
    elif context.tokens.peek().data == "switch":
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

        if not context.tokens.peek().data == "{":
            report_parse_error("Expected '{' token", context.tokens)
        else:
            next(context.tokens)

        while not context.tokens.peek().data == "}":
            if context.tokens.peek().data == "default":
                next(context.tokens)

                if not context.tokens.peek().data == ":":
                    report_parse_error("Expected ':' token", context.tokens)
                else:
                    next(context.tokens)
                
                children.append(ParseNode("Default"))
            elif context.tokens.peek().data == "case":
                next(context.tokens)

                children.append(ParseNode("Case", [parse_expression(context, 0)]))

                if not context.tokens.peek().data == ":":
                    report_parse_error("Expected ':' token", context.tokens)
                else:
                    next(context.tokens)
            else:
                children.append(parse_statement(context))

        if not context.tokens.peek().data == "}":
            report_parse_error("Expected '}' token", context.tokens)
        else:
            next(context.tokens)

        return ParseNode("Switch", children)
    elif context.tokens.peek().data == "for":
        next(context.tokens)

        children = []

        if not context.tokens.peek().data == "(":
            report_parse_error("Expected '(' token", context.tokens)
        else:
            next(context.tokens)

        children.append(parse_statement(context))

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
    elif check_raw_type(context.tokens.peek(), context):
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

    if context.tokens.peek().data == "=":
        next(context.tokens)

        expr = parse_expression(context)

        if not context.tokens.peek().data == ";":
            report_parse_error("Expected ';' token", context.tokens)
        else:
            next(context.tokens)

        context.add_var(children[1].data, children[0].data)

        return ParseNode("GlobalVariable", children + [expr])


    if not context.tokens.peek().data == "(":
        report_parse_error("Expected '(' token", context.tokens)
    else:
        next(context.tokens)

    context.add_func(children[1].data)

    context.push_scope(Scope())

    while not context.tokens.peek().data == ")":
        children.append(parse_argument(context))

        context.add_var(children[-1].children[1].data, children[-1].children[0].data)

        if context.tokens.peek().data == ",":
            next(context.tokens)
        else:
            break

    if not context.tokens.peek().data == ")":
        report_parse_error("Expected ')' token", context.tokens)
    else:
        next(context.tokens)

    children.append(parse_statement(context))

    context.pop_scope()

    return ParseNode("Function", children)


def parse_typedef(context):
    children = []

    magic = next(context.tokens)
    if magic.data != "typedef":
        report_parse_error("Expected 'typedef' token", context.tokens)

    children = [parse_type(context), parse_identifier(context)]

    if not context.tokens.peek().data == ";":
        report_parse_error("Expected ';' token", context.tokens)
    else:
        next(context.tokens)

    context.add_type(children[1].data, children[0].data)

    return ParseNode("TypeDef", children)


def parse_enum(context):
    children = []
    current = 0

    if not context.tokens.peek().data == "enum":
        report_parse_error("Expected 'typedef' token", context.tokens)
    else:
        next(context.tokens)

    children.append(parse_identifier(context))

    if not context.tokens.peek().data == "{":
        report_parse_error("Expected '{' token", context.tokens)
    else:
        next(context.tokens)

    while context.tokens.peek().data != "}":
        ident = parse_identifier(context)
        if context.tokens.peek().data == "=":
            next(context.tokens)

            num = parse_expression(context, 0)
            if num.data == "Integer":
                current = int(num.children[0].data)
            else:
                report_parse_error("Expected Integer", context.tokens)

        children.append(ParseNode("EnumEqual", [ident, ParseNode("Integer", [ParseNode(str(current))])]))
        current += 1

        if context.tokens.peek().data == ",":
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

    return ParseNode("Enum", children)

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

        elif peeked.data == "enum":
            children.append(parse_enum(context))

        else:
            children.append(parse_function_def(context))

    return ParseNode("File", children)


def parse(tokens):
    peekable = PeekIter(tokens)
    context = ParserContext(peekable)

    result = parse_file(context)

    return result