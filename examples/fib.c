#include "examples/display.h"

int fib(int i)
{
    if (i < 2)
    {
        return 1;
    }

    return fib(i - 1) + fib(i - 2);
}

int main()
{
    clear_display();

    for (int i = 0; i < 10; i++)
    {
        print("fib(");
        print_number(i);
        print(") = ");
        print_number(fib(i));
        print("\n");
    }

    while(1);

    return 0;
}