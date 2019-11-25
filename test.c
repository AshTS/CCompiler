//#include <stdio.h>

char get_char()
{
    return 'a';
}

int main(int argc, char** argv)
{
    char* hello = "Hello World!";
    char* hello2 = "hello world!";
    return hello[0] + hello2[0];
}