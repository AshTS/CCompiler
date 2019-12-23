ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after

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


# void put_char(char val)
put_char:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R4, R0, 0
ADD R5, R0, 28672
ADD R6, R0, 0
RB R6, R5
ADD R4, R0, R6
ADD R7, R0, 0
ADD R5, R0, 28673
ADD R8, R0, 0
RB R8, R5
ADD R7, R0, R8
ADD R5, R0, 32768
ADD R9, R0, 128
ADD R10, R0, 0
MUL R10, R7, R9
ADD R9, R0, 2
ADD R11, R0, 0
MUL R11, R4, R9
ADD R12, R0, 0
ADD R12, R10, R11
ADD R13, R0, 0
ADD R13, R5, R12
ADD R5, R0, R13
SB R5, R3
ADD R5, R0, 28672
ADD R9, R0, 1
ADD R14, R0, 0
ADD R14, R4, R9
SB R5, R14
put_char_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void clear_display()
clear_display:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, 32
ADD R4, R0, 0
ADD R4, R0, 28672
ADD R5, R0, 0
ADD R5, R0, 0
SB R4, R5
ADD R6, R0, 0
ADD R6, R0, 28673
ADD R7, R0, 0
ADD R7, R0, 0
SB R6, R7
ADD R8, R0, 0
ADD R8, R0, 0
clear_display_L0:
ADD R9, R0, 0
ADD R9, R0, 1024
ADD R10, R0, 0
CL R10, R8, R9
CE R15, R10, 0
JF R15, clear_display_L1
SUB R2, R2, 2
SW R2, R8
JL R1, put_char
RW R8, R2
ADD R2, R2, 2
ADD R11, R0, 0
ADD R11, R8, 1
ADD R8, R0, R11
J clear_display_L0
clear_display_L1:
ADD R12, R0, 28672
ADD R13, R0, 0
SB R12, R13
ADD R12, R0, 28673
ADD R13, R0, 0
SB R12, R13
clear_display_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, 72
ADD R4, R0, 28672
ADD R5, R0, 0
SB R4, R5
ADD R4, R0, 28673
ADD R5, R0, 0
SB R4, R5
JL R1, clear_display
JL R1, put_char
ADD R3, R0, 101
JL R1, put_char
ADD R3, R0, 108
JL R1, put_char
ADD R3, R0, 108
JL R1, put_char
ADD R3, R0, 111
JL R1, put_char
JL R1, update_display
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

