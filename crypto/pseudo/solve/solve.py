import pwn
import Crypto.Util.number as cun
import random
import gmpy2
from functools import reduce
from itertools import chain
from operator import mul
import Crypto.Util.number as cun
from statistics import mode
import subprocess

rand = random.SystemRandom()


def get_primes(p0, ks):
    if not cun.isPrime(p0):
        return None

    ps = [k * (p0 - 1) + 1 for k in ks]
    if all(cun.isPrime(p) for p in ps):
        return ps
    else:
        return None


def byte_to_bits(s: int):
    return [int(x) for x in bin(s)[2:].zfill(8)]


def bytes_to_bits(s: bytes):
    return list(chain(*[byte_to_bits(b) for b in s]))


def bits_to_bytes(s):
    return cun.long_to_bytes(int("".join(str(x) for x in s), 2))


# https://core.ac.uk/download/pdf/81930829.pdf
# Lemma 4.2
p0 = 343367327175643
ks = [1, 13, 41, 53, 101]
ps = get_primes(p0, ks)
n = reduce(mul, ps)  # type: ignore
print(n)

if pwn.args.REMOTE:
    io = pwn.remote("localhost", 1024)
else:
    io = pwn.process("../deploy/chall.py", shell=True)

cmd = io.recvlineS().strip().split("of: ")[-1]
print(cmd)
output = subprocess.check_output(cmd, shell=True)
io.sendline(output)
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
