#include <stdio.h>
#include <stdint.h>

int main() {
    uint64_t diff;

    // Initialize iteration (x4)
    asm volatile (
        "mov x4, #1000  \n"
        "mul x4, x4, x4 \n"
    );

    // Initialize gadget (operands x7, x8)
    asm volatile (
        "mov x7, #0xff00000000000000 \n"
        "mov x8, #0x1234             \n"
    );

    // Start measuring
    asm volatile ("msr pmcr_el0, %0" : : "r"(0x00000001)); 
    asm volatile ("mrs x0, pmccntr_el0");

    // Code to be measured
    asm volatile (
        "gadget:         \n"
// ============ Gadget below ============
        "udiv x6, x7, x8 \n"
// ======================================
        "subs x4, x4, #1 \n"
        "bne gadget      \n"
    );

    // Read final counter value
    asm volatile (
        "mrs x1, pmccntr_el0 \n"
        "sub x2, x1, x0      \n"
        "mov %0, x2" : "=r"(diff)
    );

    printf("Cycles: %llu\n", diff);
    return 0;
}
