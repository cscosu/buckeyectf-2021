from Crypto.Util.number import getPrime, inverse, bytes_to_long

e = 1440

while True:
    p = getPrime(1024)
    q = getPrime(1024)
    n = p * q
    phi = (p - 1) * (q - 1)
    if phi % 2 == 0 and phi % 5 == 0:
        break
    print(".", end="", flush=True)

print()

flag = b"buckeye{r0ots_0f_uN1Ty_w0rk_f0r_th1s???}"

c = pow(bytes_to_long(flag), e, n)
print(f"e = {e}")
print(f"p = {p}")
print(f"q = {q}")
print(f"c = {c}")
