#/bin/sh
gcc -O0 main.c -o gadget-udiv-17c.elf
objdump -d gadget-udiv-17c.elf > disas-gadget.txt
