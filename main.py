import preprocessor
import tokenizer
import parser
import generation

import utils

input_file_name = "test.c"
input_file_data = open(input_file_name, "r").read()

preprocessed, line_map, preprocessor_context = preprocessor.preprocess(input_file_data, input_file_name)

tokens = tokenizer.tokenize(preprocessed, line_map, input_file_name)
tokens = tokenizer.macros(tokens, preprocessor_context)

print(tokens)

tree = parser.parse(tokens)
tree.display()

prog = generation.generate_program(tree)

print(prog)
