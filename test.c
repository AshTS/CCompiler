#include "display.h"

struct Data
{
    int value0;
    int value1;
};

int main()
{
    struct Data data;

    data.value0 = 5;
    data.value1 = 7;

    print_number(data.value0);
    put_char('\n');
    print_number(data.value1);
}

