int add(int a, int b)
{
    return (a += b, a);
}

/*struct LinkedList
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

    if (list->next != 0)
    {
        traverse(list->next);
    }
}

int main(int argc, char** argv)
{
    // LinkedList list = {4, 0};
    // LinkedList v0 = {5, 0};
    // LinkedList v1 = {2, 0};

    append(&list, &v0);
    append(&list, &v1);
    
    traverse(&list);

    return 0;
}*/