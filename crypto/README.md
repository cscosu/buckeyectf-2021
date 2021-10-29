# BuckeyeCTF 2021 crypto write-ups

Version with LaTeX rendered: https://hackmd.io/@65XZ9ZfDTb21FI-0un6Zhg/BJj1FqYUK

These are write-ups for the crypto challenges I wrote for BuckeyeCTF 2021. Source code and solve scripts can be found here: https://github.com/cscosu/buckeyectf-2021/tree/master/crypto

## Key exchange

**Stats**: 141 solves / 40 points / easy

Let's exchange the flag (securely):

```
nc crypto.chall.pwnoh.io 13374
```

```python
import random
import hashlib

# Mac/Linux: pip3 install pycryptodome
# Windows: py -m pip install pycryptodome
import Crypto.Util.number as cun
from Crypto.Cipher import AES

rand = random.SystemRandom()
FLAG = b"buckeye{???????????????????????????????????????????????????????}"


def diffie_hellman(message: bytes):
    p = cun.getPrime(512)
    g = 5
    print(f"p = {p}")
    print(f"g = {g}")

    a = rand.randrange(2, p - 1)  # private key
    A = pow(g, a, p)  # public key

    # g ^ a === A  (mod p)
    # It's computationally infeasible for anyone else to derive a from A
    print(f"A = {A}")

    B = int(input("Give me your public key B: "))
    if not (1 < B < p - 1):
        print("Suspicious public key")
        return

    # B ^ a === (g ^ b) ^ a === g ^ (ab)  (mod p)
    # Nobody can derive this shared secret except us!
    shared_secret = pow(B, a, p)

    # Use AES, a symmetric cipher, to encrypt the flag using the shared key
    key = hashlib.sha1(cun.long_to_bytes(shared_secret)).digest()[:16]
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(message)
    print(f"ciphertext = {ciphertext.hex()}")


print("I'm going to send you the flag.")
print("However, I noticed that an FBI agent has been eavesdropping on my messages,")
print("so I'm going to send it to you in a way that ONLY YOU can decrypt the flag.")
print()
diffie_hellman(FLAG)
```

### Solution

This is Diffie-Hellman key exchange: the server plays the role of Alice, and you play the role of Bob.

To calculate the shared key, pick a random $b$ then send $g^b \pmod{p}$. Then the shared key is $A^b \equiv B^a \equiv g^{ab} \pmod{p}$.

```python
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
```

## Key exchange 2

**Stats**: 34 solves / 90 points / easy

No public key this time!

```
nc crypto.chall.pwnoh.io 13386
```

### Solution

This is the same as the first Key exchange challenge, but no public key $A$ is given. The solution is the perform a small subgroup attack:

- Find any small prime factor $k$ of $p - 1$ (besides 2)
- Set $B \equiv g^k \pmod{p}$. Then the order of $B$ is at most $k$.
- The server calculates the shared key as $B^a \pmod{p}$. That means the shared key must one of $B, B^2, B^3, \ldots, B^k$. Just try all of them:

```python
for i in range(3, 1024):
    if (p - 1) % i == 0:
        break
else:
    io.close()
    return False

print(i)
b = (p - 1) // i
B = pow(g, b, p)
```

## Elliptigo

**Stats**: 21 solves / 465 points / medium

I heard everyone uses Curve25519 these days. I'm sure it's super secure, so I'll even let you pick a base point!

```
nc crypto.chall.pwnoh.io 13373
```

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import size, long_to_bytes
import os
import hashlib
from collections import namedtuple

FLAG = b"buckeye{???????????????????}"

Point = namedtuple("Point", ("x", "z"))
Curve = namedtuple("Curve", ("a", "b"))

p = 2 ** 255 - 19
C = Curve(486662, 1)

"""
Implements the Montgomery Ladder from https://eprint.iacr.org/2017/212.pdf
"""


def point_add(P: Point, Q: Point, D: Point) -> Point:
    """
    Algorithm 1 (xADD)
    """
    V0 = (P.x + P.z) % p
    V1 = (Q.x - Q.z) % p
    V1 = (V1 * V0) % p
    V0 = (P.x - P.z) % p
    V2 = (Q.x + Q.z) % p
    V2 = (V2 * V0) % p
    V3 = (V1 + V2) % p
    V3 = (V3 * V3) % p
    V4 = (V1 - V2) % p
    V4 = (V4 * V4) % p
    x = (D.z * V3) % p
    z = (D.x * V4) % p
    return Point(x, z)


def point_double(P: Point) -> Point:
    """
    Algorithm 2 (xDBL)
    """
    V1 = (P.x + P.z) % p
    V1 = (V1 * V1) % p
    V2 = (P.x - P.z) % p
    V2 = (V2 * V2) % p
    x = (V1 * V2) % p
    V1 = (V1 - V2) % p
    V3 = (((C.a + 2) // 4) * V1) % p
    V3 = (V3 + V2) % p
    z = (V1 * V3) % p
    return Point(x, z)


def scalar_multiplication(P: Point, k: int) -> Point:
    """
    Algorithm 4 (LADDER)
    """

    if k == 0:
        return Point(0, 0)

    R0, R1 = P, point_double(P)
    for i in range(size(k) - 2, -1, -1):
        if k & (1 << i) == 0:
            R0, R1 = point_double(R0), point_add(R0, R1, P)
        else:
            R0, R1 = point_add(R0, R1, P), point_double(R1)
    return R0


def normalize(P: Point) -> Point:
    if P.z == 0:
        return Point(0, 0)

    return Point((P.x * pow(P.z, -1, p)) % p, 1)


def legendre_symbol(x: int, p: int) -> int:
    return pow(x, (p - 1) // 2, p)


def is_on_curve(x: int) -> bool:
    y2 = x ** 3 + C.a * x ** 2 + C.b * x
    return legendre_symbol(y2, p) != (-1 % p)


def main():
    print("Pick a base point")
    x = int(input("x: "))

    if size(x) < 245:
        print("Too small!")
        return

    if x >= p:
        print("Too big!")
        return

    if not is_on_curve(x):
        print("That x coordinate is not on the curve!")
        return

    P = Point(x, 1)

    a = int.from_bytes(os.urandom(32), "big")
    A = scalar_multiplication(P, a)
    A = normalize(A)

    key = hashlib.sha1(long_to_bytes(A.x)).digest()[:16]

    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(FLAG, 16))
    print(ciphertext.hex())


if __name__ == "__main__":
    main()
```

### Solution

This is the same setup as Key exchange 2, except now the group is Curve25519. The solution is to do a small subgroup attack:

```python
# Pick a generator G
G = Point(6, 1)
subgroup_order = (2 ** 252 + 27742317777372353535851937790883648493)
order = 8 * subgroup_order
assert normalize(scalar_multiplication(G, 2)) != Point(0, 0)
assert normalize(scalar_multiplication(G, 4)) != Point(0, 0)
assert normalize(scalar_multiplication(G, 8)) != Point(0, 0)
assert normalize(scalar_multiplication(G, subgroup_order)) != Point(0, 0)
assert normalize(scalar_multiplication(G, order)) == Point(0, 0)

B = normalize(scalar_multiplication(G, order // 8))
assert normalize(scalar_multiplication(B, 8)) == Point(0, 0)

subgroup = [normalize(scalar_multiplication(B, i)) for i in range(1, 8 + 1)]
xs = sorted([B.x for B in subgroup])
shared_secrets = [hashlib.sha1(long_to_bytes(x)).digest()[:16] for x in xs]

io = pwn.process("python3 ../src/chall.py", shell=True)
io.sendlineafter("x: ", str(xs[-1]))

ct = bytes.fromhex(io.recvlineS().strip())
for shared_secret in shared_secrets:
    cipher = AES.new(shared_secret, AES.MODE_ECB)
    print(cipher.decrypt(ct))
```

## Defective RSA

**Stats**: 33 solves / 441 points / hard

I use whatever exponent I want

```python
from Crypto.Util.number import getPrime, inverse, bytes_to_long

e = 1440

p = getPrime(1024)
q = getPrime(1024)
n = p * q

flag = b"buckeye{???????????????????????????????}"
c = pow(bytes_to_long(flag), e, n)

print(f"e = {e}")
print(f"p = {p}")
print(f"q = {q}")
print(f"c = {c}")

# e = 1440
# p = 108625855303776649594296217762606721187040584561417095690198042179830062402629658962879350820293908057921799564638749647771368411506723288839177992685299661714871016652680397728777113391224594324895682408827010145323030026082761062500181476560183634668138131801648343275565223565977246710777427583719180083291
# q = 124798714298572197477112002336936373035171283115049515725599555617056486296944840825233421484520319540831045007911288562132502591989600480131168074514155585416785836380683166987568696042676261271645077182221098718286132972014887153999243085898461063988679608552066508889401992413931814407841256822078696283307
# c = 4293606144359418817736495518573956045055950439046955515371898146152322502185230451389572608386931924257325505819171116011649046442643872945953560994241654388422410626170474919026755694736722826526735721078136605822710062385234124626978157043892554030381907741335072033672799019807449664770833149118405216955508166023135740085638364296590030244412603570120626455502803633568769117033633691251863952272305904666711949672819104143350385792786745943339525077987002410804383449669449479498326161988207955152893663022347871373738691699497135077946326510254675142300512375907387958624047470418647049735737979399600182827754
```

This is a typical RSA encryption except except:
- We're given $p$ and $q$
- $e$ and $\phi\left(n\right)$ are not co-prime, so we don't have a unique decryption.

### Solution

Instead find all x satisfying:

\begin{align}
(m \cdot x)^e &\equiv c \pmod{n} \\
x^e &\equiv 1 \pmod{n}
\end{align}

Actually $x$ is called a [root of unity modulo $n$](https://en.wikipedia.org/wiki/Root_of_unity_modulo_n) which can be computed fairly easily.

Final script:

```python
import Crypto.Util.number as cun
from pprint import pprint


def roots_of_unity(e, phi, n, rounds=500):
    # Divide common factors of `phi` and `e` until they're coprime.
    phi_coprime = phi
    while cun.GCD(phi_coprime, e) != 1:
        phi_coprime //= cun.GCD(phi_coprime, e)

    # Don't know how many roots of unity there are, so just try and collect a bunch
    roots = set(pow(i, phi_coprime, n) for i in range(1, rounds))

    assert all(pow(root, e, n) == 1 for root in roots)
    return roots, phi_coprime


e = 1440
p = 108625855303776649594296217762606721187040584561417095690198042179830062402629658962879350820293908057921799564638749647771368411506723288839177992685299661714871016652680397728777113391224594324895682408827010145323030026082761062500181476560183634668138131801648343275565223565977246710777427583719180083291
q = 124798714298572197477112002336936373035171283115049515725599555617056486296944840825233421484520319540831045007911288562132502591989600480131168074514155585416785836380683166987568696042676261271645077182221098718286132972014887153999243085898461063988679608552066508889401992413931814407841256822078696283307
c = 4293606144359418817736495518573956045055950439046955515371898146152322502185230451389572608386931924257325505819171116011649046442643872945953560994241654388422410626170474919026755694736722826526735721078136605822710062385234124626978157043892554030381907741335072033672799019807449664770833149118405216955508166023135740085638364296590030244412603570120626455502803633568769117033633691251863952272305904666711949672819104143350385792786745943339525077987002410804383449669449479498326161988207955152893663022347871373738691699497135077946326510254675142300512375907387958624047470418647049735737979399600182827754

n = p * q

# Problem: e and phi are not coprime - d does not exist
phi = (p - 1) * (q - 1)

# Find e'th roots of unity modulo n
roots, phi_coprime = roots_of_unity(e, phi, n)

# Use our `phi_coprime` to get one possible plaintext
d = pow(e, -1, phi_coprime)
m = pow(c, d, n)
assert pow(m, e, n) == c

# Use the roots of unity to get all other possible plaintexts
ms = [(m * root) % n for root in roots]
ms = [cun.long_to_bytes(m) for m in ms]
pprint(ms)

for m in ms:
    if m.startswith(b"buckeye"):
        print(f"Flag: {m}")
        break
else:
    print("No flag found :(")
```

If you know a better way to implement `roots_of_unity()`, let me know. I implemented an algorithm from Wikipedia but it doesn't seem very clean.

### Note

This challenge is based on Broken RSA from CryptoHack, but the intended solution is different. Unfortunately, almost nobody did the intended solution and instead did something similar to [Y-CTF's solution](https://github.com/Y-CTF/writeups/blob/main/BuckeyeCTF/crypto/Defective-RSA/defective-RSA.md):

```python
from Crypto.Util.number import long_to_bytes

e = 1440
p = 108625855303776649594296217762606721187040584561417095690198042179830062402629658962879350820293908057921799564638749647771368411506723288839177992685299661714871016652680397728777113391224594324895682408827010145323030026082761062500181476560183634668138131801648343275565223565977246710777427583719180083291
q = 124798714298572197477112002336936373035171283115049515725599555617056486296944840825233421484520319540831045007911288562132502591989600480131168074514155585416785836380683166987568696042676261271645077182221098718286132972014887153999243085898461063988679608552066508889401992413931814407841256822078696283307
c = 4293606144359418817736495518573956045055950439046955515371898146152322502185230451389572608386931924257325505819171116011649046442643872945953560994241654388422410626170474919026755694736722826526735721078136605822710062385234124626978157043892554030381907741335072033672799019807449664770833149118405216955508166023135740085638364296590030244412603570120626455502803633568769117033633691251863952272305904666711949672819104143350385792786745943339525077987002410804383449669449479498326161988207955152893663022347871373738691699497135077946326510254675142300512375907387958624047470418647049735737979399600182827754

rmodp = (c % p).nth_root(e, all=True)
rq = (c % q).nth_root(e)

for rp in rmodp:
    r = crt(int(rp), int(rq), p, q)
    flag = long_to_bytes(r)

    if b"buckeye" in flag:
        print(flag.decode())
```

I'm not sure how to prevent these kind of solutions, but I at least should've made the flag much longer (more than 2048 bytes) so that people would actually need to enumerate all possible plaintexts.

## Pseudo

**Stats**: 15 solves / 476 points / hard

Surely the Legendre symbol is a great random number generator, right?

```
nc crypto.chall.pwnoh.io 13375
```

```python
#!/usr/bin/env python3
import random
import os

rand = random.SystemRandom()
FLAG = b"buckeye{?????????????????????}"


def is_prime(n, rounds=32):
    return all(pow(rand.randrange(2, n), n - 1, n) == 1 for _ in range(rounds))


class RNG:
    def __init__(self, p: int, a: int):
        self.p = p
        self.a = a

    def next_bit(self) -> int:
        ans = pow(self.a, (self.p - 1) // 2, self.p)
        self.a += 1
        return int(ans == 1)

    def next_byte(self) -> int:
        ans = 0
        for i in range(8):
            ans |= self.next_bit() << i
        return ans

    def next_bytes(self, n: int) -> bytes:
        return bytes(self.next_byte() for _ in range(n))


def main():
    p = int(input("Give me a prime number: "))

    if not (256 <= p.bit_length() <= 512):
        print("Wrong bit length")
        return

    if not is_prime(p):
        print("Fermat tells me your number isn't prime")
        return

    a = rand.randrange(2, p)
    rng = RNG(p, a)

    plaintext = b"Hello " + os.urandom(48).hex().encode()
    print("Have some ciphertexts:")

    for _ in range(32):
        s = rng.next_bytes(len(plaintext))
        c = bytes(a ^ b for a, b in zip(s, plaintext))
        print(c.hex())

    if plaintext == input("Guess the plaintext:\n").encode():
        print(f"Congrats! Here's the flag: {FLAG}")
    else:
        print("That's wrong")


main()
```

In short:
- You input a number
- The server uses the [Fermat primality test](https://en.wikipedia.org/wiki/Fermat_primality_test) to check your number
- It uses the [Legendre PRF](https://legendreprf.org/) to encrypt the flag
  - Basically it picks a random number $a$ and generates a stream of pseudo-random bits by calculating the Legendre symbol of $a, a + 1, a + 2, \ldots$

### Solution

When I wrote this problem, my first idea was just to use a Carmichael number in order to  pass the Fermat primality test.

```python
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
```

This passed the Fermat primality test, but it seemed to produce 50% ones and zeros from the RNG.

I wasn't sure why this was the case, but next I tried [strong pseudoprimes](https://core.ac.uk/download/pdf/81930829.pdf). Specifically, I chose $n = 13618186946913248902029336585225618237728639469119284611739065110030838492720163$ from Lemma 4.2 of the linked paper.

Somehow, this made the RNG produce 97% zero bits in its output, which was more than enough to get the flag. It still isn't clear to me why some Carmichael numbers produce more biased outputs than others, but it seems like an interesting problem.

- Some people like randomdude999, Polymero, and Waffles generated Carmichael numbers similar to the snippet of code above–but for some reason their numbers gave them biased PRNGs, which got them the flag.
- Shadowwws managed to find a Carmichael number 12222215858006916517610684499755896040093289077713340217662837890484212251483748795117784089 that produced only 1 bits.

## Super VDF

**Stats**: 15 solves / 476 points / medium

You'll need a supercomputer to pass my VDF

```
nc crypto.chall.pwnoh.io 13376
```

```python
from gmpy2 import is_prime, mpz
from random import SystemRandom

rand = SystemRandom()
PRIMES = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53]


def get_prime(bit_length):
    while True:
        x = mpz(1)
        while x.bit_length() < bit_length:
            x *= rand.choice(PRIMES)
        if is_prime(x + 1):
            return x + 1


def get_correct_answer():
    # Implementation redacted
    return -1


p = get_prime(1024)
q = get_prime(1024)
n = p * q

print(f"n = {n}")
print("Please calculate (59 ** 59 ** 59 ** 59 ** 1333337) % n")
ans = int(input(">>> "))

if ans == get_correct_answer():
    print("WTF do you own a supercomputer? Here's your flag:")
    print("buckeye{????????????????????????????????????}")
else:
    print("WRONG")
```

### Solution

VDF stands for Verifiable Delay Function: there's an existing VDF where you have to calculate $2^{2^{e}} \pmod{n}$ where $n$ is an RSA modulus, so this is kind of similar.

The solution here is to first factor $n$ with [Pollard's p - 1 algorithm](https://en.wikipedia.org/wiki/Pollard%27s_p_%E2%88%92_1_algorithm). Then you can calculate $\phi \left(n\right), \phi \left(\phi \left(n\right)\right), \phi \left(\phi \left(\phi \left(n\right)\right)\right)$ and so on. This is feasible because each result of $\phi$ is a smooth number.

To solve the challenge, notice that $59^{59^{e}} \equiv 59^{59^{e} \pmod{\phi\left(n \right)}} \pmod{n}$. Do this a few more times to get the answer:
```python
e = 1333337
phi = (p - 1) * (q - 1)
phi1 = euler_phi(phi)
phi2 = euler_phi(phi1)
a = pow(59, e, phi2)
b = pow(59, a, phi1)
c = pow(59, b, phi)
ans = pow(59, c, n)
```

### Note

I also saw some creative solutions from randomdude999 and Yehonatan which did not require factoring $n$.
