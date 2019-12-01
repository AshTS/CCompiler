void init()
{
    unsigned char* addr = 0x7000; 
    *addr = (char)0x01; // Write Horiz Position
    addr++;
    *addr = (char)0x01; // Write Vert Position
}

void clear_screen()
{
    unsigned char* addr = 0x8000;
    for (int i = 0; i < 1024; i++)
    {
        *addr = (char)0x20;
        addr += 2;
    }
}

void update_screen()
{
    unsigned char*addr = 0x7FFF;
    *addr = (char)0x01;
}

void put_ch(char v, unsigned char x, unsigned char y)
{
    unsigned char*addr = 2 * x + 128 * y + 0x8000;
    *addr = v;
}

int main()//int argc, char** argv)
{
    init();
    
    clear_screen();
    
    
    put_ch('A', 0, 0);
    put_ch('B', 1, 2);
    update_screen();

   return 0;
}
