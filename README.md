# C Compiler

This is a basic C Compiler written in Python. It was written as an end of year project, written in the last 50 days of 2019. It is not feature complete, it is missing unions, enums, bit fields, proper handling for global variables, and a number of other issues, however for the most part, it is a functioning C Compiler.

This compiler does not output an ELF or binary file, instead it outputs assembly in a language dictated by the target. By default the compiler targets a processor designed for this project, which has an [emulator](https://www.github.com/CarterTS/DemoProcessor) written to aid in development of the compiler.

# Usage

The compiler is run using the command

```
python3 main.py file [-o output] [options]
```

Where

-o sets the name of the output file (which defaults to result.asm)

-A Outputs the assembly code to the terminal.

-O Shows the intermediate code before and after optimization

-t Outputs the parse tree to the console

-I Outputs post-optimization intermediate code to console

-C Disables Colored Output

-c Show incremental optimization changes

-cf Show finer grain optimization changes

## Compiling the Examples

There are three example files given in the examples directory (along with display.h, which holds the code to handle outputing information for the system used by the demo processor).

To compile one of the example files, from the root directory of the project run

```
python3 main.py examples/hello.c -o hello.asm
```

with any options you may want to add.

This will output an assembly file which should end with something like this:

```
# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R13, R0, 0
JL R1, clear_display
ADD R3, R0, 26
JL R1, print
main_L0:
ADD R3, R0, 1
CE R15, R3, 0
JF R15, main_L1
J main_L0
main_L1:
ADD R13, R0, 0
main_ret:
RW R1, R2
ADD R2, R2, 2
J R1
```

This assembly file can then be assembled and run with the demo processor.

# Suggested Install

For ease of use, it is suggested the following script be used to install the projects on linux:

```sh
mkdir CCompilerPython
cd CCompilerPython

echo "Downloading CCompiler"
git clone https://github.com/CarterTS/CCompiler

echo "Downloading DemoProcessor"
git clone https://github.com/CarterTS/DemoProcessor

cd DemoProcessor
echo "Building Demo Processor"
make main

echo "Done"
```

It is then suggested that one put the following script in the root of the CCompiler repository in a file titled, 'run.sh'

```sh

#!/bin/bash

python3 ../DemoProcessor/assembler/main.py $1 ../DemoProcessor/result.bin 
../DemoProcessor/main ../DemoProcessor/result.bin
```

Using this one can run a program compiled with the compiler using

```
./run file
```

## Requirements

Requires Python 3.7 or higher
