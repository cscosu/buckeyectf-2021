from Crypto.Util.number import size, long_to_bytes
from Crypto.Cipher import AES
import os
import hashlib

os.environ["PWNLIB_NOTERM"] = "true"
import pwn

p = 2 ^ 255 - 19
E = EllipticCurve(GF(p), [0, 486662, 0, 1, 0])

for i in range(100):
    try:
        P = E.lift_x(Integer(i))
        if P.order() == E.order():
            break
    except:
        pass
else:
    raise ValueError("Couldn't find a base point")

A = P * (E.order() // 8)
assert A.order() == 8

subgroup = [(A * i) for i in range(1, 8 + 1)]
xs = sorted([A.xy()[0] for A in subgroup if not A.is_zero()])
keys = [hashlib.sha1(long_to_bytes(x)).digest()[:16] for x in xs]

if pwn.args.REMOTE:
    io = pwn.remote("localhost", 1024)
else:
    io = pwn.process("python3 ../src/chall.py", shell=True)

io.sendlineafter("x: ", str(xs[-1]))

ct = bytes.fromhex(io.recvlineS().strip())
for key in keys:
    cipher = AES.new(key, AES.MODE_ECB)
    print(cipher.decrypt(ct))
