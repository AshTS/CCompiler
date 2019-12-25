/*#include "display.h"

char fib(int n)
{
    if (n < 2)
    {
        return 1;
    }

    return fib(n - 1) + fib(n - 2);
}

int ack(int m, int n)
{
    int answer;
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
    
    return answer;
}

int main()
{
    clear_display();

    print("Ackerman\n");

    int i = 4;
    int j = 1;

    print("Ackerman of ");
    print_number(i);
    print(" and ");
    print_number(j);
    print(" is: ");
    print_number(ack(i, j));
    put_char('\n');

    while (1);

    return 0;
}*/

int main()
{
    // int data[10];
}