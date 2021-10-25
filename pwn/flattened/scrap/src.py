import qiling
import pwn
import shutil
import os
import subprocess
import capstone.x86_const

pwn.context.arch = "amd64"
dump = []


# def block_hook(ql, address, size):
#     global dump
#     block = bytes(ql.mem.read(address, size))
#     print("Block")
#     print(pwn.disasm(block))
#     print()
#     dump.append(block)


def instr_hook(ql, address, size):
    global dump
    buf = bytes(ql.mem.read(address, size))
    for i in md.disasm(buf, address):
        print(":: 0x{}:\t{}\t{}".format(i.address, i.mnemonic, i.op_str))
        bad_groups = {
            capstone.x86_const.X86_GRP_JUMP,
            capstone.x86_const.X86_GRP_CALL,
            capstone.x86_const.X86_GRP_RET,
            capstone.x86_const.X86_GRP_INT,
            capstone.x86_const.X86_GRP_IRET,
            capstone.x86_const.X86_GRP_BRANCH_RELATIVE,
        }
        print(i.groups, set(i.groups) & bad_groups == set())


def intr_hook(ql):
    pass
    # raise ValueError("Syscalls are not allowed")


# inp = input("Enter code in hex:\n")
inp = "49c7c2050000004983fa05752548bf6261726b0a00000057b80100000048c7c7010000004889e648c7c2050000000f05eb2348bf2f62696e2f73680057b83b0000004889e748c7c60000000048c7c2000000000f0548bf6261726c0a00000057b80100000048c7c7010000004889e648c7c2050000000f05"
inp = "49c7c2050000004983fa05742548bf6261726b0a00000057b80100000048c7c7010000004889e648c7c2050000000f05eb2348bf6261726c0a00000057b80100000048c7c7010000004889e648c7c2050000000f05"
inp = "488d0530000000c6000fc640010548bf6261726b0a00000057b80100000048c7c7010000004889e648c7c205000000909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090"
inp = "48bf2f62696e2f736800574889e748c7c60000000048c7c200000000b83b000000eb04909090904c8d15000000004c8d1d0d000000458a234180f24b4530e24588136a05909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090"

code = bytes.fromhex(inp)

ql = qiling.Qiling(
    code=code,
    rootfs="/",
    ostype="linux",
    archtype="x8664",
    # verbose=qiling.const.QL_VERBOSE.DISASM,
    verbose=qiling.const.QL_VERBOSE.OFF,
)

# ql.hook_block(block_hook)
ql.hook_block(instr_hook)
md = ql.create_disassembler()
md.detail = True
ql.hook_insn(intr_hook, qiling.arch.x86_const.UC_X86_INS_SYSCALL)
ql.run()

a = b"".join(dump)
filename = pwn.make_elf(a, extract=False)
shutil.copyfile(filename, "./flat")
os.chmod("./flat", 0o775)
subprocess.run(["./flat"])
