//#include <stdio.h>

char get_char()
{
    return 'a';
}

int main(int argc, char** argv)
{
    int a = 0;

    if (a - 1)
    {
        a = 0;
    }
    else if (a + 1)
    {
        a = 2;
    }
    else
    {
        a = 1;
    }

    return a;
}