ADD R2, R0, 4096
ADD R15, R0, 65534
ADD R14, R0, 61440
SW R15, R14
ADD R15, R0, 65534
RW R15, R14
ADD R14, R14, 10
SW R15, R14
SUB R14, R14, 10
ADD R1, R0, R14
JL R1, _start
JL R1, main
J __after
~
# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R13, R0, 0
main_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# void _start()
_start:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R13, R0, 0
_start_ret:
RW R1, R2
ADD R2, R2, 2
J R1

__after:

