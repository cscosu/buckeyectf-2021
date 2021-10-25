.intel_syntax noprefix
.global main
.type main, @function
main:

mov r10, 5
cmp r10, 5

je no

/* write("bark") */
mov rdi, 0x0a6b726162
push rdi
mov eax, 0x1
mov rdi, 0x1
mov rsi, rsp
mov rdx, 0x5
syscall

jmp done

no:
/* write("barl") */
mov rdi, 0x0a6c726162
push rdi
mov eax, 0x1
mov rdi, 0x1
mov rsi, rsp
mov rdx, 0x5
syscall

mov rdi, 0x68732f6e69622f
push rdi
mov eax, 0x3b
mov rdi, rsp
mov rsi, 0
mov rdx, 0
syscall


.size main, .-main
