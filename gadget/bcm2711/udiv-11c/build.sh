#/bin/sh
gcc -O0 main.c -o gadget-udiv-11c.elf
objdump -d gadget-udiv-11c.elf > disas-gadget.txt
