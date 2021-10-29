from pwn import *

p = process("./piss1")
p.recvuntil("Type some hex (end with newline):")

context.arch = "amd64"
code = """
mov rdi, 1
lea rsi, [rip+hello]
mov rdx, 12
mov eax, 1
syscall

hello:
.string "Hello world!"
"""
print(code)

assembled = asm(code)
p.sendline(assembled.hex())

p.interactive()
