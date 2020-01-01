#include "examples/display.h"

struct Point
{
    int x;
    int y;
};

int display_struct(struct Point p)
{
    print("X: ");
    print_number(p.x);
    print("  Y: ");
    print_number(p.y);
}

int main()
{
    clear_display();

    struct Point p;

    p.x = 4;
    p.y = 7;

    display_struct(p);

    while (1);

    return 0;
}

