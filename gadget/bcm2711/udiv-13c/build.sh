#/bin/sh
gcc -O0 main.c -o gadget-udiv-13c.elf
objdump -d gadget-udiv-13c.elf > disas-gadget.txt
