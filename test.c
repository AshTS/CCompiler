#include <stdio.h>

typedef int* INT_ARRAY;

enum Test
{
    VAL0,
    VAL1,
    VAL8=8,
    VAL9,
    VAL10,
    VAL3=3,
    VAL4
};

int main(int argc, char** argv)
{
    int array[100];

    INT_ARRAY new_array = array;
}