#include <stdio.h>

int main()
{
    asm volatile (
        "mov x1, #0xffffffffffffffff \n"
        "mov x2, #0xff11             \n"
    );

    asm volatile (
        "gadget:         \n"
        "udiv x0, x1, x2 \n"
        "b gadget        \n"
    );
    return 0;
}
