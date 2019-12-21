import preprocessor
import tokenizer
import parser
import generation
import assembly
import optimize
import utils
import settings
import usage

import sys

options = {}
current = ""

for val in sys.argv[1:]:
    if val.startswith("-"):
        current = val[1:]
    else:
        if current in options:
            options[current].append(val)
        else:
            options[current] = [val]

if not "" in options:
    print("No Input File Given")
    usage.usage()
    
    sys.exit()

input_file_name = options[""][0]
output_file_name = "result.asm"
input_file_data = open(input_file_name, "r").read()

if "o" in options:
    output_file_name = options["o"][0]

settings.DISPLAY_ASM = "-A" in options
settings.DISPLAY_OPTIMIZATION = "-O" in options
settings.DISPLAY_TREE = "-t" in options

preprocessed, line_map, preprocessor_context = preprocessor.preprocess(input_file_data, input_file_name)

tokens = tokenizer.tokenize(preprocessed, line_map, input_file_name)
tokens = tokenizer.macros(tokens, preprocessor_context)

tree = parser.parse(tokens)

if settings.DISPLAY_TREE:
    tree.display()

prog = generation.generate_program(tree)

funcs = [str(p) for p in prog.functions]

optimzied = optimize.optimize(prog)

if settings.DISPLAY_OPTIMIZATION:
    for p_func, o_func in zip(funcs, optimzied.functions):
        print("\n")
        utils.compare(p_func, str(o_func))

result = assembly.assemble(optimzied)

if settings.DISPLAY_ASM:
    print(result)

f = open(output_file_name, 'w')
f.write(result)
f.close()
