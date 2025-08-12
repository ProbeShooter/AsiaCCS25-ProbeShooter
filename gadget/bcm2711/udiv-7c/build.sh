#/bin/sh
gcc -O0 main.c -o gadget-udiv-7c.elf
objdump -d gadget-udiv-7c.elf > disas-gadget.txt
