import ast
import difflib
import hashlib
import hmac
import html
import io
import ipaddress
import logging
import math
import os
import re
import secrets
import shlex
import sqlite3
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import urlparse

# 01. Security Basics - Introduction and threat model
# ------------------------------------
# - Security is not a feature you add at the end; it is a habit of asking
#   "what if the input is hostile?" while you write each function.
# - THREAT MODEL in plain words - four questions:
#     1. What are we protecting?      (passwords, personal data, the server itself)
#     2. Who might attack it?         (strangers on the internet, a curious user, a bad dependency)
#     3. Where can they get in?       (every place data ENTERS the program)
#     4. What happens if they do?     (decides how much effort a defence deserves)
# - TRUST BOUNDARY = the line between code you control and the outside world.
#   EVERYTHING that crosses it is UNTRUSTED INPUT until validated:
#       form fields, URL parts, headers, cookies, uploaded files and their NAMES,
#       JSON/XML bodies, command-line args, environment variables, files on disk,
#       database rows written by someone else, responses from other services.
# - Principles used all file long:
#     * validate input at the boundary (allow-lists, not deny-lists)
#     * use safe APIs that separate CODE from DATA (parameterized queries, arg lists)
#     * least privilege (give code and users only what they need)
#     * defence in depth (several cheap layers beat one perfect one)
#     * fail safe and fail quietly to users (log details privately)
# - Every demo below is HARMLESS: payloads only print text, files live in a
#   temp folder, nothing touches the network.

print("# 01. Security Basics - Introduction")
print("# ------------------------------------")

TMP_HOLDER = tempfile.TemporaryDirectory()
TMP = Path(TMP_HOLDER.name).resolve()
ENV = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")

# 02. eval() / exec() on user input = remote code execution
# ------------------------------------
# - eval(text) RUNS text as Python. If an outsider controls the text, they
#   control your program. The "payload" below only prints a line - a real
#   attacker would read files or delete things instead.
# - Fix: do not evaluate input. For literals use ast.literal_eval (accepts
#   only numbers, strings, lists, dicts, tuples, sets, booleans, None). For
#   arithmetic, walk the syntax tree and allow only operators you list.
# - eval(text, {"__builtins__": {}}) is NOT a sandbox; see below.

print("\n# 02. eval() on user input")
user_text = "[print('!! attacker code ran inside our program'), 42][1]"
result = eval(user_text)  # noqa: S307  <- deliberately unsafe demo
print("  eval(user_text) returned:", result, "<- and the print above proves code executed")

try:
    ast.literal_eval(user_text)
except ValueError as exc:
    print("  ast.literal_eval(user_text) -> rejected:", type(exc).__name__)
print("  ast.literal_eval('[1, 2, {\"a\": None}]') ->", ast.literal_eval('[1, 2, {"a": None}]'))

escape = "().__class__.__base__.__subclasses__()[0] is not None"
print("  'empty builtins' (no len/print/open) yet attribute chain still works:", eval(escape, {"__builtins__": {}}))
print("  -> reaching every class in the interpreter via attributes; real exploits chain from here.")

ALLOWED_OPS = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
               ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b}


def safe_calc(expression):
    """Evaluate +, -, *, / on numbers only. Anything else is rejected."""
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in ALLOWED_OPS:
            return ALLOWED_OPS[type(node.op)](walk(node.left), walk(node.right))
        raise ValueError(f"not allowed: {type(node).__name__}")
    return walk(ast.parse(expression, mode="eval"))


print("  safe_calc('2 + 3 * 4') ->", safe_calc("2 + 3 * 4"))
try:
    safe_calc("__import__('os').getcwd()")
except ValueError as exc:
    print("  safe_calc(attack)      -> ValueError:", exc)
print("# - The same applies to exec(), compile(), and 'pd.eval'/'df.query' on raw user text.")

# 03. Unsafe deserialization: pickle and yaml.load
# ------------------------------------
# - pickle can rebuild ANY object, and an object may say "when you unpickle me,
#   call this function". So pickle.loads(untrusted_bytes) is code execution,
#   exactly like eval. The runnable demo is in
#   "06-Standard Library/16-Serialization-And-Config.py" - not repeated here.
#   Rule: unpickle only data YOU produced and nobody else can modify (and sign it
#   with hmac if it crosses a boundary). For data from others use JSON.
# - YAML has the same trap: yaml.load(text) with the full loader can build
#   Python objects (tags like !!python/object/apply:...). Always yaml.safe_load.

print("\n# 03. pickle / yaml (reference + one safe check)")
print("  pickle.loads(untrusted)   -> NEVER.  Use json for data from outside.")
print("  yaml.load(text)           -> avoid.  Use yaml.safe_load(text).")
try:
    import yaml

    try:
        yaml.safe_load('!!python/object/apply:builtins.print ["would run code"]')
    except yaml.YAMLError as exc:
        print("  yaml.safe_load(python tag) -> refused:", type(exc).__name__)
except ImportError:
    print("  (PyYAML not installed - skipping the yaml.safe_load check)")

# 04. SQL injection
# ------------------------------------
# - Building SQL by gluing strings lets the input change the QUERY's meaning.
#   Fix: parameterized queries - the database receives code and data separately.
# - You cannot bind table/column NAMES as parameters; for those, choose from an
#   allow-list. Fuller treatment: "06-Standard Library/17-Sqlite3.py".

print("\n# 04. SQL injection (in-memory sqlite)")
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE users (name TEXT, role TEXT)")
db.executemany("INSERT INTO users VALUES (?, ?)", [("asha", "admin"), ("raj", "user"), ("mira", "user")])
attack = "nobody' OR '1'='1"

glued = f"SELECT name FROM users WHERE name = '{attack}'"
print("  glued SQL :", glued)
print("  rows      :", [r[0] for r in db.execute(glued)], "<- every user leaked")
rows = db.execute("SELECT name FROM users WHERE name = ?", (attack,)).fetchall()
print("  with '?'  :", rows, "<- the text is just a (non-existent) name")

SORTABLE = {"name", "role"}  # identifiers: allow-list, never parameters


def users_sorted_by(column):
    if column not in SORTABLE:
        raise ValueError(f"cannot sort by {column!r}")
    return [r[0] for r in db.execute(f"SELECT name FROM users ORDER BY {column}")]


print("  ORDER BY via allow-list:", users_sorted_by("name"))
try:
    users_sorted_by("name; DROP TABLE users")
except ValueError as exc:
    print("  attack column ->", exc)
db.close()

# 05. Command injection
# ------------------------------------
# - shell=True hands the whole string to a shell, where ; | && $( ) ` are
#   operators. Input containing them adds NEW commands.
# - Fix 1: pass a LIST and no shell - each item is one literal argument.
# - Fix 2: if you truly need a shell, shlex.quote() every piece of input.
# - Better still: validate against an allow-list first.
# - (Demo uses 'echo'; skipped on Windows where the shell differs.)

print("\n# 05. Command injection")
if os.name == "posix":
    name = "report.txt; echo INJECTED-SECOND-COMMAND"
    bad = subprocess.run(f"echo file: {name}", shell=True, capture_output=True, text=True, timeout=10)
    print("  shell=True + f-string :", bad.stdout.strip().splitlines(), "<- second command ran")
    good = subprocess.run(["echo", "file:", name], capture_output=True, text=True, timeout=10)
    print("  list args, no shell   :", good.stdout.strip().splitlines())
    quoted = subprocess.run(f"echo file: {shlex.quote(name)}", shell=True, capture_output=True, text=True, timeout=10)
    print("  shlex.quote + shell   :", quoted.stdout.strip().splitlines())
    print("  shlex.quote(name)     :", shlex.quote(name))
else:
    print("  (skipped: POSIX shell demo)")
print("# - Same family: os.system(), os.popen(), and f-string'd 'git ...' calls.")

# 06. Path traversal, symlinks, zip/tar slip
# ------------------------------------
# - A user-supplied filename like "../../etc/passwd" climbs OUT of the folder
#   you meant to serve. Absolute paths ("/etc/passwd") replace your base
#   entirely when joined: Path("base") / "/etc/passwd" == "/etc/passwd".
# - Fix: resolve the final path (this follows symlinks and removes '..'),
#   then check it is still INSIDE the base: Path.is_relative_to (3.9+).
# - Do NOT 'sanitize' by stripping '../' - "....//" becomes "../" after one pass.

BASE = TMP / "uploads"
BASE.mkdir()
(BASE / "report.txt").write_text("public report")
(TMP / "secret.txt").write_text("TOP SECRET (outside the uploads folder)")


def safe_join(base, user_name):
    base = Path(base).resolve()
    target = (base / user_name).resolve()
    if not target.is_relative_to(base):
        raise PermissionError(f"path escapes base folder: {user_name!r}")
    return target


print("\n# 06. Path traversal")
print("  naive join:", (BASE / "../secret.txt").resolve().name, "-> reads", (BASE / "../secret.txt").resolve().read_text()[:10] + "...")
for candidate in ["report.txt", "docs/../report.txt", "../secret.txt", "/etc/passwd", "a/../../secret.txt"]:
    try:
        print(f"  safe_join({candidate!r:22}) -> OK  {safe_join(BASE, candidate).relative_to(BASE)}")
    except PermissionError as exc:
        print(f"  safe_join({candidate!r:22}) -> BLOCKED ({exc})")

# - Symlinks: a link INSIDE the base that points OUTSIDE. resolve() follows it,
#   so the same check catches it.
try:
    os.symlink(TMP / "secret.txt", BASE / "innocent.txt")
    try:
        safe_join(BASE, "innocent.txt")
    except PermissionError as exc:
        print("  symlink inside base pointing outside -> BLOCKED:", exc)
except OSError:
    print("  (symlinks not permitted here - skipped)")

print("# - TOCTOU (time-of-check, time-of-use): between 'check' and 'open' an attacker")
print("#   can swap the file for a symlink. Prefer ONE atomic operation: open(...) and")
print("#   handle errors, os.open(..., O_NOFOLLOW), or create with mode 'x' (below).")
try:
    (BASE / "once.txt").write_text("first")
    with open(BASE / "once.txt", "x"):
        pass
except FileExistsError:
    print("  open(path, 'x') -> FileExistsError: creation is atomic, no check-then-create race")

# - Archive slip: archive member names are also untrusted.
members = {"good.txt": b"fine", "../evil.txt": b"would land outside the folder"}
buf = io.BytesIO()
with zipfile.ZipFile(buf, "w") as z:
    for member, data in members.items():
        z.writestr(member, data)
dest = TMP / "unzipped"
dest.mkdir()
with zipfile.ZipFile(io.BytesIO(buf.getvalue())) as z:
    for info in z.infolist():
        try:
            safe_join(dest, info.filename)
            verdict = "ok"
        except PermissionError:
            verdict = "REJECTED (zip slip)"
        print(f"  zip member {info.filename!r:16} -> {verdict}")

tbuf = io.BytesIO()
with tarfile.open(fileobj=tbuf, mode="w") as t:
    for member, data in members.items():
        ti = tarfile.TarInfo(member)
        ti.size = len(data)
        t.addfile(ti, io.BytesIO(data))
tdest = TMP / "untarred"
tdest.mkdir()
try:
    with tarfile.open(fileobj=io.BytesIO(tbuf.getvalue())) as t:
        t.extractall(tdest, filter="data")  # 3.12+: 'data' filter blocks escapes
except tarfile.TarError as exc:
    print("  tar extractall(filter='data') ->", type(exc).__name__)
print("  files in tar dest:", sorted(p.name for p in tdest.iterdir()), "| evil.txt outside?", (TMP / "evil.txt").exists())
print("# - tarfile: ALWAYS pass filter='data' (default becomes strict in Python 3.14).")

# 07. Safe temporary files
# ------------------------------------
# - A predictable name like /tmp/myapp.tmp lets another local user pre-create
#   it (or a symlink with that name) and read/redirect your data.
# - tempfile creates files with an unpredictable name, atomically, with mode
#   0600 (owner only). Never use the old tempfile.mktemp() (name only, racy).

print("\n# 07. Safe temp files")
fd, tmp_name = tempfile.mkstemp(prefix="app-", suffix=".tmp", dir=TMP)
os.close(fd)
mode = oct(os.stat(tmp_name).st_mode & 0o777)
print("  mkstemp mode:", mode, "(owner read/write only);  name looks like", re.sub(r"[a-z0-9_]{8}", "XXXXXXXX", Path(tmp_name).name))
with tempfile.TemporaryDirectory(dir=TMP) as scratch:
    print("  TemporaryDirectory exists inside with-block:", Path(scratch).is_dir())
print("  ...and is deleted afterwards:", not Path(scratch).exists())

# 08. Input validation: allow-lists, limits, Unicode, resource exhaustion
# ------------------------------------
# - ALLOW-LIST: define what is valid and reject the rest. A deny-list
#   ("block <script>") always misses a variant you did not think of.
# - Check type, length, range, and format - in that order, cheapest first.
# - re.fullmatch() demands the WHOLE string match. re.match() only checks the
#   start, and '$' also matches just before a trailing newline!

print("\n# 08. Input validation")
USERNAME = re.compile(r"[a-z][a-z0-9_]{2,19}")  # 3-20 chars, starts with a letter


def valid_username(value):
    return isinstance(value, str) and len(value) <= 64 and USERNAME.fullmatch(value) is not None


for value in ["asha_92", "ab", "9lives", "asha\n", "a" * 100, None]:
    print(f"  valid_username({value!r:12.12}) -> {valid_username(value)}")
print("  re.match(r'^[a-z]+$', 'abc\\n') ->", bool(re.match(r"^[a-z]+$", "abc\n")), "<- '$' lets a newline through")
print("  re.fullmatch(r'[a-z]+', 'abc\\n') ->", bool(re.fullmatch(r"[a-z]+", "abc\n")))

# - Range checks on numbers (also reject NaN, which is not equal to itself):
def valid_quantity(text):
    try:
        qty = int(text)
    except (TypeError, ValueError):
        return False
    return 1 <= qty <= 1000


print("  valid_quantity:", {t: valid_quantity(t) for t in ["5", "0", "-3", "1e3", "99999", "abc"]})
print("  float('nan') == float('nan') ->", float("nan") == float("nan"), "| math.isnan check needed for floats")

# - Unicode pitfalls
arabic = "١٢٣"  # Arabic-Indic digits 1 2 3
print("\n  Unicode: '١٢٣'.isdigit() ->", arabic.isdigit(), "| int() ->", int(arabic),
      "| re.fullmatch(r'[0-9]+') ->", bool(re.fullmatch(r"[0-9]+", arabic)))
print("  -> \\d and isdigit() accept non-ASCII digits. Use [0-9] or re.ASCII when you mean 0-9.")
latin, cyrillic = "admin", "аdmin"  # second starts with CYRILLIC small a
print("  homoglyph: 'admin' == 'аdmin' ->", latin == cyrillic, "| they LOOK the same;",
      "first char of 2nd is", unicodedata.name(cyrillic[0]))
print("  fix: require ASCII usernames -> 'аdmin'.isascii() is", cyrillic.isascii(), "-> reject it")
print("  NFKC: 'ﬁle' ->", unicodedata.normalize("NFKC", "ﬁle"), "| casefold('Straße') ->", "Straße".casefold())
print("  -> normalize (NFKC) and casefold BEFORE comparing or storing usernames/emails,")
print("     or 'ADMIN' and 'admin'/'ａdmin' become different accounts.")

# - Resource exhaustion: no integer overflow in Python, but huge inputs eat CPU/RAM.
print("\n  Python int has no overflow, but str->int is limited:", sys.get_int_max_str_digits(), "digits")
try:
    int("9" * 5000)
except ValueError as exc:
    print("  int('9'*5000) ->", str(exc)[:60] + "...")


def read_limited(stream, max_bytes):
    data = stream.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise ValueError(f"input larger than {max_bytes} bytes")
    return data


try:
    read_limited(io.BytesIO(b"x" * 5000), 1024)
except ValueError as exc:
    print("  read_limited ->", exc, "(cap size BEFORE parsing/decompressing/loading)")
print("# - Also cap: upload size, JSON nesting, number of items, decompressed size, timeouts.")

# 09. ReDoS - catastrophic regex backtracking
# ------------------------------------
# - A regex with nested repetition, like (a+)+, can try an EXPONENTIAL number
#   of ways to split the input when the match FAILS at the end. One crafted
#   string then freezes a web server thread (Regular-expression Denial of Service).
# - Below: the failing input is 'aaaa...!' . Each +2 characters multiplies
#   the work ~4x. Sizes are kept tiny and capped so this finishes in well
#   under a second. Exact times vary per machine; the SHAPE is the lesson.

print("\n# 09. ReDoS")
EVIL = re.compile(r"^(a+)+$")
sizes, times = [], []
budget_start = time.perf_counter()
for n in (12, 14, 16, 18, 20):
    sample = "a" * n + "!"
    t0 = time.perf_counter()
    EVIL.match(sample)
    times.append(time.perf_counter() - t0)
    sizes.append(n)
    if time.perf_counter() - budget_start > 0.5:  # hard cap: never let this run long
        print("  (time cap reached, stopping early)")
        break
base = max(times[0], 1e-6)
for n, t in zip(sizes, times):
    doublings = max(0, round(math.log2(max(t / base, 1))))
    print(f"  n={n:>2} chars  work ~ 2^{doublings:<2} x the n={sizes[0]} case  {'#' * doublings}")
print("  -> every +2 characters costs about 4x more. At n=40 this would run for HOURS.")

safe_input = "a" * 50_000 + "!"
t0 = time.perf_counter()
print("  fix 1: ^a+$ on 50,000 chars  ->", bool(re.fullmatch(r"a+", safe_input)), f"(instant: {time.perf_counter() - t0 < 0.5})")
t0 = time.perf_counter()
print("  fix 2: possessive (a++)+ (3.11+) ->", bool(re.fullmatch(r"(a++)+", safe_input)), f"(instant: {time.perf_counter() - t0 < 0.5})")
print("  fix 3: cap input length BEFORE matching (len(text) <= 200), and avoid nested")
print("         quantifiers like (x+)+, (x*)*, (x|x)+, (\\w+\\s?)* applied to user text.")

# 10. assert is NOT validation
# ------------------------------------
# - assert statements are REMOVED when Python runs with -O (optimize), which
#   production setups sometimes use. A security/validation check written as
#   assert silently disappears. assert is for "this can never happen" bugs
#   in YOUR code, not for checking user input. Raise a real exception.

print("\n# 10. assert vs python -O")
code = "def withdraw(amount):\n    assert amount > 0, 'amount must be positive'\n    return 'withdrew ' + str(amount)\nprint(withdraw(-500))\n"
for flag in ([], ["-O"]):
    done = subprocess.run([sys.executable, *flag, "-c", code], capture_output=True, text=True, env=ENV, timeout=30)
    label = "python -O" if flag else "python   "
    last = (done.stderr.strip().splitlines() or [""])[-1] or done.stdout.strip()
    print(f"  {label}: exit {done.returncode} -> {last}")
print("  -> with -O the negative withdrawal sailed through. Use: if amount <= 0: raise ValueError(...)")

# 11. Secrets handling
# ------------------------------------
# - Never hard-code API keys/passwords in source: they end up in git history,
#   screenshots, logs, and every developer's laptop.
# - Read them from the environment (set by the deploy platform / secret
#   manager) or a '.env' file that is listed in .gitignore and never committed.
# - Fail FAST at startup if a required secret is missing - do not fall back to
#   a default password.
# - If a secret leaks: ROTATE it immediately. Deleting the commit is not enough
#   (clones, forks, and caches keep it). Scan with gitleaks/detect-secrets/trufflehog.

print("\n# 11. Secrets handling")
GITIGNORE = ".env\n.env.*\n*.pem\n*.key\nsecrets/\n"
print("  .gitignore must contain:", GITIGNORE.split())
print("  .env.example (committed, no real values):  API_KEY=changeme   DB_URL=postgres://user:pass@host/db")


def load_api_key(environ):
    try:
        return environ["API_KEY"]
    except KeyError:
        raise RuntimeError("API_KEY is not set. Export it or add it to your .env file.") from None


try:
    load_api_key({})
except RuntimeError as exc:
    print("  missing secret ->", exc)
print("  present secret ->", "len", len(load_api_key({"API_KEY": "sk-demo-1234567890"})))

# - Never log or print secrets. A logging.Filter can redact them as a safety net.
TOKEN_PATTERN = re.compile(r"(?i)\b(authorization|token|api[_-]?key|password)\b(\s*[=:]\s*)(\S+)")


class RedactFilter(logging.Filter):
    def filter(self, record):
        message = record.getMessage()
        record.msg = TOKEN_PATTERN.sub(lambda m: f"{m.group(1)}{m.group(2)}[REDACTED]", message)
        record.args = ()
        return True


log = logging.getLogger("secdemo")
log.setLevel(logging.INFO)
log.propagate = False
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("  LOG %(levelname)s %(message)s"))
handler.addFilter(RedactFilter())
log.addHandler(handler)
log.info("calling vendor with api_key=%s for user %s", "sk-live-ABCDEF123456", "asha")
log.info("request headers: Authorization: Bearer-abc.def.ghi")
log.removeHandler(handler)
print("  -> redaction is a safety net; the real fix is never passing secrets to the logger.")

# - Also keep secrets out of repr()/tracebacks:
class Credentials:
    def __init__(self, user, password):
        self.user, self.password = user, password

    def __repr__(self):
        return f"Credentials(user={self.user!r}, password='***')"


print("  repr(Credentials) ->", Credentials("asha", "hunter2"))

# - secrets module: cryptographically secure randomness (see section 13).
print("  secrets.token_urlsafe(16) length:", len(secrets.token_urlsafe(16)), "(random every run, so value not printed)")

# 12. Password storage
# ------------------------------------
# - Never store passwords, and never store a FAST hash (md5, sha1, sha256).
#   Fast = attackers try billions of guesses per second, and identical
#   passwords produce identical hashes (lookup tables).
# - Store a SLOW, SALTED hash made for passwords: scrypt or PBKDF2 (both in
#   hashlib), or - better where you can install it - argon2-cffi / bcrypt.
# - SALT = random bytes unique per user, stored beside the hash; defeats
#   precomputed tables and hides that two users share a password.
# - Compare with hmac.compare_digest (constant time), not '=='. See also
#   "06-Standard Library/15-Hashing-And-Encoding.py".

print("\n# 12. Password storage")
print("  sha256('hunter2') twice  :", hashlib.sha256(b"hunter2").hexdigest()[:16], "==", hashlib.sha256(b"hunter2").hexdigest()[:16], "<- same every time: bad")

SCRYPT_N, SCRYPT_R, SCRYPT_P = 2**14, 8, 1


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, n=SCRYPT_N, r=SCRYPT_R, p=SCRYPT_P, dklen=32)
    return f"scrypt${SCRYPT_N}${SCRYPT_R}${SCRYPT_P}${salt.hex()}${digest.hex()}"


def verify_password(password, stored):
    _, n, r, p, salt_hex, digest_hex = stored.split("$")
    candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt_hex), n=int(n), r=int(r), p=int(p), dklen=32)
    return hmac.compare_digest(candidate, bytes.fromhex(digest_hex))


try:
    h1, h2 = hash_password("hunter2"), hash_password("hunter2")
    print("  scrypt, same password   : hashes differ ->", h1 != h2, "(different random salts)")
    print("  stored format           :", h1.split("$")[0] + "$N$r$p$<salt>$<hash>", "-> parameters travel WITH the hash so you can raise them later")
    print("  verify correct / wrong  :", verify_password("hunter2", h1), "/", verify_password("hunter3", h1))
except (AttributeError, ValueError) as exc:  # scrypt needs OpenSSL support
    print("  (scrypt unavailable here:", exc, "- use hashlib.pbkdf2_hmac)")
t0 = time.perf_counter()
hashlib.pbkdf2_hmac("sha256", b"hunter2", b"0123456789abcdef", 600_000)
print("  pbkdf2_hmac(sha256, 600_000 iterations) took a noticeable, deliberate",
      "fraction of a second" if time.perf_counter() - t0 < 2 else "long time")
print("  -> the slowness is the feature: it costs YOU one login, an attacker a billion guesses.")
print("# - Also add: rate limiting, lockout/backoff, MFA, and never reveal whether the")
print("#   username or the password was wrong ('invalid credentials').")

# 13. Randomness: random vs secrets
# ------------------------------------
# - random is a predictable generator (Mersenne Twister). Given its seed or a
#   few outputs, every future value can be computed. Fine for games and
#   simulations, FATAL for tokens, reset links, session ids, passwords.
# - secrets uses the operating system's secure source and cannot be seeded.
#   (More in "06-Standard Library/12-Random-And-Secrets.py".)

import random  # noqa: E402

print("\n# 13. random vs secrets")
a, b = random.Random(1234), random.Random(1234)
print("  two random.Random(1234):", [a.randint(0, 99) for _ in range(5)], "==", [b.randint(0, 99) for _ in range(5)], "<- predictable")
print("  secrets.token_hex(8) twice differ:", secrets.token_hex(8) != secrets.token_hex(8))
alphabet = "abcdefghjkmnpqrstuvwxyz23456789"
password = "".join(secrets.choice(alphabet) for _ in range(14))
print("  generated password length:", len(password), "| secrets.randbelow(10) in range:", 0 <= secrets.randbelow(10) < 10)
print("  hmac.compare_digest('abc', 'abc') ->", hmac.compare_digest("abc", "abc"), "(constant-time compare for tokens/MACs)")
print("# - '==' on secrets can leak, via timing, how many leading characters were right.")
print("# - uuid.uuid4() is random enough for ids; uuid1() embeds time + MAC: do not use as a secret.")

# 14. HTTPS / TLS verification must stay ON
# ------------------------------------
# - Certificate verification is what proves you are talking to the REAL server.
#   Turning it off makes HTTPS pointless: anyone on the network can read/modify
#   the traffic ("man-in-the-middle").
# - NEVER, to "make the error go away":
#       requests.get(url, verify=False)
#       ssl._create_unverified_context()
#       context.check_hostname = False ; context.verify_mode = ssl.CERT_NONE
#       urllib3.disable_warnings()
# - Fix the real cause instead: install the right CA bundle, set
#   REQUESTS_CA_BUNDLE / SSL_CERT_FILE for an internal CA, fix the server's
#   certificate chain or hostname.
# - Always set timeouts (requests.get(url, timeout=5)): a hanging peer is a DoS.

print("\n# 14. TLS verification (inspecting contexts only - no network)")
good_ctx = ssl.create_default_context()
print("  create_default_context(): verify_mode =", good_ctx.verify_mode.name, "| check_hostname =", good_ctx.check_hostname)
with __import__("warnings").catch_warnings():
    __import__("warnings").simplefilter("ignore")
    bad_ctx = ssl._create_unverified_context()  # noqa: S323  <- shown ONLY to display its settings
print("  _create_unverified_context(): verify_mode =", bad_ctx.verify_mode.name, "| check_hostname =", bad_ctx.check_hostname, " <- DO NOT USE")
print("  minimum TLS version of default context:", good_ctx.minimum_version.name)

# 15. Output escaping (XSS) and friends
# ------------------------------------
# - XSS: untrusted text placed into HTML runs as script in the victim's browser.
#   Fix: ESCAPE for the context you output into:
#       HTML body / attribute -> html.escape(text, quote=True)
#       URL part              -> urllib.parse.quote(text)
#       shell                 -> shlex.quote(text)
#       SQL                   -> parameters (section 4)
# - Better: use a template engine with auto-escape ON (Jinja2 autoescape=True,
#   Django templates) and never mark user text as "safe".

print("\n# 15. XSS and escaping")
comment = '<script>alert("harmless demo")</script> & "quotes"'
print("  raw into HTML   :", f"<p>{comment}</p>")
print("  escaped         :", f"<p>{html.escape(comment)}</p>")
attr_attack = '" onmouseover="steal()'
print("  attribute attack:", f'<input value="{attr_attack}">', "<- breaks out of value=")
print("  attribute safe  :", f'<input value="{html.escape(attr_attack, quote=True)}">')
print("# - Also: send 'Content-Security-Policy' and set cookies HttpOnly + Secure + SameSite.")

# 16. XML bombs and defusedxml
# ------------------------------------
# - XML can define "entities" that expand into other entities. A tiny document
#   can expand to gigabytes ("billion laughs"), and external entities can make
#   the parser read local files or fetch URLs (XXE).
# - Python's xml.* modules are not hardened against every case; for untrusted
#   XML use the defusedxml package (pip install defusedxml), a drop-in:
#       from defusedxml import ElementTree as ET
# - Demo: a SMALL expansion (hundreds of characters, harmless).

print("\n# 16. XML entity expansion")
XML_BOMB = """<?xml version="1.0"?>
<!DOCTYPE lolz [
  <!ENTITY a "haha">
  <!ENTITY b "&a;&a;&a;&a;&a;&a;&a;&a;&a;&a;">
  <!ENTITY c "&b;&b;&b;&b;&b;&b;&b;&b;&b;&b;">
]>
<lolz>&c;</lolz>"""
import xml.etree.ElementTree as ET  # noqa: E402

root = ET.fromstring(XML_BOMB)
print(f"  stdlib parsed {len(XML_BOMB)} bytes of XML into {len(root.text)} characters (x{len(root.text) // len(XML_BOMB)} bigger)")
print("  (each extra entity level multiplies the size: 3 more levels of x10 = 1000x, 10 levels = gigabytes)")
try:
    from defusedxml import ElementTree as SafeET
    from defusedxml.common import DefusedXmlException

    try:
        SafeET.fromstring(XML_BOMB)
    except DefusedXmlException as exc:
        print("  defusedxml        ->", type(exc).__name__, "(entity definitions refused)")
except ImportError:
    print("  (defusedxml not installed - pip install defusedxml)")

# 17. Supply-chain hygiene (printed reference)
# ------------------------------------
# - Your app is mostly OTHER people's code. A malicious or compromised package
#   runs with your privileges the moment you install or import it.
# - Habits:
#     * PIN versions (requirements.txt / lockfile: uv.lock, poetry.lock, pip-tools)
#       so you install exactly what you tested.
#     * PIN HASHES so a swapped file is refused:
#           pip-compile --generate-hashes requirements.in
#           pip install --require-hashes -r requirements.txt
#       a hashed line looks like:
#           requests==2.32.3 \
#               --hash=sha256:<64 hex chars>
#     * SCAN for known vulnerabilities in CI:  pip-audit   (or: safety check),
#       and turn on Dependabot / Renovate for update pull requests.
#     * REVIEW new dependencies: maintained? many users? needed at all?
#       Prefer the standard library for small jobs.
#     * TYPOSQUATTING: attackers publish names one typo away from popular
#       packages (reqeusts, python-dateutil vs dateutils). Copy names from
#       official docs, not memory.
#     * Install from trusted indexes only; avoid '--extra-index-url' mixing
#       public and private indexes (dependency confusion).
#     * Separate dev and runtime dependencies; use virtual environments; do not
#       'sudo pip install'.
#     * CI secrets: least-privilege tokens, no secrets in pull requests from forks.

print("\n# 17. Supply chain: a tiny typosquat check (no network)")
KNOWN = ["requests", "numpy", "pandas", "flask", "django", "pytest", "urllib3", "cryptography"]
for wanted in ["requests", "reqeusts", "nunpy", "left-pad-utils"]:
    close = difflib.get_close_matches(wanted, KNOWN, n=1, cutoff=0.8)
    if wanted in KNOWN:
        print(f"  {wanted:16} known package")
    elif close:
        print(f"  {wanted:16} WARNING: one typo away from {close[0]!r} - possible typosquat")
    else:
        print(f"  {wanted:16} unknown - review before installing")
print("  tools: pip-audit | safety | Dependabot | Renovate | pip install --require-hashes")

# 18. Least privilege, file permissions
# ------------------------------------
# - Run services as a normal user (never root); in containers set USER;
#   give the DB account only the tables/operations it needs; give API tokens
#   the minimum scopes; make files private by default.

print("\n# 18. Least privilege (file permissions)")
key_path = TMP / "private.key"
fd = os.open(key_path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)  # private from the first byte
with os.fdopen(fd, "w") as f:
    f.write("demo-not-a-real-key")
print("  created with mode", oct(key_path.stat().st_mode & 0o777), "- owner only (no window where it was world-readable)")
print("  write_text() + chmod() afterwards leaves a short window of default permissions.")
print("  running as root?", hasattr(os, "geteuid") and os.geteuid() == 0, "(should be False for app code)")

# 19. Access control: check ownership, not just login
# ------------------------------------
# - Broken access control is #1 in the OWASP list. Being logged in is
#   authentication; "may THIS user see THIS record" is authorization, and
#   must be checked on the SERVER for every request.

print("\n# 19. Authorization (IDOR)")
INVOICES = {1: {"owner": "asha", "total": 500}, 2: {"owner": "raj", "total": 900}}


def get_invoice_bad(current_user, invoice_id):
    return INVOICES[invoice_id]  # trusts the id from the URL


def get_invoice(current_user, invoice_id):
    invoice = INVOICES.get(invoice_id)
    if invoice is None or invoice["owner"] != current_user:
        raise LookupError("invoice not found")  # same answer for 'missing' and 'not yours'
    return invoice


print("  bad : asha asks for invoice 2 ->", get_invoice_bad("asha", 2), "<- raj's data leaked")
try:
    get_invoice("asha", 2)
except LookupError as exc:
    print("  good: asha asks for invoice 2 ->", exc)

# 20. Server-side request forgery (SSRF) check - no network used
# ------------------------------------
# - If your server fetches a URL given by a user, the user can point it at
#   internal addresses (127.0.0.1, cloud metadata 169.254.169.254, 10.x.x.x)
#   or file:// URLs. Allow-list schemes and hosts; reject private IPs.

print("\n# 20. SSRF: URL allow-listing")
ALLOWED_HOSTS = {"api.example.com", "cdn.example.com"}


def url_allowed(url):
    parts = urlparse(url)
    if parts.scheme != "https" or not parts.hostname:
        return False
    try:
        ip = ipaddress.ip_address(parts.hostname)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return False
    except ValueError:
        pass  # a hostname, not an IP literal
    return parts.hostname in ALLOWED_HOSTS


for url in ["https://api.example.com/v1/items", "http://api.example.com/", "https://127.0.0.1/admin",
            "https://169.254.169.254/latest/meta-data", "file:///etc/passwd", "https://evil.example.net/"]:
    print(f"  {url:44} -> {'ALLOWED' if url_allowed(url) else 'blocked'}")
print("# - Also re-check after redirects and DNS resolution; DNS can point a public name at 127.0.0.1.")

# 21. Error messages and stack traces must not leak internals
# ------------------------------------
# - A traceback shows file paths, library versions, SQL, sometimes secrets:
#   a map for attackers. Show users a short generic message + a reference id;
#   write the full detail to your PRIVATE logs under the same id.
# - Never run web frameworks in debug mode in production (Flask debug=True
#   exposes an interactive console; Django DEBUG=True leaks settings).

print("\n# 21. Do not leak internals")
private_log = io.StringIO()
logging.basicConfig(stream=private_log, level=logging.ERROR, format="%(message)s", force=True)


def handle_request():
    try:
        db_password = "hunter2"
        raise ConnectionError(f"cannot connect to db.internal:5432 as admin with password {db_password}")
    except Exception:
        ref = secrets.token_hex(4)
        logging.exception("request failed [ref=%s]", ref)  # detail goes to PRIVATE logs
        return f"Something went wrong. Reference: {ref}", ref


public_message, ref = handle_request()
print("  user sees   :", re.sub(r"[0-9a-f]{8}", "<ref>", public_message))
print("  private log holds the details:", "db.internal" in private_log.getvalue(), "(and the ref id:", ref in private_log.getvalue(), ")")
logging.basicConfig(stream=sys.stdout, force=True)
logging.getLogger().handlers.clear()
print("# - Careful: the secret in that message is itself a leak even in logs; redact (section 11).")

# 22. python -X dev, -W error, -I
# ------------------------------------
# - python -X dev    : development mode - more warnings (unclosed files, bad
#                      encodings), asyncio debug, memory-error hooks. Run your tests with it.
# - python -W error  : every warning becomes an exception. Deprecations are
#                      early notice of removals - and sometimes of insecure defaults.
# - python -I        : isolated mode - ignores PYTHON* env vars and the user's
#                      site-packages and script dir: safer for admin scripts.
# - pytest -W error  : same idea inside the test run.

print("\n# 22. python -X dev")
leak = "f = open(__import__('os').devnull)\nprint('script finished')\n"
for flags in ([], ["-X", "dev"]):
    done = subprocess.run([sys.executable, *flags, "-c", leak], capture_output=True, text=True, env=ENV, timeout=30)
    warn = [ln for ln in done.stderr.splitlines() if "ResourceWarning" in ln]
    label = "-X dev" if flags else "default"
    print(f"  {label:7}: stdout={done.stdout.strip()!r} warning={re.sub(r'0x[0-9a-f]+', '0x..', warn[0].split(': ', 1)[-1]) if warn else 'none (silently leaked a file handle)'}")

# 23. OWASP Top 10 (2021) mapped to Python
# ------------------------------------
# - OWASP = a community that lists the most common web-app risks. For each:
#   what it is, and the Python-flavoured example/fix covered above.
#
#   A01 Broken Access Control        IDOR: get_invoice(id) without owner check; path traversal
#                                    -> check ownership per request (section 19), safe_join (6)
#   A02 Cryptographic Failures       md5/sha1 passwords, http not https, hard-coded keys, random for tokens
#                                    -> scrypt/argon2 (12), secrets (13), TLS on (14)
#   A03 Injection                    SQL string-gluing, shell=True, eval, template injection
#                                    -> parameters (4), arg lists (5), literal_eval (2), escaping (15)
#   A04 Insecure Design              no rate limit, trusting client-side checks, no threat model
#                                    -> threat-model early (1), validate on the server
#   A05 Security Misconfiguration    DEBUG=True, default passwords, open admin pages, XML external entities
#                                    -> defusedxml (16), config per environment (21)
#   A06 Vulnerable/Outdated Components  old Django/Pillow/requests with known CVEs
#                                    -> pip-audit, Dependabot, pinned+updated deps (17)
#   A07 Identification & Authentication Failures  weak passwords, no lockout/MFA, session ids that guess
#                                    -> hashing (12), secrets tokens (13), rate limiting
#   A08 Software & Data Integrity Failures  pickle.loads on untrusted data, unsigned updates, CI tampering
#                                    -> json/yaml.safe_load (3), --require-hashes (17), hmac signatures
#   A09 Logging & Monitoring Failures  no logs of logins/failures, OR logging secrets
#                                    -> structured logs, redaction filter (11), alerts
#   A10 Server-Side Request Forgery  fetching user-supplied URLs
#                                    -> host/scheme allow-list, block private IPs (20)

print("\n# 23. OWASP Top 10 -> section map")
OWASP = [
    ("A01 Broken Access Control", "19, 6"), ("A02 Cryptographic Failures", "12, 13, 14"),
    ("A03 Injection", "2, 4, 5, 15"), ("A04 Insecure Design", "1, 8"),
    ("A05 Security Misconfiguration", "16, 21, 22"), ("A06 Vulnerable Components", "17"),
    ("A07 Auth Failures", "12, 13"), ("A08 Integrity Failures", "3, 17"),
    ("A09 Logging Failures", "11, 21"), ("A10 SSRF", "20"),
]
for risk, sections in OWASP:
    print(f"  {risk:32} -> sections {sections}")

# 24. Pre-release security checklist
# ------------------------------------
#   [ ] No secrets in code or git history; .env in .gitignore; secrets rotated if ever leaked
#   [ ] All external input validated: type, length, range, allow-listed format
#   [ ] No eval/exec/pickle/yaml.load on untrusted data; shell=False with arg lists
#   [ ] All SQL parameterized; identifiers from allow-lists
#   [ ] File paths from users go through safe_join; archives extracted with filters
#   [ ] Passwords hashed with scrypt/argon2/bcrypt + salt; tokens from secrets
#   [ ] TLS verification on everywhere; timeouts on every network call
#   [ ] Output escaped / template autoescape on; security headers and cookie flags set
#   [ ] Authorization checked per object, on the server
#   [ ] Dependencies pinned (with hashes), scanned (pip-audit), and minimal
#   [ ] DEBUG off; errors generic to users, detailed in private logs; logs free of secrets
#   [ ] Runs as non-root with least privilege; files private by default
#   [ ] Tests include hostile inputs ('../', quotes, huge sizes, unicode, empty)
#   [ ] Someone else reviewed the diff with "how would I abuse this?" in mind

print("\n# 24. Pre-release checklist: see the comment block above (14 items)")

# 25. Cleanup
# ------------------------------------
TMP_HOLDER.cleanup()
print("\n# 25. Cleanup")
print("temp folder removed:", not TMP.exists())
