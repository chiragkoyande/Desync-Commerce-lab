import os, socket, threading

MODE = os.getenv("PROXY_MODE", "vulnerable")
BACKEND = ("backend", 9000)

def response(status, body):
    return f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode() + body

def details(raw):
    head = raw.split(b"\r\n\r\n", 1)[0].split(b"\r\n")
    try: method, target, version = head[0].decode("latin1").split(" ", 2)
    except ValueError: return "", "", {}
    headers = {}
    for line in head[1:]:
        if b":" in line:
            key, value = line.split(b":", 1); headers[key.decode().lower()] = value.strip().decode("latin1")
    return method, target, headers

def collect(sock):
    # Burp can deliver the headers and queued request bytes in separate packets.
    sock.settimeout(1.25); data = b""
    try:
        while len(data) < 65536:
            part = sock.recv(8192)
            if not part: break
            data += part
    except socket.timeout: pass
    return data

def serve(sock):
    try:
        raw = collect(sock); method, target, headers = details(raw)
        if target.startswith("/internal/"):
            sock.sendall(response("403 Forbidden", b'{"error":"frontend blocked protected path"}')); return
        if MODE == "fixed" and headers.get("content-length") and headers.get("transfer-encoding"):
            sock.sendall(response("400 Bad Request", b'{"error":"ambiguous framing rejected by patched proxy"}')); return
        upstream = socket.create_connection(BACKEND, 3); upstream.settimeout(5); upstream.sendall(raw); upstream.shutdown(socket.SHUT_WR)
        while True:
            part = upstream.recv(8192)
            if not part: break
            sock.sendall(part)
    except (OSError, socket.timeout): pass
    finally: sock.close()

def main():
    print(f"frontend proxy ready mode={MODE}", flush=True)
    server = socket.socket(); server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); server.bind(("0.0.0.0", 80)); server.listen(50)
    while True:
        sock, address = server.accept(); threading.Thread(target=serve, args=(sock,), daemon=True).start()

if __name__ == "__main__": main()
