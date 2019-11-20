#include <stdio.h>

struct Point
{
    float x;
    float y;
    float z;
};

typedef struct Point Point;

int main(int argc, char** argv)
{
    Point point = {0.0, 1.0, -3.14};
    printf("%f", point.x);
}