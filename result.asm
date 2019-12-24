ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after
~ 46 69 62 6F 6E 61 63 63 69 0A 00
# void update_display()
update_display:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, 32767
ADD R4, R0, 1
SB R3, R4
update_display_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void halt()
halt:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, 65535
ADD R4, R0, 1
SB R3, R4
halt_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void insert_char(char val, char x, char y)
insert_char:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R6, R0, 0
MUL R6, R5, 128
ADD R7, R0, 0
MUL R7, R4, 2
ADD R8, R0, 0
ADD R8, R6, R7
ADD R6, R0, 0
ADD R6, R8, 32768
ADD R7, R0, R6
SB R7, R3
insert_char_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void clear_display()
clear_display:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, 28672
ADD R4, R0, 28672
ADD R5, R0, 28672
ADD R3, R0, 0
SB R5, R3
ADD R3, R0, 28673
ADD R4, R0, 0
SB R3, R4
ADD R5, R0, 0
clear_display_L0:
ADD R3, R0, 1024
ADD R4, R0, 0
CL R4, R5, R3
CE R15, R4, 0
JF R15, clear_display_L1
SUB R2, R2, 2
SW R2, R5
ADD R3, R0, 32
ADD R4, R0, R5
ADD R5, R0, 0
JL R1, insert_char
RW R5, R2
ADD R2, R2, 2
ADD R3, R0, 0
ADD R3, R5, 1
ADD R5, R0, R3
J clear_display_L0
clear_display_L1:
ADD R3, R0, 28672
ADD R4, R0, 0
SB R3, R4
ADD R3, R0, 28673
ADD R4, R0, 0
SB R3, R4
JL R1, update_display
clear_display_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# char put_char(char val)
put_char:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R4, R0, 0
CE R4, R3, 10
CE R15, R4, 0
JF R15, put_char_L0
ADD R5, R0, 28672
ADD R4, R0, 28672
ADD R5, R0, 0
SB R4, R5
ADD R4, R0, 28673
ADD R5, R0, 28673
ADD R6, R0, 0
RB R6, R5
ADD R5, R0, 0
ADD R5, R6, 1
SB R4, R5
J put_char_ret
put_char_L0:
put_char_L1:
ADD R4, R0, 0
ADD R4, R0, 28672
ADD R5, R0, 0
RB R5, R4
ADD R4, R0, R5
ADD R6, R0, 28673
ADD R7, R0, 0
RB R7, R6
ADD R6, R0, R3
SUB R2, R2, 2
SW R2, R4
ADD R3, R0, R6
ADD R4, R0, R5
ADD R5, R0, R7
JL R1, insert_char
RW R4, R2
ADD R2, R2, 2
ADD R5, R0, 28672
ADD R6, R0, 0
ADD R6, R4, 1
SB R5, R6
put_char_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void print(char* data)
print:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R4, R0, R3
ADD R3, R0, R4
print_L0:
ADD R4, R0, 0
RB R4, R3
CE R15, R4, 0
JF R15, print_L1
ADD R4, R0, 0
RB R4, R3
SUB R2, R2, 2
SW R2, R3
ADD R3, R0, R4
JL R1, put_char
RW R3, R2
ADD R2, R2, 2
ADD R4, R0, 0
ADD R4, R3, 1
ADD R3, R0, R4
J print_L0
print_L1:
JL R1, update_display
print_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void print_number(unsigned char num)
print_number:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R4, R0, 9
ADD R5, R0, 0
CNLE R5, R3, R4
CE R15, R5, 0
JF R15, print_number_L0
ADD R4, R0, 0
DIV R4, R3, 10
ADD R5, R0, 0
ADD R5, R4, 48
SUB R2, R2, 2
SW R2, R3
ADD R3, R0, R5
JL R1, put_char
RW R3, R2
ADD R2, R2, 2
print_number_L0:
print_number_L1:
ADD R4, R0, 0
DIV R4, R3, 10
ADD R5, R0, 0
MUL R5, R4, 10
ADD R4, R0, 0
SUB R4, R3, R5
ADD R3, R0, R4
ADD R4, R0, 0
ADD R4, R3, 48
ADD R3, R0, R4
JL R1, put_char
JL R1, update_display
print_number_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# char fib(int n)
fib:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 1
ADD R4, R0, 2
ADD R5, R0, 0
CL R5, R3, R4
CE R15, R5, 0
JF R15, fib_L0
J fib_ret
fib_L0:
fib_L1:
ADD R4, R0, 0
SUB R4, R3, 1
SUB R2, R2, 2
SW R2, R3
ADD R3, R0, R4
JL R1, fib
ADD R4, R0, R15
RW R3, R2
ADD R2, R2, 2
ADD R5, R0, 0
SUB R5, R3, 2
SUB R2, R2, 2
SW R2, R4
ADD R3, R0, R5
JL R1, fib
ADD R5, R0, R15
RW R4, R2
ADD R2, R2, 2
ADD R6, R0, 0
ADD R6, R4, R5
ADD R15, R0, R6
fib_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
JL R1, clear_display
ADD R3, R0, 16
JL R1, print
ADD R4, R0, 0
main_L0:
ADD R3, R0, 10
ADD R5, R0, 0
CL R5, R4, R3
CE R15, R5, 0
JF R15, main_L1
SUB R2, R2, 2
SW R2, R4
ADD R3, R0, R4
JL R1, fib
RW R4, R2
ADD R2, R2, 2
SUB R2, R2, 2
SW R2, R4
ADD R3, R0, R15
JL R1, print_number
RW R4, R2
ADD R2, R2, 2
SUB R2, R2, 2
SW R2, R4
ADD R3, R0, 10
JL R1, put_char
RW R4, R2
ADD R2, R2, 2
ADD R3, R0, 0
ADD R3, R4, 1
ADD R4, R0, R3
J main_L0
main_L1:
main_L2:
ADD R3, R0, 1
CE R15, R3, 0
JF R15, main_L3
J main_L2
main_L3:
ADD R15, R0, 0
main_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void _start()
_start:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
_start_ret:
RW R1, R2
ADD R2, R2, 2
J R1

__after:

