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

    phi = (p - 1) * (q - 1)
    phi1 = euler_phi(phi)
    phi2 = euler_phi(phi1)
    e = 1333337
    a = pow(59, e, phi2)
    b = pow(59, a, phi1)
    c = pow(59, b, phi)
    d = pow(59, c, n)
    return d


p = get_prime(1024)
q = get_prime(1024)
n = p * q

print(f"n = {n}")
print("Please calculate (59 ** 59 ** 59 ** 59 ** 1333337) % n")
ans = int(input(">>> "))

if ans == get_correct_answer():
    print("WTF do you own a supercomputer? Here's your flag:")
    print("buckeye{phee_phi_pho_phum_v3ry_stup1d_puzzle}")
else:
    print("WRONG")
