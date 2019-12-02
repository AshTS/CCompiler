import preprocessor
import tokenizer
import parser
import generation
import assembly
import optimize

import utils

input_file_name = "test.c"
input_file_data = open(input_file_name, "r").read()

preprocessed, line_map, preprocessor_context = preprocessor.preprocess(input_file_data, input_file_name)

tokens = tokenizer.tokenize(preprocessed, line_map, input_file_name)
tokens = tokenizer.macros(tokens, preprocessor_context)

tree = parser.parse(tokens)

prog = generation.generate_program(tree)

optimzied = optimize.optimize(prog)

for p_func, o_func in zip(prog.functions, optimzied.functions):
    print("\n")
    utils.compare(str(p_func), str(o_func))

result = assembly.assemble(prog)

f = open("result.asm", 'w')
f.write(result)
f.close()
