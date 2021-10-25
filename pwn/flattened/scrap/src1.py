import qiling
import pwn
import shutil
import os
import subprocess
import capstone.x86_const

pwn.context.arch = "amd64"
dump = []


def code_hook(ql, address, size):
    global dump
    buf = ql.mem.read(address, size)
    for i in md.disasm(buf, address):
        allowed_syscalls = {1, 0x3c}
        if (
            capstone.x86_const.X86_GRP_INT in i.groups
            and ql.reg.eax not in allowed_syscalls
        ):
            print(f"syscall = {hex(ql.reg.eax)}")
            raise ValueError("HACKING DETECTED!")

        ignored_groups = {
            capstone.x86_const.X86_GRP_JUMP,
            capstone.x86_const.X86_GRP_CALL,
            capstone.x86_const.X86_GRP_RET,
            capstone.x86_const.X86_GRP_IRET,
            capstone.x86_const.X86_GRP_BRANCH_RELATIVE,
        }
        ignore = len(set(i.groups) & ignored_groups) > 0

        print(
            f"[{' ' if ignore else '+'}] {hex(i.address)}: {i.mnemonic} {i.op_str}"
        )
        if not ignore:
            dump.append(bytes(i.bytes))


inp = input("Enter code in hex:\n")
code = bytes.fromhex(inp)

ql = qiling.Qiling(
    code=code,
    rootfs="/",
    ostype="linux",
    archtype="x8664",
    # verbose=qiling.const.QL_VERBOSE.DISASM,
)

ql.hook_code(code_hook)
md = ql.create_disassembler()
md.detail = True
ql.run()

print(dump)
a = b"".join(dump)
filename = pwn.make_elf(a, extract=False, vma=0x11FF000)
shutil.copyfile(filename, "./flat")
os.chmod("./flat", 0o775)
subprocess.run(["./flat"])
