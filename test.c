//#include <stdio.h>

/*
void clear_screen(unsigned int addr)
{
    int i = 0;
    while (i < 16)
    {
        for (int j = 0; j < 64; j++)
        {
            *((unsigned char*)addr) = 0x20;
            addr += 2;
        }
        i++;
    }
}*/

int factorial(int i)
{
    return (i == 1) ? 1 : (i * factorial(i - 1));
}

int main(int argc, char** argv)
{
    clear_screen(0x8000);

    return 0;
}