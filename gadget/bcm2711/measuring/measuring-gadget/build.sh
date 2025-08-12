#/bin/sh
gcc -O0 main.c -o measuring-gadget.elf
objdump -d measuring-gadget.elf > disas-gadget.txt
