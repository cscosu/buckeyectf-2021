import pwn
import shutil
import os

pwn.context.arch = "amd64"
pwn.context.log_level = "WARN"

elf = pwn.ELF(f"./solve")
f = elf.functions["main"]
a = elf.read(f.address, f.size)
print(a.hex())
# a = pwn.disasm(s)
# print(a)

filename = pwn.make_elf(a, extract=False)
shutil.copyfile(filename, "./solve_pwn")
os.chmod("./solve_pwn", 0o775)
