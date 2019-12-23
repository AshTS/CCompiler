#include "display.h"

char fib(int n)
{
    if (n < 2)
    {
        return 1;
    }

    return fib(n - 1) + fib(n - 2);
}

int main()
{
    clear_display();

    print("Fibonacci\n");

    char i = 0;
    while (i < 10)
    {
        print_number(fib(i));
        put_char('\n');
        i += 1;
    }

    while (1);

    return 0;
}