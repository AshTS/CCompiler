import preprocessor
import tokenizer
import parser

input_file_name = "test.c"
input_file_data = open(input_file_name, "r").read()

preprocessed, line_map = preprocessor.preprocess(input_file_data, input_file_name)

tokens = tokenizer.tokenize(preprocessed, line_map, input_file_name)
parser.parse(tokens)# .display()
