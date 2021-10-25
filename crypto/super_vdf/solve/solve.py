import gmpy2
import math
from functools import reduce
from operator import mul
import pwn


PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]


def pollards_rho(n):
    x = 2
    for _ in range(30):
        x = pow(x, reduce(mul, PRIMES), n)
        g = gmpy2.gcd(x - 1, n)
        if 1 < g < n:
            return g

    raise ValueError("Fail")


def factor(x):
    # Trial division
    ans = []
    for p in PRIMES:
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        ans.append((p, e))
    return ans


def euler_phi(x):
    factors = factor(x)
    phi = 1
    for f in factors:
        p, e = f
        if e > 0:
            phi *= (p - 1) * pow(p, e - 1)
    return phi


if pwn.args.REMOTE:
    # io = pwn.remote("localhost", 1024)
    io = pwn.remote("crypto.chall.pwnoh.io", 13376)
else:
    io = pwn.process("python3 ../deploy/chall.py", shell=True)

n = int(io.recvlineS().strip().split("=")[1])
p = pollards_rho(n)
assert 1 < p < n
assert n % p == 0
q = n // p

e = 1333337
phi = (p - 1) * (q - 1)
phi1 = euler_phi(phi)
phi2 = euler_phi(phi1)
a = pow(59, e, phi2)
b = pow(59, a, phi1)
c = pow(59, b, phi)
d = pow(59, c, n)

io.sendlineafter(">>> ", str(d))
io.interactive()
