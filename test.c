

struct LinkedList
{
    int value;
    struct LinkedList* next;
};

typedef struct LinkedList LinkedList;

/*
void append(LinkedList* list, LinkedList* val)
{
    if (list->next == NULL)
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
    printf("Number: %i\n", list->value);

    if (list->next != NULL)
    {
        traverse(list->next);
    }
}

int main(int argc, char** argv)
{
    LinkedList list = {4, NULL};
    LinkedList v0 = {5, NULL};
    LinkedList v1 = {2, NULL};

    append(&list, &v0);
    append(&list, &v1);
    
    traverse(&list);

    return 0;
}*/