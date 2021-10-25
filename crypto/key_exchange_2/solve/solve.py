import pwn
import Crypto.Util.number as cun
from Crypto.Cipher import AES
import hashlib
import random

def go():
    if pwn.args.REMOTE:
        # io = pwn.remote("localhost", 1024)
        io = pwn.remote("crypto.chall.pwnoh.io", 13386)
    else:
        io = pwn.process("python3 ../deploy/server.py", shell=True)

    io.recvuntil("decrypt the flag.\n")
    io.recvline()

    p = int(io.recvlineS().strip().split(" = ")[-1])
    g = int(io.recvlineS().strip().split(" = ")[-1])

    for i in range(3, 1024):
        if (p - 1) % i == 0:
            break
    else:
        io.close()
        return False

    print(i)
    b = (p - 1) // i
    B = pow(g, b, p)
    if B == 1 or B == (p - 1):
        return False

    io.sendlineafter("Give me your public key B: ", str(B))

    ct = bytes.fromhex(io.recvlineS().strip().split(" = ")[-1])
    print(f"ct = {ct}")

    shared_secrets = [B]
    x = B
    while x != 1:
        x = (x * B) % p
        shared_secrets.append(x)

    print(shared_secrets)
    for shared_secret in shared_secrets:
        key = hashlib.sha1(cun.long_to_bytes(shared_secret)).digest()[:16]
        cipher = AES.new(key, AES.MODE_ECB)
        pt = cipher.decrypt(ct)
        print(pt)

    io.close()
    return True


while True:
    if go():
        break
