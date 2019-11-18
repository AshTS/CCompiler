import preprocessor
import tokenizer
import parser

input_file_name = "test.c"
input_file_data = open(input_file_name, "r").read()

preprocessed, line_map, preprocessor_context = preprocessor.preprocess(input_file_data, input_file_name)

print(preprocessor_context.defines)

tokens = tokenizer.tokenize(preprocessed, line_map, input_file_name)
tokens = tokenizer.macros(tokens, preprocessor_context)

print(tokens)

parser.parse(tokens).display()
