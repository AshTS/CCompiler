ADD R3, R0, 0
ADD R4, R0, 0
ADD R2, R0, 4096
JL R1, _start
JL R1, main
J __after

# int update_display()
update_display:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R5, R0, 32767
ADD R6, R0, 1
SB R5, R6
update_display_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int place_char(char c)
place_char:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R6, R0, 32768
SB R6, R3
place_char_ret:
RW R1, R2
ADD R2, R2, 2
J R1


# int main()
main:
SUB R2, R2, 2
SW R2, R1
ADD R1, R0, 0
ADD R15, R0, 0
ADD R3, R0, G0
ADD R3, R0, R3
JL R1, place_char
JL R1, update_display
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
ADD G0, R0, 65
_start_ret:
RW R1, R2
ADD R2, R2, 2
J R1

__after:

