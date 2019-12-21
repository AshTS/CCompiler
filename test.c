int a = 65;

int update_display()
{
    *((char*)0x7FFF) = 1;
}

int place_char(char c)
{
    *((char*)0x8000) = c;
}

int main()
{
    place_char(a);
    update_display();
}