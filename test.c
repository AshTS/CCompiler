#include "display.h"

char bubble_sort(char* array, int size);

int main()
{
    clear_display();

    char data[3];

    data[0] = 3;
    data[1] = 1;
    data[2] = 2;

    for (int i = 0; i < 4; i++)
    {
        print_number((int)data[i]);
        put_char(' ');
    }

    put_char('\n');

    bubble_sort(data, 3);

    for (int i = 0; i < 4; i++)
    {
        print_number((int)data[i]);
        put_char(' ');
    }
    
    while (1);

    return 0;
}


char bubble_sort(char* array, int size)
{
    if (size < 2)
    {
        return 0;
    }

    char is_sorted = 1;

    for (int i = 0; i < size - 1; i++)
    {
        if (array[i] > array[i + 1])
        {
            char temp = array[i + 1];
            array[i + 1] = array[i];
            array[i] = temp;
            is_sorted = 0;
        }
    }

    if (is_sorted)
    {
        return 0;
    }
    else
    {
        bubble_sort(array, size);
    }
    
}