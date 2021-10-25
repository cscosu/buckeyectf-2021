    .intel_syntax noprefix
    .text

    .section .rodata
gift:
    .string "/bin/sh"
message:
    .string "HELLO HOW ARE YOU DOING TODAY\n"

    .text
    .globl main
    .type main, @function
main:
    # char buf[128]
    endbr64
    push rbp
    mov rbp, rsp
    sub rsp, 128

    # write(1, message, 30)
    mov rax, 1
    mov rdi, 1
    lea rsi, message
    mov rdx, 30
    syscall

    # read(0, buf, 0x1000)
    mov rax, 0
    mov rdi, 0
    mov rsi, rsp
    mov rdx, 0x1000
    syscall

    mov eax, 0

    # epilogue
    leave
    ret
    .size main, .-main

gadgets:
    pop rax
    ret

    syscall
    ret
