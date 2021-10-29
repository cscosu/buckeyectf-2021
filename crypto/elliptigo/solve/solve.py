from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from Crypto.Util.number import size, long_to_bytes
import os
import hashlib
from collections import namedtuple
import pwn

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
    # Pick a generator P
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

    if pwn.args.REMOTE:
        io = pwn.remote("localhost", 1024)
    else:
        io = pwn.process("python3 ../src/chall.py", shell=True)

    io.sendlineafter("x: ", str(xs[-1]))

    ct = bytes.fromhex(io.recvlineS().strip())
    for shared_secret in shared_secrets:
        cipher = AES.new(shared_secret, AES.MODE_ECB)
        print(cipher.decrypt(ct))


if __name__ == "__main__":
    main()
