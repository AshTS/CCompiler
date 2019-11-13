import tokenizer
import parser

input_file_name = "test.c"
input_file_data = open(input_file_name, "r").read()

tokens = tokenizer.tokenize(input_file_data)
parser.parse(tokens).display()
