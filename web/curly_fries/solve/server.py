import socket
from socketserver import ThreadingTCPServer, StreamRequestHandler
import time
from email.utils import formatdate
from pathlib import Path
import re
import os

port = 3000


def client_str(req):
    ip = req.client_address[0]
    port = req.client_address[1]
    return f"{ip}:{port}"


class MyTCPServer(ThreadingTCPServer):
    def server_bind(self):
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 10)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
        self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
        self.socket.bind(self.server_address)


header_template = """HTTP/1.1 200 OK\r
Date: {date}\r
Content-Length: {fake_content_length}\r
CoNtEnT-LeNgTh: {real_content_length}\r
Content-Type: text/html; charset="utf-8"\r
\r
"""


class TcpHandler(StreamRequestHandler):
    def on_disconnect(self):
        print(f"[*] Disconnected {client_str(self)}")

    def handle(self):
        try:
            while True:
                line = self.rfile.readline().strip().decode()
                if len(line) == 0:
                    self.on_disconnect()
                    return

                print(f"[*] {line} {client_str(self)}")

                # Discard the rest of the request
                while len(self.rfile.readline().strip()) != 0:
                    pass

                date = formatdate(timeval=None, localtime=False, usegmt=True)

                header = header_template.format(
                    date=date, fake_content_length=1023, real_content_length=16
                )

                self.wfile.write(header.encode())
                self.wfile.write(b"A" * 16)

        except ConnectionError as e:
            print(f"[-] {e} {client_str(self)}")
            self.on_disconnect()
            return


if __name__ == "__main__":
    tcp = MyTCPServer(("0.0.0.0", port), TcpHandler)
    print(f"[*] Listening on port {port} ...")
    tcp.serve_forever()
