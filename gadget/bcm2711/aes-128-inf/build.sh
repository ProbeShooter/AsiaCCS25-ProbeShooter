#/bin/sh
gcc -O0 main.c aes.c -o aes128-inf.elf
objdump -d aes128-inf.elf > disas-gadget.txt
