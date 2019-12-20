int fact(int a)
{
    if (a <= 1)
    {
        return 1;
    }

    return fact(a - 1) * a;
}

int main()
{
    int a = 1;
    
    int b = fact(a);

    return b;
}
