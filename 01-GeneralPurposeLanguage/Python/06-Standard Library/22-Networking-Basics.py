import email.utils
import http.client
import json
import selectors
import socket
import socketserver
import ssl
import struct
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# 01. Networking - How a Request Works (in Plain Words)
# ------------------------------------
# - Two programs talk over a network. One WAITS (the SERVER), one STARTS the
#   conversation (the CLIENT).
# - ADDRESS: an IP address says WHICH computer ("93.184.216.34", or
#   127.0.0.1 = "this very computer", called localhost / the loopback address).
# - PORT: a number (0-65535) says WHICH PROGRAM on that computer. Think of the
#   IP as a building and the port as the apartment number. Web = 80/443,
#   SSH = 22. Ports below 1024 usually need admin rights.
# - TCP: reliable, ordered, connection-based. Like a phone call: connect first,
#   then a continuous two-way stream of bytes; lost data is resent for you.
#   Used by the web, email, databases, SSH.
# - UDP: no connection, no promises. Like posting letters: each datagram is
#   independent, may be lost, duplicated or reordered. Fast and simple.
#   Used by DNS, video calls, games, metrics.
# - REQUEST / RESPONSE: the client sends a request ("GET /users/5"), the server
#   sends a response (status + data). HTTP is this pattern on top of TCP.
# - The layers you will meet in this file, lowest to highest:
#       socket (raw TCP/UDP)  ->  socketserver (handler classes)  ->  http.server / http.client / urllib (HTTP)
# - SAFETY RULE FOR THIS FILE: it talks ONLY to 127.0.0.1 (this computer) on
#   ports the operating system picks for us (port 0 = "pick any free one").
#   Nothing leaves your machine. Every server runs in a daemon thread, every
#   socket has a timeout, and everything is shut down at the end.

print("# 01. Networking - How a Request Works")
print("# ------------------------------------")

LOCALHOST = "127.0.0.1"

# Some systems route urllib through an HTTP proxy named in environment variables
# (http_proxy). Localhost traffic must NEVER go through one, so install an
# opener with NO proxies. (Real code on a corporate network often wants the opposite.)
urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))


# 02. A TCP Echo Server in a Thread
# ------------------------------------
# - Server steps:  socket() -> bind((host, port)) -> listen() -> accept() (waits for a client)
#                  -> recv()/sendall() on the connection socket -> close()
# - Client steps:  socket() -> connect((host, port)) -> sendall()/recv() -> close()
# - accept() returns a NEW socket just for that client; the listening socket
#   keeps listening. That is how one server handles many clients.
# - SO_REUSEADDR: lets you restart a server immediately on the same port
#   instead of "Address already in use" while the old one lingers in TIME_WAIT.
# - A `with` block closes the socket for you, even when an error happens.
# - We use a daemon thread so the server runs "in the background" while the
#   same script plays the client. daemon=True means it can never keep the
#   script alive on exit.
class TcpServerThread:
    """Run `handler(conn)` for each accepted TCP connection, one at a time, in a daemon thread."""

    def __init__(self, handler):
        self.handler = handler
        self.stop_event = threading.Event()
        self.ready = threading.Event()
        self.port = None
        self.thread = threading.Thread(target=self._serve, daemon=True)

    def _serve(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((LOCALHOST, 0))  # port 0 = let the OS choose a free port
            server.listen()
            server.settimeout(0.1)  # so the loop can notice stop_event
            self.port = server.getsockname()[1]  # read back the port we were given
            self.ready.set()
            while not self.stop_event.is_set():
                try:
                    conn, _addr = server.accept()
                except socket.timeout:
                    continue
                with conn:
                    conn.settimeout(3)
                    try:
                        self.handler(conn)
                    except (socket.timeout, ConnectionError):
                        pass  # a misbehaving client must not kill the server

    def __enter__(self):
        self.thread.start()
        if not self.ready.wait(5):
            raise RuntimeError("server did not start")
        return self

    def __exit__(self, *exc):
        self.stop_event.set()
        self.thread.join(timeout=5)


def echo_handler(conn):
    while data := conn.recv(1024):  # b"" means the client closed its side
        conn.sendall(data)  # sendall keeps sending until ALL bytes are written


print("\n# 02. TCP echo server and client")
with TcpServerThread(echo_handler) as srv:
    print("server listening on an OS-chosen port:", srv.port > 0)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        client.settimeout(3)
        client.connect((LOCALHOST, srv.port))
        client.sendall(b"hello socket")
        print("client got back:", client.recv(1024))
        print("local address (ip, port>0):", client.getsockname()[0], client.getsockname()[1] > 0)
        print("peer address matches server:", client.getpeername() == (LOCALHOST, srv.port))

# 03. TCP Is a STREAM, Not Messages (the Big Gotcha)
# ------------------------------------
# - TCP delivers a river of bytes, in order. It does NOT remember where each
#   sendall() ended. Two sends can arrive glued together; one send can arrive
#   in pieces. recv(n) means "give me AT MOST n bytes" - possibly fewer.
# - So you must define your own message boundaries ("framing"). Common ways:
#     * a delimiter (HTTP headers end with a blank line, many protocols use \n)
#     * a length prefix (first 4 bytes = how long the message is)  <- shown below
print("\n# 03. TCP is a stream: partial reads and glued messages")


def two_sends_handler(conn):
    conn.sendall(b"AAAA")  # two separate sends...
    conn.sendall(b"BBBB")
    time.sleep(0.2)  # keep the connection open until the client has read


with TcpServerThread(two_sends_handler) as srv:
    with socket.create_connection((LOCALHOST, srv.port), timeout=3) as c:  # connect shortcut
        first = c.recv(3)  # ask for only 3 bytes
        print("recv(3) returned exactly:", first, "(partial data of 'AAAA')")
        rest = b""
        while len(first + rest) < 8:  # a loop is REQUIRED: one recv may not be enough
            rest += c.recv(100)
        print("all bytes joined:", first + rest, "<- the two sends' boundary is gone")

# A length-prefix framing helper: [4-byte big-endian length][payload]
# struct.pack("!I", n): "!" = network byte order (big-endian), "I" = unsigned 4-byte int.


def send_msg(sock, payload):
    sock.sendall(struct.pack("!I", len(payload)) + payload)


def recv_exact(sock, n):
    """Read exactly n bytes, looping because recv() may return less."""
    chunks = []
    remaining = n
    while remaining:
        chunk = sock.recv(min(remaining, 65536))
        if not chunk:
            raise ConnectionError("connection closed in the middle of a message")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_msg(sock):
    (length,) = struct.unpack("!I", recv_exact(sock, 4))
    if length > 10_000_000:  # never trust a length from the network without a cap
        raise ValueError("message too large")
    return recv_exact(sock, length)


def shout_handler(conn):
    """Framed server: read one framed message, reply with it upper-cased, until the client leaves."""
    while True:
        try:
            msg = recv_msg(conn)
        except ConnectionError:
            return
        send_msg(conn, msg.upper())


print("\nframed messages (length-prefix):")
with TcpServerThread(shout_handler) as srv:
    with socket.create_connection((LOCALHOST, srv.port), timeout=3) as c:
        for message in (b"first", b"", b"x" * 200_000):  # includes empty and a big one
            send_msg(c, message)
            reply = recv_msg(c)
            print(f"  sent {len(message):>6} bytes -> got {len(reply):>6} bytes back, uppercased ok: {reply == message.upper()}")

# 04. Timeouts: settimeout() and socket.timeout
# ------------------------------------
# - By default socket calls BLOCK forever. A silent peer would hang your program.
# - settimeout(seconds) makes recv/accept/connect raise socket.timeout
#   (an alias of TimeoutError from Python 3.10) when nothing happens in time.
# - ALWAYS set a timeout on network code. This is the number-one production habit.
print("\n# 04. settimeout() and socket.timeout")


def silent_handler(conn):
    time.sleep(0.6)  # accepts the connection but never says anything


with TcpServerThread(silent_handler) as srv:
    with socket.create_connection((LOCALHOST, srv.port), timeout=3) as c:
        c.settimeout(0.2)
        start = time.monotonic()
        try:
            c.recv(10)
        except socket.timeout:
            print("recv timed out after ~%.1fs instead of hanging forever" % (time.monotonic() - start))

# 05. UDP - Datagrams on Localhost
# ------------------------------------
# - No listen/accept/connect. bind() a socket, then sendto(data, address) and
#   recvfrom(size) -> (data, sender_address).
# - Message BOUNDARIES ARE KEPT: one sendto = one recvfrom (unlike TCP).
# - No delivery guarantee. On localhost it behaves, over a real network
#   packets can vanish, so protocols on UDP add their own retries/timeouts.
print("\n# 05. UDP send/recv")
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_server, \
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_client:
    udp_server.bind((LOCALHOST, 0))
    udp_server.settimeout(2)
    udp_client.settimeout(2)
    server_addr = udp_server.getsockname()
    udp_client.sendto(b"ping 1", server_addr)
    udp_client.sendto(b"ping 2", server_addr)
    for _ in range(2):
        data, sender = udp_server.recvfrom(1024)  # each datagram arrives separately
        print("server received:", data)
        udp_server.sendto(data.replace(b"ping", b"pong"), sender)  # reply to whoever sent it
    reply, _ = udp_client.recvfrom(1024)
    print("client received first reply:", reply)

# 06. Names and Addresses without Touching the Internet
# ------------------------------------
# - getaddrinfo(host, port) turns a name into connectable address tuples.
#   For "localhost" it only reads the local hosts file - no external DNS.
# - gethostname() is just this machine's own name (we only show that it works).
# - IPv4 (127.0.0.1) vs IPv6 (::1): "localhost" may resolve to both.
print("\n# 06. getaddrinfo / gethostname (local only)")
infos = socket.getaddrinfo("localhost", 80, proto=socket.IPPROTO_TCP)
families = sorted({socket.AddressFamily(info[0]).name for info in infos})
print("localhost resolves to families:", families)
print("an IPv4 address for localhost:", socket.gethostbyname("localhost"))
print("gethostname() returns a non-empty string:", bool(socket.gethostname()))
print("htons / ntohs byte-order helpers:", socket.htons(1), "->", socket.ntohs(socket.htons(1)))

# 07. socketserver - Let the Library Do the Loop
# ------------------------------------
# - Writing accept loops and threads by hand is repetitive. socketserver gives
#   you a server class (TCPServer, ThreadingTCPServer) and you write only a
#   Handler class with handle().
# - ThreadingTCPServer: one thread per connection, so clients don't wait for each other.
# - StreamRequestHandler adds self.rfile / self.wfile (file-like objects) so
#   you can read LINES instead of juggling recv().
print("\n# 07. socketserver.ThreadingTCPServer")


class UpperHandler(socketserver.StreamRequestHandler):
    timeout = 3  # socket timeout for each connection

    def handle(self):
        for line in self.rfile:  # one line per iteration, framing by newline
            self.wfile.write(line.strip().upper() + b"\n")


class ReusableThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True  # SO_REUSEADDR
    daemon_threads = True  # handler threads must not keep the process alive


with ReusableThreadingTCPServer((LOCALHOST, 0), UpperHandler) as tcp_server:
    port = tcp_server.server_address[1]
    thread = threading.Thread(target=tcp_server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
    thread.start()

    def ask(word):  # three clients at once, to show threading
        with socket.create_connection((LOCALHOST, port), timeout=3) as c:
            c.sendall(word.encode() + b"\n")
            answers.append(c.makefile("rb").readline().strip().decode())

    answers = []
    clients = [threading.Thread(target=ask, args=(w,)) for w in ("alpha", "beta", "gamma")]
    for t in clients:
        t.start()
    for t in clients:
        t.join(timeout=5)
    print("three concurrent clients got:", sorted(answers))
    tcp_server.shutdown()  # stops serve_forever (call from a DIFFERENT thread than the loop)
    thread.join(timeout=5)
# leaving the `with` closed the server socket (server_close)

# 08. selectors - One Thread, Many Sockets (brief)
# ------------------------------------
# - A selector asks the OS "which of these sockets are ready to read/write RIGHT NOW?"
#   so one thread can serve thousands of connections without blocking on any.
#   This is what asyncio and most high-performance servers do underneath.
# - Demo with socket.socketpair(): two connected sockets, no ports needed.
print("\n# 08. selectors (readiness)")
left, right = socket.socketpair()
with left, right, selectors.DefaultSelector() as sel:
    sel.register(right, selectors.EVENT_READ, data="the right socket")
    print("before sending, ready sockets:", len(sel.select(timeout=0.1)))
    left.sendall(b"wake up")
    for key, _events in sel.select(timeout=1):
        print("now ready:", key.data, "->", key.fileobj.recv(100))

# ====================================================================
# HTTP LAYER
# ====================================================================

# 09. A Tiny HTTP Server with http.server
# ------------------------------------
# - HTTP = text on top of TCP. Request: "GET /path HTTP/1.1" + headers + optional body.
#   Response: "HTTP/1.1 200 OK" + headers + body.
# - Status codes: 2xx success (200 OK, 201 Created), 3xx redirect,
#   4xx the CLIENT made a mistake (400 bad request, 404 not found, 413 too large),
#   5xx the SERVER failed (500, 503 unavailable).
# - BaseHTTPRequestHandler: write do_GET / do_POST methods; they read self.path,
#   self.headers, self.rfile and write with send_response/send_header/end_headers/wfile.
# - ThreadingHTTPServer handles each request in its own thread.
# - http.server is fine for demos, tests and tiny internal tools. For production
#   use a real framework (Flask, FastAPI, Django) behind a real server (gunicorn, uvicorn).
# - Override log_message to silence the default one-line-per-request stderr logging.
print("\n# 09. http.server with a JSON route and a 404 route")

MAX_BODY = 1_000_000  # never read an unbounded body from the network


class Handler(BaseHTTPRequestHandler):
    server_version = "DemoServer/1.0"
    sys_version = ""  # don't advertise the Python version in the Server header

    def log_message(self, format, *args):  # noqa: A002 - name fixed by the base class
        pass  # silence request logging

    def _send_json(self, status, obj):
        body = json.dumps(obj).encode("utf-8")
        try:
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))  # client needs this to know where the body ends
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass  # the client gave up (e.g. its timeout fired) - normal in real life

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        query = urllib.parse.parse_qs(parsed.query)
        if parsed.path == "/api/hello":
            name = query.get("name", ["world"])[0]
            # NOTE: the Host header is chosen by the CLIENT; we only echo it to demonstrate that.
            self._send_json(200, {"message": f"Hello, {name}!", "host_seen": self.headers.get("Host", "").split(":")[0]})  # port stripped: it changes every run
        elif parsed.path == "/api/slow":
            time.sleep(0.6)
            self._send_json(200, {"slow": True})
        elif parsed.path == "/api/flaky":
            self.server.flaky_calls += 1
            if self.server.flaky_calls <= 2:
                self._send_json(503, {"error": "temporarily unavailable"})
            else:
                self._send_json(200, {"ok": True, "after_calls": self.server.flaky_calls})
        else:
            self._send_json(404, {"error": "not found", "path": parsed.path})

    def do_POST(self):
        if self.path != "/api/echo":
            self._send_json(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._send_json(411, {"error": "Content-Length required"})
            return
        if length > MAX_BODY:
            self._send_json(413, {"error": "body too large"})
            return
        raw = self.rfile.read(length)
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "body is not valid JSON"})  # validate input; never crash on it
            return
        self._send_json(201, {"received": payload, "type": type(payload).__name__})


class QuietServer(ThreadingHTTPServer):
    daemon_threads = True  # request threads never block interpreter exit
    flaky_calls = 0

    def handle_error(self, request, client_address):
        if isinstance(sys.exc_info()[1], ConnectionError):
            return  # client hung up; not worth a traceback
        super().handle_error(request, client_address)


http_server = QuietServer((LOCALHOST, 0), Handler)  # bound to localhost ONLY - see security notes below
http_port = http_server.server_address[1]
http_thread = threading.Thread(target=http_server.serve_forever, kwargs={"poll_interval": 0.05}, daemon=True)
http_thread.start()
BASE = f"http://{LOCALHOST}:{http_port}"
print("HTTP server started on localhost, ephemeral port:", http_port > 0)

try:
    # 10. urllib.request.urlopen - the Simplest Client
    # ------------------------------------
    # - urlopen(url, timeout=...) returns a response object (a context manager).
    # - response.status (200), .reason, .headers, .read() -> bytes (decode it!).
    # - It RAISES HTTPError for 4xx/5xx instead of returning, and URLError when
    #   the connection itself fails. (Unlike `requests`, which returns the response.)
    print("\n# 10. urllib.request.urlopen (GET)")
    with urllib.request.urlopen(f"{BASE}/api/hello?name=Asha", timeout=3) as resp:
        body = resp.read()
        print("status       :", resp.status, resp.reason)
        print("Content-Type :", resp.headers["Content-Type"])
        print("getheader    :", resp.getheader("Content-Length"), "bytes (same as len(body):", len(body), ")")
        data = json.loads(body)  # bytes -> dict
        print("parsed JSON  :", data["message"])

    # 11. urllib.request.Request - Headers and a POST JSON Body
    # ------------------------------------
    # - Request(url, data=bytes, headers={...}, method="POST") builds a request.
    # - data must be BYTES. Setting Content-Type: application/json tells the
    #   server how to read it. Passing data= makes it a POST automatically.
    print("\n# 11. Request with headers and a POST JSON body")
    payload = {"user": "debanjan", "tags": ["python", "net"], "n": 3}
    req = urllib.request.Request(
        f"{BASE}/api/echo",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Accept": "application/json", "User-Agent": "learning-script/1.0"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=3) as resp:
        answer = json.loads(resp.read())
        print("status      :", resp.status, "(201 Created)")
        print("round trip  :", answer["received"] == payload, "| server saw type:", answer["type"])

    # 12. http.client - the Lower-Level Client
    # ------------------------------------
    # - urllib is built on http.client. Use it directly when you want a persistent
    #   connection, full control of headers, or to see raw status/headers.
    # - Always read the response body (or close) before reusing the connection.
    print("\n# 12. http.client.HTTPConnection")
    conn = http.client.HTTPConnection(LOCALHOST, http_port, timeout=3)
    try:
        conn.request("GET", "/api/hello?name=Bob", headers={"Accept": "application/json"})
        r = conn.getresponse()
        print("status, reason :", r.status, r.reason)
        print("headers (some) :", r.getheader("Content-Type"), "|", r.getheader("Server"))
        print("missing header :", r.getheader("X-Not-There", "default-value"))
        print("body           :", json.loads(r.read()))
        r.close()
    finally:
        conn.close()

    conn = http.client.HTTPConnection(LOCALHOST, http_port, timeout=3)
    try:
        body = json.dumps([1, 2, 3])
        conn.request("POST", "/api/echo", body=body, headers={"Content-Type": "application/json"})
        r = conn.getresponse()
        print("POST via http.client ->", r.status, json.loads(r.read()))
    finally:
        conn.close()

    # 13. HTTPError and URLError
    # ------------------------------------
    # - HTTPError: the server answered, but with 4xx/5xx. It IS ALSO a response:
    #   err.code, err.reason, err.headers, err.read() (the error body).
    # - URLError: no answer at all - connection refused, DNS failure, timeout.
    #   err.reason holds the underlying exception.
    # - HTTPError is a SUBCLASS of URLError, so catch HTTPError FIRST.
    print("\n# 13. HTTPError and URLError")
    try:
        urllib.request.urlopen(f"{BASE}/nope", timeout=3)
    except urllib.error.HTTPError as err:
        print("HTTPError  :", err.code, err.reason, "| body:", json.loads(err.read()))
    except urllib.error.URLError as err:
        print("URLError   :", err.reason)

    # A closed port: grab a free port, close the socket, then try to connect to it.
    with socket.socket() as probe:
        probe.bind((LOCALHOST, 0))
        closed_port = probe.getsockname()[1]
    try:
        urllib.request.urlopen(f"http://{LOCALHOST}:{closed_port}/", timeout=3)
    except urllib.error.HTTPError as err:
        print("unexpected HTTPError", err.code)
    except urllib.error.URLError as err:
        print("URLError   : connection refused ->", isinstance(err.reason, ConnectionRefusedError))

    # Timeouts: the /api/slow route sleeps 0.6s, we only wait 0.2s.
    try:
        urllib.request.urlopen(f"{BASE}/api/slow", timeout=0.2)
    except (urllib.error.URLError, socket.timeout) as err:
        reason = getattr(err, "reason", err)
        print("slow route : timed out ->", isinstance(reason, socket.timeout))

    # Input validation on the server side: bad JSON gets a clean 400, not a crash.
    bad = urllib.request.Request(f"{BASE}/api/echo", data=b"{not json", method="POST",
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(bad, timeout=3)
    except urllib.error.HTTPError as err:
        print("bad JSON   :", err.code, json.loads(err.read()))

    # 14. urllib.parse - Take URLs Apart and Build Them Safely
    # ------------------------------------
    # - Never build URLs with string concatenation: spaces, &, =, ?, # and non-ASCII
    #   characters in values would corrupt the URL (or let a user inject extra parameters).
    # - urlparse / urlsplit  -> named pieces (scheme, netloc, path, query, fragment)
    #   (urlsplit skips the rarely used ";params" part)
    # - urlunparse           -> pieces back to a string
    # - urlencode            -> dict to "a=1&b=2" with proper escaping
    # - parse_qs             -> query string to dict of LISTS (a key can repeat)
    # - quote / unquote      -> percent-encode one piece (quote keeps "/" unless safe="")
    # - urljoin              -> resolve a relative link against a base
    print("\n# 14. urllib.parse")
    url = "https://user@example.com:8443/docs/page.html?lang=en&tag=a&tag=b#section-2"
    parts = urllib.parse.urlparse(url)
    print("scheme  :", parts.scheme)
    print("netloc  :", parts.netloc, "| hostname:", parts.hostname, "| port:", parts.port, "| username:", parts.username)
    print("path    :", parts.path)
    print("query   :", parts.query, "| fragment:", parts.fragment)
    print("urlsplit:", urllib.parse.urlsplit(url).path)
    print("parse_qs:", urllib.parse.parse_qs(parts.query))
    print("rebuilt :", urllib.parse.urlunparse(parts._replace(query="lang=bn", fragment="")))

    params = {"q": "python & sockets = fun?", "page": 2, "name": "Debanjan Mondal", "city": "Kolkata/Howrah"}
    query = urllib.parse.urlencode(params)
    print("urlencode:", query)
    print("safe URL :", f"http://localhost:PORT/api/hello?{urllib.parse.urlencode({'name': 'A&B C'})}")
    print("quote    :", urllib.parse.quote("a b/c?d"), "| safe='':", urllib.parse.quote("a b/c?d", safe=""))
    print("unquote  :", urllib.parse.unquote("a%20b%2Fc"))
    print("repeated keys with doseq:", urllib.parse.urlencode({"tag": ["a", "b"]}, doseq=True))
    print("urljoin  :", urllib.parse.urljoin("https://example.com/a/b/c.html", "../d.html"))
    print("urljoin  :", urllib.parse.urljoin("https://example.com/a/", "https://other.example/x"),
          "<- an absolute second argument REPLACES the base (don't join untrusted input blindly)")

    # 15. JSON API Round-Trip
    # ------------------------------------
    # - The everyday pattern: build dict -> json.dumps -> bytes -> send;
    #   receive bytes -> json.loads -> dict. See 04-Json-And-Csv.py for JSON itself.
    print("\n# 15. JSON API round-trip helper")

    def call_api(method, path, body=None, timeout=3):
        data = None if body is None else json.dumps(body).encode()
        request = urllib.request.Request(f"{BASE}{path}", data=data, method=method,
                                         headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.status, json.loads(response.read())

    print("GET :", call_api("GET", "/api/hello?name=Chitra"))
    print("POST:", call_api("POST", "/api/echo", {"items": [1, 2, 3], "ok": True}))

    # 16. Timeouts and Retries with Backoff - THE Production Habit
    # ------------------------------------
    # - Networks are unreliable. Every call needs (1) a timeout and (2) a retry
    #   policy for TRANSIENT failures (timeouts, connection errors, 502/503/504).
    # - Backoff: wait longer after each failure (0.05, 0.1, 0.2 ...), often with
    #   random "jitter", so a struggling server isn't hammered by everyone at once.
    # - Do NOT retry 4xx errors: the request itself is wrong and will fail again.
    # - Only retry operations that are safe to repeat (GET, or POST made idempotent).
    print("\n# 16. Retry with exponential backoff")

    def get_with_retries(url, attempts=4, timeout=1.0, base_delay=0.05):
        for attempt in range(1, attempts + 1):
            try:
                with urllib.request.urlopen(url, timeout=timeout) as response:
                    print(f"  attempt {attempt}: HTTP {response.status}")
                    return json.loads(response.read())
            except urllib.error.HTTPError as err:
                print(f"  attempt {attempt}: HTTP {err.code}")
                if err.code < 500:
                    raise  # client error: retrying won't help
            except (urllib.error.URLError, socket.timeout) as err:
                print(f"  attempt {attempt}: network problem ({type(getattr(err, 'reason', err)).__name__})")
            if attempt == attempts:
                raise RuntimeError(f"giving up after {attempts} attempts")
            time.sleep(base_delay * 2 ** (attempt - 1))

    print("flaky endpoint (fails twice with 503, then works):")
    print("  final answer:", get_with_retries(f"{BASE}/api/flaky"))

    print("a 404 is NOT retried:")
    try:
        get_with_retries(f"{BASE}/missing")
    except urllib.error.HTTPError as err:
        print("  raised immediately:", err.code)

    # 17. Security Notes (Host header demo)
    # ------------------------------------
    # - NEVER bind a server to "0.0.0.0" (all network interfaces) casually: it
    #   makes your dev server reachable from the whole network (café wifi!).
    #   Bind to 127.0.0.1 unless you really mean to expose it - and then add
    #   authentication and TLS.
    # - Validate ALL input: JSON shape, sizes (we cap the body), numbers, paths.
    #   Reject with 400/413 rather than crashing or trusting it.
    # - Don't trust the Host header (or any header): the client writes them. Using
    #   it to build links, password-reset URLs or cache keys enables "Host header
    #   attacks". Use a configured allow-list of hostnames.
    # - Never put secrets (tokens, passwords) in URLs/query strings: they end up in logs.
    # - Don't disable certificate verification to "make HTTPS work".
    print("\n# 17. Security: the Host header is attacker-controlled")
    conn = http.client.HTTPConnection(LOCALHOST, http_port, timeout=3)
    try:
        conn.putrequest("GET", "/api/hello", skip_host=True)
        conn.putheader("Host", "evil.example")  # a client can claim to be anything
        conn.endheaders()
        print("server saw Host =", json.loads(conn.getresponse().read())["host_seen"], "<- never trust it")
    finally:
        conn.close()
    print("our server is bound to:", http_server.server_address[0], "(localhost only), not 0.0.0.0")
finally:
    # Always shut down: stop the loop, close the listening socket, join the thread.
    http_server.shutdown()
    http_server.server_close()
    http_thread.join(timeout=5)
    print("\nHTTP server stopped; thread alive:", http_thread.is_alive())

# 18. The Real World: requests and httpx (printed reference, NOT executed)
# ------------------------------------
# - The standard library clients work but are verbose. Most real projects use
#   the third-party `requests` (simple, sync) or `httpx` (also async, HTTP/2).
#   Install: pip install requests httpx
# - They return the response even for 4xx/5xx (call .raise_for_status()),
#   encode/decode JSON for you, and handle sessions and connection reuse.
print("\n# 18. requests / httpx equivalents (reference only, not run)")
print('''
# urllib (what we did above)              # requests (3 lines)
#   req = Request(url, data=..., ...)       import requests
#   with urlopen(req, timeout=3) as r:      r = requests.post(url, json=payload, timeout=3)
#       json.loads(r.read())                r.raise_for_status(); print(r.json())
#
# httpx (sync or async)
#   import httpx
#   r = httpx.get(url, params={"q": "x"}, timeout=3)
#   r.raise_for_status(); print(r.json())
#
# ALWAYS pass timeout=: requests has NO default timeout (it can hang forever!).
''')

# 19. ssl and HTTPS (printed reference)
# ------------------------------------
# - HTTPS = HTTP wrapped in TLS: encryption (nobody can read it) + authentication
#   (certificate proves you reached the real server) + integrity.
# - urllib and http.client.HTTPSConnection do HTTPS automatically and verify
#   certificates by default. The ssl module is what they use underneath.
# - ssl.create_default_context() gives you safe defaults: verify the certificate
#   chain AND the hostname. We can build one offline and look at it.
# - NEVER use ssl._create_unverified_context() or verify=False in real code:
#   it removes the protection and invites man-in-the-middle attacks.
print("\n# 19. ssl / HTTPS (reference)")
ctx = ssl.create_default_context()
print("verify_mode    :", ctx.verify_mode.name, "(CERT_REQUIRED = certificate must be valid)")
print("check_hostname :", ctx.check_hostname)
print("min TLS version:", ctx.minimum_version.name)
print('''
# How an HTTPS call would look (not executed - needs the internet):
#   import urllib.request
#   with urllib.request.urlopen("https://example.com/", timeout=5) as r:
#       print(r.status)
# Self-signed certificate in a LAN/test? Point to its CA file instead of disabling checks:
#   ctx = ssl.create_default_context(cafile="my-ca.pem")
#   urllib.request.urlopen(url, context=ctx, timeout=5)
''')

# 20. Email: Build with email.message (never sent here)
# ------------------------------------
# - EmailMessage builds a correct email (headers, encoding, attachments).
# - smtplib sends it to a mail server. We only BUILD and PRINT it - there is no
#   mail server on localhost and we never touch the network for this demo.
print("# 20. email.message.EmailMessage (build and print only)")
msg = EmailMessage()
msg["From"] = "learner@example.com"
msg["To"] = "friend@example.com"
msg["Subject"] = "Hello from Python ☃"  # non-ASCII is encoded for you
msg["Date"] = email.utils.formatdate(0, usegmt=True)  # fixed date so output is repeatable
msg["Message-ID"] = "<demo-1@example.com>"
msg.set_content("Plain text body.\nSent from a tutorial.")
msg.add_alternative("<h1>Hello</h1><p>HTML version.</p>", subtype="html")
msg.add_attachment(b"col1,col2\n1,2\n", maintype="text", subtype="csv", filename="data.csv")
print("is_multipart :", msg.is_multipart())
print("part types   :", [part.get_content_type() for part in msg.walk()])
print("Subject      :", msg["Subject"])
print("first lines of the wire format:")
for line in msg.as_string().splitlines()[:6]:
    print("  ", line)
print('''
# Sending it (reference, not executed):
#   import smtplib
#   with smtplib.SMTP("smtp.example.com", 587, timeout=10) as s:
#       s.starttls(context=ssl.create_default_context())   # upgrade to encrypted
#       s.login(user, app_password)                        # secrets from env vars, never in code
#       s.send_message(msg)
''')

# 21. Cleanup Checklist and Summary
# ------------------------------------
# - Every socket: closed (use `with`). Every server: shutdown() then server_close().
#   Every thread: daemon=True or joined. Every call: a timeout.
# - Choosing a layer:
#     raw socket        custom protocols, learning, tiny tools
#     socketserver      simple servers without hand-written accept loops
#     http.server       throwaway/local HTTP; frameworks for real services
#     urllib/http.client  dependency-free HTTP clients; requests/httpx for comfort
print("\n# 21. Summary")
leftover = [t.name for t in threading.enumerate() if t is not threading.main_thread() and not t.daemon]
print("non-daemon helper threads left running:", leftover)
print("remember: timeouts everywhere, bind to 127.0.0.1, validate input, retry only transient errors, close what you open")
