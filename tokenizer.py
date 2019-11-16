from utils import PeekIter


class Token:
    def __init__(self, data, line, col, line_map, file_name="[unknown]"):
        self.data, self.col, self.line, self.file = data, col, *line_map[line]

    def __repr__(self):
        return "<'%s' %s, %i:%i>" % (self.data, self.file, self.line, self.col)


def tokenize(text, line_map, file_name="[unknown]"):
    symbols = [".", ",", "{", "}", "(", ")", "=", ";", "&", "*", "-", "!", "+", "++", "--", "->", "[", "]", "?", ":", "=", "/", "||", "&&", "==", "!=", ">", "<", "<=", ">=", "|", "&", "^", "<<", ">>", "+=", "-=", "*=", "/=", "%=", "<<=", ">>=", "|=", "&=", "^="]
    symbols_first = [v[0] for v in symbols]
    beginnings = [v[0] for v in symbols if len(v) > 1]

    current_word = ""
    text_iter = PeekIter(text + " ")

    tokens = []

    in_multiline_comment = False
    in_comment = False
    in_string = False

    line_number = 1
    column_number = 0

    for c in text_iter:
        if c == "\n":
            if current_word != "":
                tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                current_word = ""

            column_number = 0
            line_number += 1
        column_number += 1

        if in_multiline_comment:
            if c == '*' and next(text_iter) == '/':
                in_multiline_comment = False

        elif in_comment:
            if c == '\n':
                in_comment = False

        elif in_string:
            if c == '"':
                in_string = False
                current_word += c
                tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                current_word = ""
            elif c == '\\':
                p = next(text_iter)
                if p == "n":
                    current_word += "\n"
                elif p == "t":
                    current_word += "\t"
                else:
                    current_word += p
            else:
                current_word += c

        else:
            if c in [" ", "\n", "\t"]:
                if current_word != "":
                    tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                current_word = ""
            elif c == '/':
                if text_iter.peek() == "*":
                    in_multiline_comment = True

                    if current_word != "":
                        tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                    current_word = ""

                elif text_iter.peek() == "/":
                    in_comment = True

                    if current_word != "":
                        tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                    current_word = ""
                else:
                    if current_word != "":
                        tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                    tokens.append(Token(c, line_number, column_number - 1, line_map, file_name))
                    current_word = ""
            elif c in symbols_first:
                if current_word != "":
                    tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                current_word = ""

                if c in beginnings:
                    next_c = text_iter.peek()
                    if c + next_c in symbols:
                        tokens.append(Token(c + next(text_iter), line_number, column_number - len(current_word), line_map, file_name))
                    else:
                        tokens.append(Token(c, line_number, column_number - 1, line_map, file_name))
                else:
                    tokens.append(Token(c, line_number, column_number - 1, line_map, file_name))
            elif c == '"':
                if current_word != "":
                    tokens.append(Token(current_word, line_number, column_number - len(current_word), line_map, file_name))
                current_word = '"'
                in_string = True
            else:
                current_word += c
    
    return tokens
