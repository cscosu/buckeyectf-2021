import random

pt = b"buckeye{h0ly_sh1t_wh4t_th3_h3ck_1s_th1s_w31rd_ch4ll3ng3}"
key = 0x99

pairs = list(zip(pt, range(len(pt))))
random.shuffle(pairs)

pt_scrambled = [p[0] for p in pairs]

styles = []
for i, p in enumerate(pairs):
    s = f".flag-char-{i} {{ order: {p[1]} }}"
    styles.append(s)
print("\n".join(styles))

ct = []
for i, b in enumerate(pt_scrambled):
    ct.append(((i * i) % 256) ^ b ^ key)
print(ct)
