ADD R3, R0, 0
ADD R4, R0, 0
ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after

# int fact0(int a)
fact0:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 1
ADD R4, R0, 0
ADD R4, R0, 2
ADD R5, R0, 0
CL R5, R3, R4
CE R15, R5, 0
JF R15, fact0_L0
J fact0_ret
fact0_L0:
fact0_L1:
ADD R6, R0, 1
ADD R7, R0, 0
SUB R7, R3, R6
ADD R8, R0, R7
SUB R2, R2, 2
SW R2, R3
ADD R3, R0, R8
JL R1, fact0
ADD R9, R0, R15
RW R3, R2
ADD R2, R2, 2
ADD R10, R0, 0
MUL R10, R3, R9
ADD R15, R0, R10
fact0_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int fact1(int a)
fact1:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R4, R0, 1
ADD R5, R0, 0
ADD R5, R0, 2
ADD R6, R0, 0
CL R6, R3, R5
CE R15, R6, 0
JF R15, fact1_L1
J fact1_L0
fact1_L1:
ADD R7, R0, 1
ADD R8, R0, 0
SUB R8, R3, R7
ADD R9, R0, R8
SUB R2, R2, 2
SW R2, R3
ADD R3, R0, R9
JL R1, fact1
ADD R10, R0, R15
RW R3, R2
ADD R2, R2, 2
ADD R11, R0, 0
MUL R11, R3, R10
ADD R4, R0, R11
fact1_L0:
ADD R15, R0, R4
fact1_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int nouse(int a)
nouse:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 1
nouse_ret:
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

