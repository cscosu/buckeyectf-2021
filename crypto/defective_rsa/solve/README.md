# Defective RSA

I use whatever exponent I want

Attachments: `chall.py`

**Category**: crypto \
**Points**: ? \
**Solves**: ? \
**Author**: qxxxb

## Overview

We're given this:

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
```

This is a typical RSA encryption except except:
- We're given `p` and `q`
- `e` and `phi(n)` are not co-prime, so we don't have a unique decryption.

## Solution

Instead find all x satisfying:

```
(m * x) ^ e === c  (mod n)
      x ^ e === 1  (mod n)
```

Actually `x` is called a
[root of unity modulo `n`](https://en.wikipedia.org/wiki/Root_of_unity_modulo_n)
which can be computed fairly easily.

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

### Note

This challenge is based on Broken RSA from CryptoHack, but the intended
solution is different.
