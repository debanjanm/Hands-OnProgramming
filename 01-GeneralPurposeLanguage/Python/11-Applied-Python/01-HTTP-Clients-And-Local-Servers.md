# HTTP Clients and Local Servers — Notes

## What this covers
HTTP basics (methods, status codes, headers, cookies), a tiny stdlib `ThreadingHTTPServer` bound to `127.0.0.1` port 0 and run in a daemon thread, and three clients against it: `urllib.request`, `requests`, and `httpx` — params, JSON, timeouts, redirects, retries with backoff, sessions, streaming, error handling, and auth.

## Key points
- Methods: GET/HEAD are *safe*; GET/PUT/DELETE are *idempotent*; POST is neither. Status classes: 2xx ok, 3xx redirect, 4xx client fault, 5xx server fault.
- Bind demo servers to `127.0.0.1` and port `0`; read the real port from `server.server_address[1]`.
- Run `serve_forever()` in a daemon thread; stop with `shutdown()` then `server_close()` then `join()`, inside a `finally`.
- `urllib` raises `HTTPError` for 4xx/5xx (a subclass of `URLError`, so catch it first). `requests` does **not** raise unless you call `raise_for_status()`.
- Build query strings with `urlencode` / `params=`, never f-strings.
- `requests.Session` / `httpx.Client` reuse connections, keep cookies, and share default headers and auth.
- Retry only idempotent requests on 429/502/503/504; use exponential backoff (`base * 2**attempt`), jitter, and a max attempts cap.
- Basic auth is base64 (reversible, not encryption); a bearer token *is* the secret.
- Read secrets from environment variables; never commit them or log `Authorization` headers.

## Gotchas (the part worth revising twice)
- `requests` has **no default timeout** — always pass `timeout=`. `httpx` defaults to 5 s.
- `httpx` does **not** follow redirects by default; `requests` does.
- `timeout` is per-operation, not a total deadline.
- `json=` serializes and sets the content type; `data=dict` sends a form body.
- `urljoin("http://h/api/v1", "users")` silently drops `v1` — keep the trailing slash.
- 401 means unauthenticated, 403 means authenticated but forbidden.
- Calling `server.shutdown()` from the server thread itself deadlocks; a still-sleeping handler can delay exit unless threads are daemons.
- Proxy environment variables can hijack localhost calls — set `trust_env=False` or use an empty `ProxyHandler`.
- Blind retries of POST can create duplicate records.

## When it matters
Any script or service that calls another service: integrations, webhooks, health checks, scrapers. A local server makes your tests fast, offline, and deterministic.

## One-line recap example
```python
import requests
r = requests.get("http://127.0.0.1:8000/items", params={"q": "py"}, timeout=5)
r.raise_for_status()
print(r.json())
```
