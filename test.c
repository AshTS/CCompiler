#include <stdio.h>
#include <stdio.h>

#define IGNORE

int main()
{
    #ifndef IGNORE
    int i = 0;
    switch (i)
    {
        case 0:
            printf("Hi\n");
            break;
        case 1:
        case 2:
            printf("Good ");
        default:
            printf("Bye!\n");
    }
    #else
    printf("IGNORED!");
    #endif

    return 0;
}
