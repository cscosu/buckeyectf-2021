

# This file was *autogenerated* from the file solve.sage
from sage.all_cmdline import *   # import sage library

_sage_const_2 = Integer(2); _sage_const_255 = Integer(255); _sage_const_19 = Integer(19); _sage_const_0 = Integer(0); _sage_const_486662 = Integer(486662); _sage_const_1 = Integer(1); _sage_const_100 = Integer(100); _sage_const_8 = Integer(8); _sage_const_16 = Integer(16); _sage_const_1024 = Integer(1024)
from Crypto.Util.number import size, long_to_bytes
from Crypto.Cipher import AES
import os
import hashlib

os.environ["PWNLIB_NOTERM"] = "true"
import pwn

p = _sage_const_2  ** _sage_const_255  - _sage_const_19 
E = EllipticCurve(GF(p), [_sage_const_0 , _sage_const_486662 , _sage_const_0 , _sage_const_1 , _sage_const_0 ])

for i in range(_sage_const_100 ):
    try:
        P = E.lift_x(Integer(i))
        if P.order() == E.order():
            break
    except:
        pass
else:
    raise ValueError("Couldn't find a base point")

A = P * (E.order() // _sage_const_8 )
assert A.order() == _sage_const_8 

subgroup = [(A * i) for i in range(_sage_const_1 , _sage_const_8  + _sage_const_1 )]
xs = sorted([A.xy()[_sage_const_0 ] for A in subgroup if not A.is_zero()])
keys = [hashlib.sha1(long_to_bytes(x)).digest()[:_sage_const_16 ] for x in xs]

if pwn.args.REMOTE:
    io = pwn.remote("localhost", _sage_const_1024 )
else:
    io = pwn.process("python3 ../src/chall.py", shell=True)

io.sendlineafter("x: ", str(xs[-_sage_const_1 ]))

ct = bytes.fromhex(io.recvlineS().strip())
for key in keys:
    cipher = AES.new(key, AES.MODE_ECB)
    print(cipher.decrypt(ct))
