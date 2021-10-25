import pwn
import Crypto.Util.number as cun
import random
import gmpy2
from functools import reduce
from itertools import chain
from operator import mul
import Crypto.Util.number as cun
from statistics import mode

# This should not work!

rand = random.SystemRandom()


def is_prime(n, rounds=32):
    return all(pow(rand.randrange(2, n), n - 1, n) == 1 for _ in range(rounds))


def byte_to_bits(s: int):
    return [int(x) for x in bin(s)[2:].zfill(8)]


def bytes_to_bits(s: bytes):
    return list(chain(*[byte_to_bits(b) for b in s]))


def bits_to_bytes(s):
    return cun.long_to_bytes(int("".join(str(x) for x in s), 2))


def carmichael(start):
    start = start if start % 2 == 0 else start - 1
    k = start
    while True:
        p1 = 6 * k + 1
        p2 = 12 * k + 1
        p3 = 18 * k + 1
        if cun.isPrime(p1) and cun.isPrime(p2) and cun.isPrime(p3):
            n = p1 * p2 * p3
            return n
        k += 2


k = 1 << (450 // 3)
k = gmpy2.mpz(k)
n = carmichael(k)
print(is_prime(n))
print(n)
n = 3767931946748426120607694620091415506089489910018762417221794878367942390719547853460426965095518994215158366732215845009690003537675755481

io = pwn.process("../deploy/chall.py", shell=True)

io.sendlineafter("Give me a prime number: ", str(n))

io.recvuntil("Have some ciphertexts:\n")

cts = []
for _ in range(32):
    ct = bytes.fromhex(io.recvlineS())
    print(ct)
    cts.append(ct)

# Take the most common bit at each position

bitss = [bytes_to_bits(ct) for ct in cts]
n = len(bitss[0])

bits_by_pos = [[bits[i] for bits in bitss] for i in range(n)]

bits = [mode(bits) for bits in bits_by_pos]
pt = bits_to_bytes(bits)
print(pt)

io.sendlineafter("Guess the plaintext:\n", pt)
io.interactive()
