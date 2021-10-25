import pwn
import random

pwn.context.arch = "amd64"

for i in range(256):
    print(pwn.disasm(bytes([i, 0x05, random.randrange(256)])))
    print()
