#ifndef DISPLAY_H
#define DISPLAY_H

void update_display()
{
    *((char*)0x7FFF) = 1;
}

void halt()
{
    *((char*)0xFFFF) = 1;
}

void insert_char(char val, char x, char y)
{
    *((char*)(0x8000 + y * 128 + x * 2)) = val;
}

void clear_display()
{
    *((char*)0x7000) = 0; //X
    *((char*)0x7001) = 0; //Y
    
    int i = 0;
    while (i < 1024)
    {
        insert_char(' ', i, 0);
        i++;
    }

    *((char*)0x7000) = 0; //X
    *((char*)0x7001) = 0; //Y

    update_display();
}



char put_char(char val)
{
    if (val == '\n')
    {
        *((char*)0x7000) = 0;
        *((char*)0x7001) = *((char*)0x7001) + 1;
        return 0;
    }
    char x = *((char*)0x7000);
    char y = *((char*)0x7001);

    insert_char(val, x, y);

    *((char*)0x7000) = x + 1;
}

void print(char* data)
{
    data = (char*)data;

    while (*data)
    {
        put_char(*(data));
        
        data++;
    }

    update_display();
}

void print_number(unsigned short num)
{
    if (num > 99999)
    {
        put_char('0' + num / 100000);
    }

    num -= (num / 100000) * 100000;

    if (num > 9999)
    {
        put_char('0' + num / 10000);
    }

    num -= (num / 10000) * 10000;

    if (num > 999)
    {
        put_char('0' + num / 1000);
    }

    num -= (num / 1000) * 1000;

    if (num > 99)
    {
        put_char('0' + num / 100);
    }

    num -= (num / 100) * 100;

    if (num > 9)
    {
        put_char('0' + num / 10);
    }

    num -= (num / 10) * 10;

    put_char('0' + num);

    update_display();
}

#endif //DISPLAY_H