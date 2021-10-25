.intel_syntax noprefix
.global main
.type main, @function
main:

mov rdi, 0x68732f6e69622f
push rdi
mov rdi, rsp
mov rsi, 0
mov rdx, 0

mov eax, 0x3b

jmp skip
nop
skip:

lea rcx, [rip]
cmp cl, 0x2b
sete bl
add eax, ebx

syscall

.size main, .-main
