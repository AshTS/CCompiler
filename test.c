int fact0(int a)
{
    if (a < 2)
    {
        return 1;
    }
    
    return a * fact0(a - 1);
}

int fact1(int a)
{
    return (a < 2) ? 1 : a * fact1(a - 1);
}

int nouse(int a)
{
    int c = 1;
    int d = c;
    int b = d;
    return b;
}