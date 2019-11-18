#include <stdio.h>
#define MIN(a, b) ((a) < (b) ? (a) : (b))

int main()
{
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
}

/*#include "stdio.h"

struct LinkedList
{
    int value;
    struct LinkedList* next;
};

typedef struct LinkedList LinkedList;


void append(LinkedList* list, LinkedList* val)
{
    if (list->next == 0)
    {
        list->next = val;
    }
    else
    {
        append(list->next, val);
    }
}

void traverse(LinkedList* list)
{
    printf("Number: %s", list->value);

    if (list->next != 0)
    {
        traverse(list->next);
    }
}

int main(int argc, char** argv)
{
    LinkedList list;// = {4, 0};
    LinkedList v0;// = {5, 0};
    LinkedList v1;// = {2, 0};

    list.value = 4;
    list.next = 0;

    v0.value = 5;
    v0.next = 0;

    v1.value = 2;
    v1.next = 0;

    append(&list, &v0);
    append(&list, &v1);
    
    traverse(&list);

    int a = 0;

    char c = (char)a;

    return 0;
}*/