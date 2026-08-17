# Desync Commerce

> A local, Dockerized HTTP Request Smuggling mini-CTF built around a realistic ecommerce experience.

Desync Commerce presents a normal premium storefront backed by an intentionally mismatched HTTP/1.1 proxy and backend. The five-lesson series teaches request boundaries, persistent connections, `Content-Length`, `Transfer-Encoding`, desynchronization, telemetry, and remediation.

Everything runs on localhost. There are no real accounts, credentials, external targets, scanners, or destructive actions.

## What You Build

```text
Browser / Burp Suite
        |
        v
Next.js storefront :3000
        |
        v
Teaching proxy :8080  ------>  Private backend :9000
        |
        +-- Patched proxy :8081
```

The vulnerable teaching proxy forwards persistent HTTP/1.1 connections while the backend consumes `Transfer-Encoding: chunked`. The front-end security decision and backend request boundary can therefore disagree. The patched proxy rejects ambiguous framing before forwarding it.

## Highlights

- Production-inspired ecommerce storefront called **Desync Commerce**
- Next.js, TypeScript, Tailwind CSS, and local product artwork
- Separate frontend proxy and private backend containers
- Burp Suite Repeater-compatible local target
- Five progressive HTTP desynchronization challenges
- Per-challenge progress, flags, hints, and reset controls
- Live backend parser telemetry and connection state
- Vulnerable versus patched proxy comparison
- Backend-only flag release after the intended condition
- No flag values in frontend source, HTML, or client bundle
- Separate author solution in `SOLUTION.md`

## Challenge Series

Open:

```text
http://localhost:3000/challenge
```

| # | Lesson | Focus |
|---|---|---|
| 01 | Find the Boundary | Request boundary calculation |
| 02 | CL.TE | Frontend length versus backend transfer coding |
| 03 | TE.CL | Reverse framing disagreement |
| 04 | CL.0 | Zero-length body on a reused connection |
| 05 | HTTP/2 Downgrade | Controlled HTTP/2-to-HTTP/1.1 translation model |

Each lesson releases its flag only after the matching backend challenge condition succeeds.

## Requirements

- Docker Engine
- Docker Compose
- Burp Suite Community or Professional, optional
- Python 3.10+, optional for local replay helpers

## Start the Lab

From the repository root:

```bash
docker compose up --build
```

Open the storefront:

```text
http://localhost:3000
```

Open the CTF page:

```text
http://localhost:3000/challenge
```

Check service status:

```bash
docker compose ps
```

## Burp Suite Workflow

The lab proxy owns port `8080`. Do not start Burp's own listener on `8080`.

1. Open Burp Suite and go to **Repeater**.
2. Set the Repeater target to `http://localhost:8080`.
3. Use HTTP/1.1.
4. Disable automatic `Content-Length` updates.
5. Start with the normal protected-route request shown on `/challenge`.
6. Work through the progressive hints.
7. Refresh `/challenge` after each successful lesson.

If you use Burp's browser proxy listener, put that listener on another free port such as `127.0.0.1:8082`. The application UI remains on `localhost:3000`; the controlled request target is `localhost:8080`.

## Local Replay Helpers

These helpers are restricted to `127.0.0.1:8080` and are provided for repeatable lab verification:

```bash
python3 labs/series.py --challenge boundary
python3 labs/series.py --challenge cl-te
python3 labs/series.py --challenge te-cl
python3 labs/series.py --challenge cl-zero
python3 labs/series.py --challenge h2-downgrade
```

They are optional. The intended learning workflow is to inspect and reproduce the behavior with Burp Suite.

## Monitoring

The challenge page includes a local HTTP desync monitor. For raw backend telemetry:

```bash
docker compose logs -f backend
```

Useful events include:

```text
Request boundary calculated
Request boundary mismatch detected
Backend processed secondary request
FLAG RELEASED
```

The monitor is designed to show the frontend/backend interpretation difference without displaying the solution payload in the public storefront.

## Patched Mode

Compare the vulnerable proxy with:

```text
http://localhost:8081
```

The patched proxy rejects conflicting `Content-Length` and `Transfer-Encoding` framing with `400 Bad Request`. This demonstrates the intended defensive rule:

```text
Vulnerable: frontend parser != backend parser -> desync possible
Patched:    ambiguous framing rejected        -> no backend forwarding
```

## Reset

Use **Reset series** on the challenge page, or run:

```bash
curl http://localhost:8080/api/reset
```

Restart everything from scratch:

```bash
docker compose down
docker compose up --build
```

## Project Layout

```text
.
├── backend/
│   ├── Dockerfile
│   └── server.py
├── frontend/
│   ├── app/
│   ├── public/products/
│   ├── Dockerfile
│   └── package.json
├── proxy/
│   ├── Dockerfile
│   └── proxy.py
├── labs/
│   └── series.py
├── docs/
│   └── architecture.md
├── docker-compose.yml
├── README.md
└── SOLUTION.md
```

## Learning Objectives

- Understand HTTP/1.1 persistent connection reuse
- Compare `Content-Length` and `Transfer-Encoding`
- Reason about request boundaries at the byte level
- Observe frontend authorization checks versus backend interpretation
- Reproduce CL.TE-style desynchronization locally
- Understand CL.0 and downgrade translation risks
- Use telemetry to explain parser disagreement
- Apply framing normalization and rejection as remediation

## Safety Boundary

This repository contains intentionally vulnerable teaching code. Use it only on your own machine or an isolated Docker network. Never point the replay helpers or Burp requests at public websites or systems you do not own.

The project deliberately excludes SQL injection, XSS, SSRF, command injection, path traversal, IDOR, insecure JWTs, real authentication data, credential capture, and arbitrary-target proxying.

## Author Notes

The intended solution, parser reasoning, and remediation details are in `SOLUTION.md`. Keep that file private when using this repository as a player-facing CTF.

## Credits

Created as an educational HTTP security lab and mini-CTF series. The project is designed for demonstrations, Burp Suite practice, and security learning in a controlled local environment.
