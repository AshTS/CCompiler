TERMINATE_ON_ERROR = False

def report_parse_error(error, tokens=None, token=None):
    if token is None:
        token = tokens.peek()

    line = token.line
    col = token.col + 1
    file_name = token.file

    print("Parse Error %s on line %i, col %i in file %s" % (error, line, col, file_name))

    if TERMINATE_ON_ERROR:
        raise Exception()
