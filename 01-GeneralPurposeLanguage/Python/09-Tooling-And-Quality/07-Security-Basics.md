# Security Basics — Notes

## What this covers
A developer's security checklist for Python, with safe (harmless-payload) demos: injection, unsafe deserialization, path traversal, validation, ReDoS, secrets, passwords, randomness, TLS, escaping, supply chain and error handling.

## Key points
- **Trust boundary**: everything entering the program (forms, URLs, headers, file names, uploads, env vars, other services) is untrusted until validated. Prefer **allow-lists** over deny-lists; check type, length, range, then format.
- **Code vs data**: `eval`/`exec` on input is remote code execution → use `ast.literal_eval` or a whitelisted AST walker. SQL → parameters (`?`), identifiers from an allow-list. Shell → `subprocess.run([...])` with no shell, or `shlex.quote` if you must.
- **Deserialization**: never `pickle.loads` untrusted bytes; use JSON; `yaml.safe_load` not `yaml.load`; XML from outsiders → `defusedxml`.
- **Paths**: `(base / name).resolve()` then `.is_relative_to(base)`. This catches `../`, absolute paths and symlinks. Archives: check member names (zip slip); `tarfile.extractall(filter="data")`.
- **Temp files**: `tempfile` (`mkstemp`, `TemporaryDirectory`) gives unpredictable names and mode `0600`. Create files atomically (`open(path, "x")`, `os.open(..., 0o600)`).
- **Validation**: `re.fullmatch` not `re.match`; normalize (NFKC) and `casefold()` before comparing names; limit input sizes before parsing.
- **`assert` is not validation**: `python -O` removes it. Raise `ValueError`.
- **Secrets**: never in code; env vars or git-ignored `.env`; fail fast if missing; redact in logs (a `logging.Filter`); rotate if leaked.
- **Passwords**: slow + salted hash (`hashlib.scrypt`/`pbkdf2_hmac`, or argon2/bcrypt), compare with `hmac.compare_digest`. **Randomness for security**: `secrets`, never `random`.
- **TLS**: leave verification ON (`verify=False` / `_create_unverified_context` are bugs). Always set timeouts.
- **Escape per context**: `html.escape` for HTML/attributes, `shlex.quote` for shell, `urllib.parse.quote` for URLs; use autoescaping templates.
- **Supply chain**: pin versions and hashes (`pip install --require-hashes`), run `pip-audit`, enable Dependabot, review new deps, watch for typosquats.
- **Authorization** checked per object on the server (IDOR); **SSRF**: allow-list URL schemes/hosts, block private IPs. Errors to users stay generic with a reference id; details go to private logs. Run with least privilege.
- `python -X dev` and `-W error` surface hidden problems early (e.g. unclosed files).

## Gotchas (the part worth revising twice)
- `eval(x, {"__builtins__": {}})` is **not** a sandbox; attribute chains still reach every class.
- `Path("base") / "/etc/passwd"` **replaces** the base. Stripping `../` by hand fails (`....//`).
- `re.match(r"^[a-z]+$", "abc\n")` **matches** (`$` allows a trailing newline). Fix: `fullmatch`.
- `\d` and `str.isdigit()` accept non-ASCII digits (`int("١٢٣")` is 123); homoglyphs (`аdmin` with Cyrillic `а`) look identical but differ.
- Python ints don't overflow, but huge inputs exhaust CPU/RAM (`int("9"*5000)` is blocked at 4300 digits by default).
- **ReDoS**: nested quantifiers like `^(a+)+$` take ~4x longer per +2 characters on failing input. Fix: simpler pattern, possessive/atomic groups (3.11+), cap input length first.
- Plain `sha256(password)` gives the same hash every time (fast to attack). `==` on secrets can leak via timing.
- `write_text()` then `chmod()` leaves a window of loose permissions; create with the mode.
- Check-then-use (TOCTOU) races: prefer one atomic operation.
- A secret inside an exception message ends up in logs. Redaction is a safety net, not the fix.

## When it matters
Any code that touches input from outside: web apps, CLIs run on untrusted files, services calling other services. Treat the checklist as a pre-release review item.

## One-line recap example
```python
base = Path("uploads").resolve()
target = (base / user_filename).resolve()
if not target.is_relative_to(base):
    raise PermissionError("path escapes base folder")
```
