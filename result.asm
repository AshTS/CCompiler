ADD R3, R0, 0
ADD R4, R0, 0
ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after

# int fact(int a)
fact:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
CLE R5, R3, R4
CE R15, R5, 0
JF R15, fact_L0
ADD R15, R0, R6
J fact_ret
fact_L0:
fact_L1:
SUB R8, R3, R7
ADD R9, R0, R8
SUB R2, R2, 2
SW R2, R3
SUB R2, R2, 2
SW R2, R4
SUB R2, R2, 2
SW R2, R5
SUB R2, R2, 2
SW R2, R6
ADD R3, R0, R9
JL R1, fact
ADD R10, R0, R15
RW R6, R2
ADD R2, R2, 2
RW R5, R2
ADD R2, R2, 2
RW R4, R2
ADD R2, R2, 2
RW R3, R2
ADD R2, R2, 2
MUL R11, R10, R3
ADD R15, R0, R11
fact_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, R3
main_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void _start()
_start:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
_start_ret:
RW R1, R2
ADD R2, R2, 2
J R1

__after:

