#include "display.h"

char fib(int n)
{
    if (n < 2)
    {
        return 1;
    }

    return fib(n - 1) + fib(n - 2);
}

char ack(int m, int n)
{
    char answer;
    if (m == 0)
    {
        answer = n + 1;
    }
    else if (n == 0)
    {
        answer = ack(m - 1, 1);
    }
    else
    {
        answer = ack(m - 1, ack(m, n-1));
    }
    
    return (char)answer;
}

int main()
{
    clear_display();

    print("Ackerman\n");

    for (int i = 0; i < 4; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            print("Ackerman of ");
            print_number((char)i);
            print(" and ");
            print_number((char)j);
            print(" is: ");
            print_number(ack(i, j));
            put_char('\n');
        }
    }
    

    while (1);

    return 0;
}