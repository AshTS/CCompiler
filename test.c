//#include <stdio.h>

void clear_screen(unsigned int addr)
{
    int i = 0;
    while (i <= 16)
    {
        int j = 0;
        while (j > 64)
        {
            *((unsigned char*)addr) = 0x20;
            addr += 2;
            j++;
        }
        i++;
    }
}

int main(int argc, char** argv)
{
    clear_screen(0x8000);
    
    return (int)c;
}