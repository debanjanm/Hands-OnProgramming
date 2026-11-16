# 01. HTTP In One Page: Methods, Status Codes, Headers
# 02. A Tiny Local Server (http.server + ThreadingHTTPServer)
# 03. Starting The Server On Port 0 In A Daemon Thread
# 04. urllib.request: GET And Reading The Response
# 05. urllib.request: POST JSON And Custom Headers
# 06. urllib.request: Errors (HTTPError vs URLError)
# 07. Query Strings Done Right
# 08. Cookies
# 09. requests: GET, params, json, headers
# 10. requests: raise_for_status And Error Handling
# 11. requests: Timeouts
# 12. requests: Redirects
# 13. requests: Session (Connection Reuse, Shared Defaults)
# 14. requests: Streaming Responses
# 15. Retries With Exponential Backoff
# 16. httpx: The Modern Sibling
# 17. Basic Auth And Bearer Tokens
# 18. Never Hardcode Secrets
# 19. Clean Shutdown

# Everything here talks ONLY to 127.0.0.1 on an ephemeral port. No internet.

import base64
import http.cookiejar
import json
import os
import socket
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import requests
except ImportError:
    requests = None

try:
    import httpx
except ImportError:
    httpx = None

# 01. HTTP In One Page: Methods, Status Codes, Headers
# ----------------------------
# - HTTP is a text request/response protocol: one request line
#   ("GET /path HTTP/1.1"), headers, blank line, optional body.
# - Methods: GET (read), POST (create / action), PUT (replace),
#   PATCH (partial update), DELETE (remove), HEAD (headers only).
# - Safe = does not change state (GET, HEAD). Idempotent = repeating has the
#   same effect (GET, PUT, DELETE). POST is neither - careful with retries.
# - Status classes: 1xx info, 2xx success, 3xx redirect, 4xx YOUR fault,
#   5xx SERVER fault.
# - Key headers: Content-Type (what the body is), Accept (what I want back),
#   Authorization, Cookie / Set-Cookie, Location (redirects).

for code in (200, 201, 204, 301, 302, 400, 401, 403, 404, 429, 500, 503):
    print(code, HTTPStatus(code).phrase)
print("200 is success? ", 200 // 100 == 2)
print("404 is client error? ", 404 // 100 == 4)
print("# Gotcha: 401 = 'who are you?' (not authenticated); 403 = 'I know you, no.'")

# 02. A Tiny Local Server (http.server + ThreadingHTTPServer)
# ----------------------------
# - We build a real HTTP server in ~60 lines so every client demo has
#   something deterministic to talk to - no internet needed.
# - Subclass BaseHTTPRequestHandler, implement do_GET / do_POST / ...
# - Each handler reads self.path, self.headers, self.rfile (request body),
#   and writes self.send_response / send_header / end_headers / wfile.
# - Override log_message to silence the default stderr access log.
# - ThreadingHTTPServer handles each request in its own thread, so a
#   /slow request does not block everything else.

STATE = {"flaky": 0}
TOKEN = "demo-token-123"  # a throwaway value for a local demo only
USER, PASSWORD = "alice", "wonderland"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence request logging
        pass

    def _send(self, status, payload=None, headers=None, raw=None, ctype="application/json"):
        body = raw if raw is not None else json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def _route(self):
        url = urllib.parse.urlsplit(self.path)
        q = urllib.parse.parse_qs(url.query)
        path = url.path

        if path == "/hello":
            return self._send(200, {"message": "hello"})
        if path == "/params":
            return self._send(200, {"query": q})
        if path == "/echo":
            raw = self._body()
            try:
                data = json.loads(raw) if raw else None
            except ValueError:
                return self._send(400, {"error": "invalid json"})
            return self._send(200, {
                "method": self.command, "json": data,
                "content_type": self.headers.get("Content-Type"),
                "x_demo": self.headers.get("X-Demo"),
            })
        if path == "/redirect":
            return self._send(302, {"moved": True}, headers={"Location": "/hello"})
        if path == "/slow":
            time.sleep(float(q.get("delay", ["0.5"])[0]))
            return self._send(200, {"slow": True})
        if path.startswith("/status/"):
            code = int(path.rsplit("/", 1)[1])
            return self._send(code, {"status": code})
        if path == "/flaky":  # fails twice with 503, then succeeds
            STATE["flaky"] += 1
            if STATE["flaky"] <= 2:
                return self._send(503, {"error": "try again"}, headers={"Retry-After": "0"})
            return self._send(200, {"ok": True, "attempt": STATE["flaky"]})
        if path == "/reset":
            STATE["flaky"] = 0
            return self._send(200, {"reset": True})
        if path == "/set-cookie":
            return self._send(200, {"set": True}, headers={"Set-Cookie": "session=abc123; Path=/; HttpOnly"})
        if path == "/whoami":
            return self._send(200, {"cookie": self.headers.get("Cookie")})
        if path == "/stream":
            lines = "".join(f"line {i}\n" for i in range(5)).encode()
            return self._send(200, raw=lines, ctype="text/plain")
        if path == "/bearer":
            if self.headers.get("Authorization") == f"Bearer {TOKEN}":
                return self._send(200, {"auth": "bearer ok"})
            return self._send(401, {"error": "bad token"}, headers={"WWW-Authenticate": "Bearer"})
        if path == "/basic":
            good = "Basic " + base64.b64encode(f"{USER}:{PASSWORD}".encode()).decode()
            if self.headers.get("Authorization") == good:
                return self._send(200, {"auth": "basic ok", "user": USER})
            return self._send(401, {"error": "bad credentials"}, headers={"WWW-Authenticate": 'Basic realm="demo"'})
        return self._send(404, {"error": "not found", "path": path})

    do_GET = do_POST = do_PUT = do_PATCH = do_DELETE = do_HEAD = _route


print("routes: /hello /params /echo /redirect /slow /status/N /flaky /set-cookie /whoami /bearer /basic /stream")

# 03. Starting The Server On Port 0 In A Daemon Thread
# ----------------------------
# - Port 0 means "OS, pick any free port". Read the real one back from
#   server.server_address[1]. Hardcoded ports collide in CI and on laptops.
# - Bind to 127.0.0.1 (loopback only) - never 0.0.0.0 for a demo server;
#   that would expose it to your whole network.
# - serve_forever() blocks, so run it in a thread. daemon=True means the
#   interpreter will not hang waiting for it at exit.
# - shutdown() stops serve_forever (call from ANOTHER thread);
#   server_close() releases the socket.

server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
server.daemon_threads = True           # per-request threads die with the process
server.handle_error = lambda *a: None  # ignore resets from timed-out clients
thread = threading.Thread(target=server.serve_forever, daemon=True)
thread.start()
BASE = f"http://127.0.0.1:{server.server_address[1]}"  # never print this
print("server thread alive:", thread.is_alive())
print("bound to loopback:", server.server_address[0] == "127.0.0.1")

try:
    # 04. urllib.request: GET And Reading The Response
    # ----------------------------
    # - urllib is in the stdlib: zero installs. Good for scripts and for
    #   understanding what the nicer libraries do for you.
    # - urlopen returns a response usable as a context manager.
    # - You get bytes: .read() then decode, and json.loads yourself.
    # - Proxies from the environment are honoured by default; we build an
    #   opener with an empty ProxyHandler so localhost never goes via one.

    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(f"{BASE}/hello", timeout=5) as resp:
        raw = resp.read()
        print("status:", resp.status, resp.reason)
        print("content-type:", resp.headers["Content-Type"])
        print("body bytes:", raw)
        print("parsed:", json.loads(raw))
    print("# Gotcha: forgetting timeout= means a stuck server can hang you forever.")

    # 05. urllib.request: POST JSON And Custom Headers
    # ----------------------------
    # - Passing data= (bytes) turns the request into a POST automatically.
    # - You must encode the body AND set Content-Type yourself.
    # - Use method="PUT" etc. on a Request object for other verbs.

    payload = json.dumps({"name": "Ada", "langs": ["py", "c"]}).encode()
    req = urllib.request.Request(
        f"{BASE}/echo", data=payload, method="POST",
        headers={"Content-Type": "application/json", "X-Demo": "yes"},
    )
    with opener.open(req, timeout=5) as resp:
        print("POST ->", resp.status, json.loads(resp.read()))
    req = urllib.request.Request(f"{BASE}/echo", data=b'{"v": 1}', method="PUT",
                                 headers={"Content-Type": "application/json"})
    with opener.open(req, timeout=5) as resp:
        print("PUT method echoed:", json.loads(resp.read())["method"])

    # 06. urllib.request: Errors (HTTPError vs URLError)
    # ----------------------------
    # - urllib RAISES for 4xx/5xx: urllib.error.HTTPError (has .code, and is
    #   also a readable response - the error body is often useful JSON).
    # - URLError = could not even talk to the server (refused, DNS, timeout).
    # - HTTPError is a SUBCLASS of URLError, so catch HTTPError first.

    try:
        opener.open(f"{BASE}/status/404", timeout=5)
    except urllib.error.HTTPError as e:
        print("HTTPError code:", e.code, "| body:", json.loads(e.read()))
        e.close()

    dead = socket.socket()
    dead.bind(("127.0.0.1", 0))
    dead_port = dead.getsockname()[1]
    dead.close()  # now nothing listens on that port
    try:
        opener.open(f"http://127.0.0.1:{dead_port}/", timeout=2)
    except urllib.error.URLError as e:
        print("URLError (connection refused):", type(e.reason).__name__)
    print("HTTPError is a URLError:", issubclass(urllib.error.HTTPError, urllib.error.URLError))

    # 07. Query Strings Done Right
    # ----------------------------
    # - Never build query strings with f-strings: spaces, &, = and unicode
    #   break them (and invite injection). Use urllib.parse.urlencode.
    # - parse_qs gives lists, because a key may repeat (?tag=a&tag=b).
    # - urlsplit/urljoin take URLs apart and combine them safely.

    qs = urllib.parse.urlencode({"q": "a b&c=d", "tag": ["x", "y"], "n": 3}, doseq=True)
    print("encoded:", qs)
    print("decoded:", urllib.parse.parse_qs(qs))
    with opener.open(f"{BASE}/params?{qs}", timeout=5) as resp:
        print("server saw:", json.loads(resp.read())["query"])
    print("urljoin:", urllib.parse.urljoin("http://h/api/v1/", "users/7"))
    print("# Gotcha: urljoin('http://h/api/v1', 'users') DROPS 'v1' (no trailing slash).")
    print("urljoin w/o slash:", urllib.parse.urljoin("http://h/api/v1", "users"))

    # 08. Cookies
    # ----------------------------
    # - Server sends Set-Cookie; the client must send it back in a Cookie
    #   header on later requests. HTTP itself has no memory - cookies fake it.
    # - Raw urllib does not remember them; use http.cookiejar's
    #   CookieJar + HTTPCookieProcessor, or a requests/httpx session.
    # - Flags: HttpOnly (JS cannot read), Secure (https only), SameSite.

    jar = http.cookiejar.CookieJar()
    copener = urllib.request.build_opener(urllib.request.ProxyHandler({}),
                                          urllib.request.HTTPCookieProcessor(jar))
    with copener.open(f"{BASE}/set-cookie", timeout=5) as resp:
        print("Set-Cookie header:", resp.headers["Set-Cookie"])
    print("jar now holds:", [(c.name, c.value) for c in jar])
    with copener.open(f"{BASE}/whoami", timeout=5) as resp:
        print("server saw Cookie:", json.loads(resp.read())["cookie"])

    # 09. requests: GET, params, json, headers
    # ----------------------------
    # - requests (pip install requests) is the friendly sync client.
    # - params={...} encodes the query for you; json={...} serializes AND
    #   sets Content-Type: application/json; data={...} would send a form.
    # - resp.json() parses; resp.text decodes; resp.content is bytes.
    # - trust_env=False on a Session ignores proxy env vars (safe for local).

    if requests is None:
        print("SKIP: requests is not installed (pip install requests)")
    else:
        s0 = requests.Session()
        s0.trust_env = False
        r = s0.get(f"{BASE}/params", params={"q": "py thon", "page": 2}, timeout=5)
        print("GET", r.status_code, r.json())
        print("content-type:", r.headers["content-type"])
        r = s0.post(f"{BASE}/echo", json={"a": [1, 2]}, headers={"X-Demo": "req"}, timeout=5)
        print("POST json ->", r.json())
        r = s0.post(f"{BASE}/echo", data="not json at all", timeout=5)
        print("bad body ->", r.status_code, r.json())
        print("# Gotcha: json= and data= are different; data=dict sends a FORM body.")
        r = s0.head(f"{BASE}/hello", timeout=5)
        print("HEAD body length:", len(r.content), "| has content-length:", "Content-Length" in r.headers)

        # 10. requests: raise_for_status And Error Handling
        # ----------------------------
        # - requests does NOT raise on 404/500 by itself. A 500 is a
        #   perfectly valid response as far as the library is concerned.
        # - resp.raise_for_status() raises HTTPError for 4xx/5xx; resp.ok is
        #   the boolean version.
        # - Network-level failures raise ConnectionError / Timeout. All
        #   inherit from requests.exceptions.RequestException - catch that
        #   as the single umbrella.

        r = s0.get(f"{BASE}/status/404", timeout=5)
        print("no exception, status:", r.status_code, "| ok:", r.ok)
        try:
            r.raise_for_status()
        except requests.HTTPError as e:
            print("raise_for_status ->", type(e).__name__, "| code:", e.response.status_code)
        try:
            s0.get(f"http://127.0.0.1:{dead_port}/", timeout=2)
        except requests.exceptions.RequestException as e:
            print("umbrella caught:", type(e).__name__)

        # 11. requests: Timeouts
        # ----------------------------
        # - requests has NO default timeout: without timeout= it can wait forever.
        # - timeout=5 applies to connect and to each read gap; use
        #   (connect, read) tuple for finer control.
        # - It is NOT a total deadline: a server dribbling a byte every few
        #   seconds can still keep you waiting.

        try:
            s0.get(f"{BASE}/slow", params={"delay": 0.6}, timeout=(2, 0.15))
        except requests.exceptions.Timeout as e:
            print("timed out:", type(e).__name__)

        # 12. requests: Redirects
        # ----------------------------
        # - requests follows redirects for GET by default (allow_redirects=True).
        # - resp.history lists the hops; resp.url is the FINAL url.
        # - allow_redirects=False lets you inspect the 3xx and Location.

        r = s0.get(f"{BASE}/redirect", timeout=5)
        print("followed:", r.status_code, "| hops:", [h.status_code for h in r.history],
              "| final path:", urllib.parse.urlsplit(r.url).path)
        r = s0.get(f"{BASE}/redirect", allow_redirects=False, timeout=5)
        print("not followed:", r.status_code, "| Location:", r.headers["Location"])
        s0.close()

        # 13. requests: Session (Connection Reuse, Shared Defaults)
        # ----------------------------
        # - A Session keeps TCP connections alive (faster for many calls),
        #   persists cookies, and shares default headers/auth.
        # - Always close it: use "with requests.Session() as s:".
        # - Per-call arguments override session defaults.

        with requests.Session() as s:
            s.trust_env = False
            s.headers.update({"X-Demo": "from-session"})
            s.get(f"{BASE}/set-cookie", timeout=5)
            print("cookie remembered:", s.get(f"{BASE}/whoami", timeout=5).json())
            print("session header sent:", s.post(f"{BASE}/echo", json={}, timeout=5).json()["x_demo"])
            print("per-call override:",
                  s.post(f"{BASE}/echo", json={}, headers={"X-Demo": "override"}, timeout=5).json()["x_demo"])

        # 14. requests: Streaming Responses
        # ----------------------------
        # - stream=True defers downloading the body, so big files do not sit
        #   fully in memory. Read with iter_content / iter_lines.
        # - Use the response as a context manager so the connection is
        #   released even if you stop early.

        with requests.Session() as s:
            s.trust_env = False
            with s.get(f"{BASE}/stream", stream=True, timeout=5) as r:
                for line in r.iter_lines(decode_unicode=True):
                    print("got:", line)

    # 15. Retries With Exponential Backoff
    # ----------------------------
    # - Retry only what is safe: network errors and 429/502/503/504, on
    #   idempotent requests (GET/PUT/DELETE). Blindly retrying POST can
    #   create duplicates - use an idempotency key (see next topic).
    # - Backoff: wait base * 2**attempt so you do not hammer a struggling
    #   server. Add random jitter in real life so clients do not retry in
    #   lockstep (omitted here to keep output deterministic).
    # - Cap the number of attempts and honour Retry-After when present.
    # - requests can do this via urllib3 Retry + HTTPAdapter; below is the
    #   plain hand-rolled loop first so the idea is visible.

    def get_with_retry(fetch, attempts=4, base=0.01):
        for attempt in range(attempts):
            status, body = fetch()
            if status not in (429, 502, 503, 504):
                return status, body, attempt + 1
            time.sleep(base * 2 ** attempt)
        return status, body, attempts

    def urllib_fetch():
        try:
            with opener.open(f"{BASE}/flaky", timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            body = json.loads(e.read())
            e.close()
            return e.code, body

    opener.open(f"{BASE}/reset", timeout=5).close()
    status, body, tries = get_with_retry(urllib_fetch)
    print("final status:", status, "| tries needed:", tries, "| ok:", body["ok"])
    opener.open(f"{BASE}/reset", timeout=5).close()
    status, body, tries = get_with_retry(urllib_fetch, attempts=2)
    print("with only 2 attempts:", status, "| gave up after:", tries)

    if requests is not None:
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        opener.open(f"{BASE}/reset", timeout=5).close()
        with requests.Session() as s:
            s.trust_env = False
            retry = Retry(total=3, backoff_factor=0.01, status_forcelist=[503], allowed_methods=["GET"])
            s.mount("http://", HTTPAdapter(max_retries=retry))
            r = s.get(f"{BASE}/flaky", timeout=5)
            print("urllib3 Retry adapter ->", r.status_code, r.json()["ok"])

    # 16. httpx: The Modern Sibling
    # ----------------------------
    # - httpx (pip install httpx) mirrors the requests API and adds async
    #   (see topic 03) and optional HTTP/2.
    # - Differences that bite: redirects are NOT followed by default
    #   (follow_redirects=True); it has a default 5s timeout (requests has
    #   none); raise_for_status exists and raises httpx.HTTPStatusError.
    # - Client(base_url=...) lets you write relative paths.
    # - Timeouts raise httpx.TimeoutException (ReadTimeout, ConnectTimeout...).

    if httpx is None:
        print("SKIP: httpx is not installed (pip install httpx)")
    else:
        with httpx.Client(base_url=BASE, trust_env=False, timeout=5.0) as c:
            r = c.get("/params", params={"q": "py", "page": 2})
            print("GET", r.status_code, r.json())
            r = c.post("/echo", json={"x": 1}, headers={"X-Demo": "httpx"})
            print("POST json ->", r.json())
            r = c.get("/redirect")
            print("default redirect behaviour:", r.status_code, "| is_redirect:", r.is_redirect)
            r = c.get("/redirect", follow_redirects=True)
            print("with follow_redirects:", r.status_code)
            try:
                c.get("/status/500").raise_for_status()
            except httpx.HTTPStatusError as e:
                print("HTTPStatusError:", e.response.status_code)
            try:
                c.get("/slow", params={"delay": 0.6}, timeout=0.15)
            except httpx.TimeoutException as e:
                print("timeout:", type(e).__name__)
            with c.stream("GET", "/stream") as r:
                print("streamed lines:", list(r.iter_lines())[:2], "...")

    # 17. Basic Auth And Bearer Tokens
    # ----------------------------
    # - Basic: header "Authorization: Basic base64(user:password)". Base64 is
    #   ENCODING, not encryption - anyone seeing it can read it, so only use
    #   over HTTPS.
    # - Bearer: "Authorization: Bearer <token>" - the token is the secret;
    #   whoever holds ("bears") it gets access.
    # - Libraries have helpers: requests auth=(user, pw), httpx auth=(user, pw).
    # - 401 means missing/invalid credentials; the server sends WWW-Authenticate.

    token = base64.b64encode(b"alice:wonderland").decode()
    print("base64 is reversible:", base64.b64decode(token).decode())

    def urllib_status(path, headers=None):
        req = urllib.request.Request(f"{BASE}{path}", headers=headers or {})
        try:
            with opener.open(req, timeout=5) as resp:
                return resp.status, json.loads(resp.read())
        except urllib.error.HTTPError as e:
            e.close()
            return e.code, None

    print("bearer, no token  ->", urllib_status("/bearer")[0])
    print("bearer, wrong     ->", urllib_status("/bearer", {"Authorization": "Bearer nope"})[0])
    print("bearer, right     ->", urllib_status("/bearer", {"Authorization": f"Bearer {TOKEN}"}))
    print("basic via header  ->", urllib_status("/basic", {"Authorization": f"Basic {token}"}))
    if requests is not None:
        with requests.Session() as s:
            s.trust_env = False
            print("requests auth=(u,p) ->", s.get(f"{BASE}/basic", auth=(USER, PASSWORD), timeout=5).json())
            print("requests bad pw     ->", s.get(f"{BASE}/basic", auth=(USER, "x"), timeout=5).status_code)
    if httpx is not None:
        with httpx.Client(trust_env=False, headers={"Authorization": f"Bearer {TOKEN}"}) as c:
            print("httpx bearer default header ->", c.get(f"{BASE}/bearer").json())

    # 18. Never Hardcode Secrets
    # ----------------------------
    # - Tokens in source code end up in git history, logs, screenshots, and
    #   forks - and are nearly impossible to fully revoke from history.
    # - Read secrets from the environment (or a secret manager) at runtime:
    #   os.environ["API_TOKEN"]; fail loudly if missing.
    # - Keep .env files out of git (.gitignore). Rotate any leaked key.
    # - Do not log Authorization headers or full URLs with ?api_key=...
    # - Prefer headers to query-string secrets: URLs are logged everywhere.
    # - The TOKEN constant above is a throwaway for a local demo, never a
    #   real credential.

    def load_token(name="DEMO_API_TOKEN_NOT_SET"):
        value = os.environ.get(name)
        if not value:
            raise RuntimeError(f"set the {name} environment variable")
        return value

    try:
        load_token()
    except RuntimeError as e:
        print("missing secret fails loudly:", e)

    def redact(headers):
        return {k: ("***" if k.lower() in {"authorization", "cookie"} else v) for k, v in headers.items()}

    print("safe to log:", redact({"Authorization": f"Bearer {TOKEN}", "Accept": "application/json"}))

finally:
    # 19. Clean Shutdown
    # ----------------------------
    # - Always stop servers in a finally block so an exception earlier does
    #   not leave a thread or socket behind.
    # - Order: shutdown() (stops the loop, blocks until it exits) ->
    #   server_close() (closes the listening socket) -> join the thread.
    # - Calling shutdown() from inside the serve_forever thread deadlocks.
    # - daemon_threads=True on the server and daemon=True on the thread
    #   stop stragglers (e.g. a still-sleeping /slow handler) from delaying exit.

    server.shutdown()
    server.server_close()
    thread.join(timeout=5)
    print("server thread stopped:", not thread.is_alive())
