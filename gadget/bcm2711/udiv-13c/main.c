#include <stdio.h>

int main()
{
    asm volatile (
        "mov  x1, #0               \n"
        "movk x1, #0x5678, LSL #32 \n"
        "movk x1, #0x1234, LSL #16 \n"
        "movk x1, #0x5678          \n"
        "mov  x2, #0x1234          \n"
    );

    asm volatile (
        "gadget:         \n"
        "udiv x0, x1, x2 \n"
        "b gadget        \n"
    );
    return 0;
}
