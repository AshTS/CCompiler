ADD R3, R0, 0
ADD R4, R0, 0
ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after

# int fact1(int a)
fact1:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 1
fact1_L1:
fact1_L0:
fact1_ret:
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

