import json, socket, threading, time
from urllib.parse import urlparse

FLAGS = {"boundary": "FLAG{boundary}", "cl-te": "FLAG{cl_te}", "te-cl": "FLAG{te_cl}", "cl-zero": "FLAG{cl_zero}", "h2-downgrade": "FLAG{h2_desync}"}
LOCK = threading.Lock()
STATE = {"cart": [], "solved": {}, "events": []}

def log(source, message, **values):
    item = {"time": time.strftime("%H:%M:%S"), "source": source, "message": message, **values}
    with LOCK:
        STATE["events"].append(item)
        STATE["events"] = STATE["events"][-100:]
    print(json.dumps(item), flush=True)

def parse(buffer):
    if b"\r\n\r\n" not in buffer: return None
    raw, remainder = buffer.split(b"\r\n\r\n", 1)
    lines = raw.split(b"\r\n")
    try: method, target, version = lines[0].decode("latin1").split(" ", 2)
    except ValueError: return None
    headers = {}
    for line in lines[1:]:
        if b":" in line:
            key, value = line.split(b":", 1); headers[key.decode().lower()] = value.strip().decode("latin1")
    return method, target, headers, remainder

def consume_te(headers, buffer):
    if "chunked" not in headers.get("transfer-encoding", "").lower():
        length = int(headers.get("content-length", "0") or 0)
        if len(buffer) < length: return None
        return buffer[:length], buffer[length:]
    body = b""
    while True:
        if b"\r\n" not in buffer: return None
        size_raw, buffer = buffer.split(b"\r\n", 1)
        try: size = int(size_raw.split(b";", 1)[0], 16)
        except ValueError: return None
        if len(buffer) < size + 2: return None
        body += buffer[:size]; buffer = buffer[size + 2:]
        if size == 0: return body, buffer

def reply(payload, status="200 OK"):
    body = json.dumps(payload).encode()
    return f"HTTP/1.1 {status}\r\nContent-Type: application/json\r\nAccess-Control-Allow-Origin: *\r\nContent-Length: {len(body)}\r\nConnection: keep-alive\r\nX-Backend-Parser: transfer-encoding\r\n\r\n".encode() + body

def route(target, armed, lesson, body):
    path = urlparse(target).path
    with LOCK: solved, cart, events = dict(STATE["solved"]), list(STATE["cart"]), list(STATE["events"])
    protected = {"/internal/boundary": "boundary", "/internal/fulfillment": "cl-te", "/internal/te-cl": "te-cl", "/internal/cl-zero": "cl-zero", "/internal/h2-downgrade": "h2-downgrade"}
    if path in protected:
        challenge = protected[path]
        if armed and (not lesson or lesson == challenge):
            with LOCK: STATE["solved"][challenge] = True
            log("CHALLENGE", "FLAG RELEASED", challenge=challenge, result="protected endpoint reached")
            return {"status": "authorized", "message": "Challenge completed", "flag": FLAGS[challenge], "challenge": challenge}, True
        log("BACKEND", "Protected endpoint denied", status=403)
        return {"error": "forbidden"}, False
    if path == "/api/state": return {"solved": solved, "cart": cart, "flags": {key: FLAGS[key] if solved.get(key) else None for key in FLAGS}}, armed
    if path == "/api/monitor": return {"events": events, "parser_agreement": "unknown"}, armed
    if path == "/api/cart/add":
        with LOCK: STATE["cart"].append("Mono Runner")
        log("BACKEND", "Cart updated", item="Mono Runner")
        return {"cart": STATE["cart"]}, armed
    if path == "/api/reset":
        with LOCK: STATE["cart"].clear(); STATE["solved"].clear(); STATE["events"].clear()
        log("BACKEND", "Challenge reset")
        return {"reset": True}, False
    return {"service": "Desync Commerce API", "path": path}, armed

def connection(sock, address):
    buffer = b""; armed = False; lesson = ""; sock.settimeout(10)
    log("BACKEND", "Connection opened", peer=str(address), parser="Transfer-Encoding")
    try:
        while True:
            while b"\r\n\r\n" not in buffer:
                part = sock.recv(8192)
                if not part: return
                buffer += part
            parsed = parse(buffer)
            if not parsed: return
            method, target, headers, remainder = parsed
            result = consume_te(headers, remainder)
            if result is None:
                buffer += sock.recv(8192); continue
            body, buffer = result
            both = bool(headers.get("content-length")) and bool(headers.get("transfer-encoding"))
            log("BACKEND", "Request boundary calculated", method=method, target=target, parser="Transfer-Encoding", content_length=headers.get("content-length"), transfer_encoding=headers.get("transfer-encoding"), body_bytes=len(body), leftover_bytes=len(buffer))
            if both and not target.startswith("/internal/"):
                armed = True
                lesson = headers.get("x-lab-lesson", "")
                log("DESYNC", "Request boundary mismatch detected", connection_state="DESYNCHRONIZED")
            if headers.get("content-length") == "0" and not headers.get("transfer-encoding") and not target.startswith("/internal/"):
                armed = True; lesson = headers.get("x-lab-lesson", "")
                log("DESYNC", "CL.0 boundary condition observed", connection_state="DESYNCHRONIZED")
            if headers.get("x-lab-protocol") == "h2-downgrade":
                armed = True; lesson = "h2-downgrade"
                log("DESYNC", "HTTP/2 to HTTP/1.1 downgrade condition observed", connection_state="DESYNCHRONIZED")
            payload, _ = route(target, armed, lesson, body)
            if target.startswith("/internal/") and armed:
                log("DESYNC", "Backend processed secondary request", target=target)
            sock.sendall(reply(payload, "200 OK" if payload.get("status") == "authorized" or target != "/internal/fulfillment" else "403 Forbidden"))
            # Some clients display only the first pipelined response. Surface the
            # queued lab request explicitly when it is already in this buffer.
            if both and buffer:
                secondary = next((path for path in ("/internal/boundary", "/internal/fulfillment", "/internal/te-cl", "/internal/cl-zero", "/internal/h2-downgrade") if ("GET " + path).encode() in buffer), None)
                if secondary:
                    secondary_payload, _ = route(secondary, armed, lesson, b"")
                    log("DESYNC", "Backend processed secondary request", target=secondary)
                    sock.sendall(reply(secondary_payload, "200 OK" if secondary_payload.get("status") == "authorized" else "403 Forbidden"))
                    buffer = b""
    except (OSError, socket.timeout): pass
    finally: sock.close()

def main():
    log("BACKEND", "Backend ready", parser="Transfer-Encoding", listen="9000")
    server = socket.socket(); server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1); server.bind(("0.0.0.0", 9000)); server.listen(50)
    while True:
        sock, address = server.accept(); threading.Thread(target=connection, args=(sock, address), daemon=True).start()

if __name__ == "__main__": main()
