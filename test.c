#include "display.h"

int main()
{
    clear_display();

    for (int i = 0; i < 10; i++)
    {
        print_number(i);
        put_char('\n');
    }

    while(1);

    return 0;
}

