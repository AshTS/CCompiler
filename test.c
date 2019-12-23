void update_display()
{
    *((char*)0x7FFF) = 1;
}

void put_char(char val)
{
    char x = *((char*)0x7000);
    char y = *((char*)0x7001);
    *((char*)(0x8000 + y * 128 + x * 2)) = val;

    *((char*)0x7000) = x + 1;
}

void clear_display()
{
    *((char*)0x7000) = 0; //X
    *((char*)0x7001) = 0; //Y
    
    int i = 0;
    while (i < 1024)
    {
        put_char(' ');
        i++;
    }

    *((char*)0x7000) = 0; //X
    *((char*)0x7001) = 0; //Y
}

int main()
{
    *((char*)0x7000) = 0; //X
    *((char*)0x7001) = 0; //Y

    clear_display();
    put_char('H');
    put_char('e');
    put_char('l');
    put_char('l');
    put_char('o');
    update_display();
    return 0;
}