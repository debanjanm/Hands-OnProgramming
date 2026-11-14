# Networking Basics — Notes

## What this covers
How programs talk over a network, shown safely on `127.0.0.1` only: raw `socket` (TCP and UDP), `socketserver`, then the HTTP layer (`http.server`, `urllib`, `http.client`, `urllib.parse`), plus HTTPS and email as reference.

## Key points
- **Vocabulary**: the **server** waits, the **client** starts. **IP address** = which computer (`127.0.0.1` = this one), **port** = which program on it. **TCP** = reliable ordered stream (like a phone call). **UDP** = independent datagrams, no guarantees (like postcards).
- **TCP server**: `socket()`, `bind((host, 0))` (port 0 = OS picks a free port, read it with `getsockname()`), `listen()`, `accept()` (returns a new socket per client). **Client**: `connect()` or `socket.create_connection(...)`, then `sendall()` / `recv()`. Use `with` to close sockets. `SO_REUSEADDR` allows quick restarts.
- **TCP is a stream, not messages.** `recv(n)` returns *at most* `n` bytes; two sends can arrive glued together. Define framing yourself: a delimiter (`\n`) or a **length prefix** (`struct.pack("!I", len)` + payload, then loop until you have exactly that many bytes).
- **Always set timeouts**: `settimeout(s)` makes blocking calls raise `socket.timeout` instead of hanging.
- **UDP**: `bind`, `sendto(data, addr)`, `recvfrom(size)`. One send = one receive (boundaries kept), but delivery is not guaranteed.
- **`socketserver.ThreadingTCPServer`** + a `StreamRequestHandler` (`handle()` reading `self.rfile`) replaces the hand-written accept loop. `selectors` = one thread watching many sockets (what `asyncio` does underneath).
- **HTTP**: request line + headers + body, response with a status. 2xx ok, 4xx client's fault, 5xx server's fault. `ThreadingHTTPServer` + `BaseHTTPRequestHandler` (`do_GET`, `do_POST`); override `log_message` to silence logs; always send `Content-Length`.
- **Clients**: `urllib.request.urlopen(url, timeout=...)`, `Request(url, data=bytes, headers=..., method=...)`, `http.client.HTTPConnection` for low-level control. JSON round trip: `json.dumps(...).encode()` out, `json.loads(resp.read())` in.
- **`urllib.parse`**: `urlparse/urlsplit` (take apart), `urlunparse` (rebuild), `urlencode` (safe query strings), `parse_qs` (values are lists), `quote`, `urljoin`.
- **Retry with backoff** for transient failures only (timeouts, connection errors, 502/503/504): wait 0.05, 0.1, 0.2... Never retry a 4xx.

## Gotchas (the part worth revising twice)
- **One `sendall` is not one `recv`.** Reading without a loop or framing works on your laptop and breaks in production.
- **No timeout = possible hang forever.** (`requests` has no default timeout either.)
- **`urlopen` raises `HTTPError` for 4xx/5xx**, and `HTTPError` is a subclass of `URLError`, so catch `HTTPError` first. An `HTTPError` still holds the response body (`err.read()`). `URLError.reason` holds the real cause (e.g. `ConnectionRefusedError`).
- **`urlopen` data must be bytes**, and responses come back as bytes (decode them).
- **Environment proxies**: `urllib` may route traffic through `http_proxy`; for localhost install an opener with `ProxyHandler({})`.
- **Server shutdown order**: `server.shutdown()` (from another thread), then `server_close()`, then join the thread. Use daemon threads so a bug cannot keep the script alive.
- **Clients that give up** cause `BrokenPipeError` in the handler; catch it, it is normal.
- **Don't build URLs by string concatenation**: `&`, `=`, spaces and `/` in values corrupt it; use `urlencode`. `urljoin` with an absolute second argument replaces the base.
- **Security**: bind to `127.0.0.1`, not `0.0.0.0`, unless you truly mean to expose it. Validate every input (JSON shape, body size). The `Host` header and all headers are chosen by the client; never trust them. No secrets in URLs. Never disable TLS verification.
- **Port 0 trick**: ephemeral ports differ each run; never hard-code ports in demos or tests.

## When it matters
Calling REST APIs (use `requests`/`httpx` in real projects: `requests.post(url, json=data, timeout=3)`), writing tiny test servers, health checks, custom protocols, understanding what frameworks do underneath, and diagnosing "connection refused", "timed out" and "address already in use". HTTPS (`ssl.create_default_context()`) verifies certificates by default; email is built with `EmailMessage` and sent with `smtplib` (not run here).

## One-line recap example
```python
import json, urllib.request
with urllib.request.urlopen("http://127.0.0.1:8000/api/hello", timeout=3) as r:   # always a timeout
    print(r.status, json.loads(r.read()))   # 200 {'message': 'Hello, world!'}
```
