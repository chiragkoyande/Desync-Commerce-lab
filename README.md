# Desync Commerce

Desync Commerce is a beginner-friendly, local HTTP Request Smuggling mini-CTF. It looks like an ecommerce website, but its frontend proxy and backend intentionally disagree about HTTP/1.1 request boundaries.

The project is designed for learning with Docker and Burp Suite. It does not contact external systems and does not contain real accounts, credentials, or sensitive data.

## What You Will Learn

- How a browser, proxy, and backend communicate
- HTTP/1.1 persistent connections
- `Content-Length`
- `Transfer-Encoding: chunked`
- Request boundary disagreement
- CL.TE and TE.CL concepts
- CL.0 behavior
- HTTP/2 downgrade concepts
- Backend telemetry
- Basic remediation

## Architecture

```text
Browser / Burp Suite
        |
        v
Next.js ecommerce website :3000
        |
        v
Vulnerable teaching proxy :8080
        |
        v
Private backend API :9000

Patched teaching proxy :8081
```

The backend port is private to Docker. Burp sends challenge traffic to the vulnerable proxy on port `8080`.

## Project Requirements

Install these before starting:

- Docker Desktop or Docker Engine
- Docker Compose
- Burp Suite Community or Professional, optional
- Python 3.10+, optional for local replay helpers

Check Docker installation:

```bash
docker --version
docker compose version
```

If both commands print version information, Docker is ready.

## Download the Project

```bash
git clone https://github.com/chiragkoyande/Desync-Commerce-lab.git
cd Desync-Commerce-lab
```

If you already have the project, only run:

```bash
cd "/home/chiragk/cyber projects/DesyncLab"
```

## First Startup

Build and start every container:

```bash
docker compose up --build
```

The first build may take a few minutes because the Next.js dependencies are installed inside Docker.

Keep this terminal open. Open a second terminal for other commands.

Check that everything is running:

```bash
docker compose ps
```

You should see four services:

```text
backend
frontend
frontend-proxy
patched-proxy
```

## Open the Website

Normal ecommerce storefront:

```text
http://localhost:3000
```

CTF challenge page:

```text
http://localhost:3000/challenge
```

The storefront is intentionally designed to look like a normal commerce website. The security training content is on `/challenge`.

## Ports

| Port | Purpose |
|---|---|
| `3000` | Next.js storefront and challenge page |
| `8080` | Vulnerable teaching proxy and Burp target |
| `8081` | Patched teaching proxy |
| `9000` | Backend inside Docker; not published to the host |

## Challenge Series

Open `http://localhost:3000/challenge` and complete the five lessons in order:

```text
01 — Find the Boundary
02 — CL.TE
03 — TE.CL
04 — CL.0
05 — HTTP/2 Downgrade
```

Each lesson has:

- A short explanation
- Progressive hints
- A local replay command
- Backend telemetry
- A separate completion state

After a lesson is solved, the page shows an unlocked item. After a challenge is solved, the ecommerce storefront also shows an updated fulfillment state.

## Burp Suite Setup

Burp must not use port `8080` for its own listener because the lab proxy already owns that port.

### Configure a Burp listener

1. Open Burp Suite.
2. Go to **Proxy → Proxy settings**.
3. Create or edit a Burp listener.
4. Use:

   ```text
   Address: 127.0.0.1
   Port: 8082
   ```

### Use Repeater

For the simplest workflow, use Burp Repeater directly:

1. Open **Repeater**.
2. Set the target to:

   ```text
   http://localhost:8080
   ```

3. Use HTTP/1.1.
4. Do not use HTTPS.
5. Disable automatic `Content-Length` updates when working with framing lessons.
6. Start with the normal request shown on the challenge page.
7. Use the progressive hints to understand the lesson.

The lab UI runs on port `3000`. Burp challenge traffic goes to port `8080`.

## Beginner Workflow

1. Open the storefront at `http://localhost:3000`.
2. Add a product to the cart.
3. Open `http://localhost:3000/challenge`.
4. Read Lesson 01 before sending any special request.
5. In Burp Repeater, send the normal protected-route request shown on the page.
6. Confirm that the frontend returns `403 Forbidden`.
7. Unlock hints one at a time.
8. Send the controlled lesson request through `http://localhost:8080`.
9. Refresh the challenge page.
10. Watch the item count change from `0 items unlocked` to `1 item unlocked`.
11. Continue with the next lesson.

## Local Replay Helpers

Burp is the recommended learning tool. The following helpers are optional and are restricted to the local lab proxy:

```bash
python3 labs/series.py --challenge boundary
python3 labs/series.py --challenge cl-te
python3 labs/series.py --challenge te-cl
python3 labs/series.py --challenge cl-zero
python3 labs/series.py --challenge h2-downgrade
```

These commands are useful for checking that Docker is working, but use Burp when recording or learning the request flow.

## Monitoring

The challenge page contains a live monitor. You can also view backend logs in a second terminal:

```bash
docker compose logs -f backend
```

Important log messages include:

```text
Request boundary calculated
Request boundary mismatch detected
Backend processed secondary request
FLAG RELEASED
```

## Reset the Challenge

### Reset only challenge progress

Run:

```bash
curl http://localhost:8080/api/reset
```

Then refresh:

```text
http://localhost:3000/challenge
```

The page should show:

```text
0/5
0 items unlocked
```

### Restart the backend

```bash
docker compose restart backend
```

### Full restart

```bash
docker compose down
docker compose up --build
```

## Patched Proxy

Repeat a lesson against:

```text
http://localhost:8081
```

The patched proxy rejects ambiguous framing with:

```text
HTTP/1.1 400 Bad Request
```

Comparison:

```text
Vulnerable:
Frontend parser != Backend parser
                |
          Desync possible

Patched:
Ambiguous framing rejected
                |
          No forwarding
```

## Troubleshooting

### Port already in use

Check which containers are running:

```bash
docker compose ps
```

Stop old DesyncLab containers:

```bash
docker compose down --remove-orphans
```

Then start again:

```bash
docker compose up --build
```

Do not run Burp's listener on port `8080`.

### Website shows an old page

Hard refresh the browser:

```text
Ctrl + Shift + R
```

### Challenge stays at zero

Check the state API:

```bash
curl http://localhost:8080/api/state
```

Check backend logs:

```bash
docker compose logs --tail=100 backend
```

Make sure Burp is targeting `http://localhost:8080`, not `https://localhost:8080`.

### Burp shows only the first response

Refresh the challenge page and check the monitor. The backend may process the secondary request even when Burp displays the first response separately.

## Stop the Lab

```bash
docker compose down
```

To remove unused Docker resources created by this project:

```bash
docker compose down --remove-orphans
```

## Learning Scope

This project intentionally focuses only on HTTP request smuggling and desynchronization. It does not intentionally include SQL injection, XSS, SSRF, command injection, path traversal, IDOR, insecure JWTs, credential capture, arbitrary proxying, or external target support.

Use the lab only on your own machine and isolated Docker network.

## Author Documentation

`SOLUTION.md` contains the intended parser analysis, challenge conditions, and remediation. Keep it private when using the repository as a player-facing CTF.
