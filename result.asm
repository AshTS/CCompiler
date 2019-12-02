ADD R3, R0, 0
ADD R4, R0, 0
ADD R2, R0, 4096
JL R1, main
J __after

# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R3, R0, 4
ADD R15, R0, 0
J main_ret
main_ret:
RW R1, R2
ADD R2, R2, 2
J R1

__after:

