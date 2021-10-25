import pwn
import Crypto.Util.number as cun
from Crypto.Cipher import AES
import hashlib
import random

if pwn.args.REMOTE:
    io = pwn.remote("localhost", 1024)
else:
    io = pwn.process("python3 ../deploy/server.py", shell=True)

io.recvuntil("decrypt the flag.\n")
io.recvline()

p = int(io.recvlineS().strip().split(" = ")[-1])
g = int(io.recvlineS().strip().split(" = ")[-1])
A = int(io.recvlineS().strip().split(" = ")[-1])

b = random.randrange(2, p - 1)
B = pow(g, b, p)
io.sendlineafter("Give me your public key B: ", str(B))

ct = bytes.fromhex(io.recvlineS().strip().split(" = ")[-1])

shared_secret = pow(A, b, p)
key = hashlib.sha1(cun.long_to_bytes(shared_secret)).digest()[:16]
cipher = AES.new(key, AES.MODE_ECB)
pt = cipher.decrypt(ct)
print(pt)
