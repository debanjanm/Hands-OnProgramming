import hashlib
import hmac
import base64
import binascii
import secrets
import sys
import tempfile
import uuid
import zlib
import os
from pathlib import Path
from urllib.parse import quote, quote_plus, unquote, unquote_plus

# 01. Hashing and Encoding - Introduction
# ------------------------------------
# - These tools all "turn data into other data", but for VERY different goals.
#   Mixing them up is one of the most common (and most dangerous) beginner bugs.
#     * ENCODING   : change the FORMAT so data survives a channel. Reversible by anyone.
#     * HASHING    : one-way fingerprint. Same input -> same output, cannot go back.
#     * ENCRYPTION : scramble with a secret key. Reversible ONLY with the key.
#     * SIGNING    : hash + secret key (HMAC) -> proves who made it and that it
#                    was not changed. Not secret, just tamper-proof.
# - The big comparison table is at the end (section 21).

print("# 01. Hashing and Encoding - Introduction")
print("# ------------------------------------")

# 02. hashlib Basics - Fingerprints of Data
# ------------------------------------
# - hashlib works on BYTES, not str. Encode text first: "text".encode("utf-8").
# - hexdigest() -> readable hex string (what you usually print/store).
# - digest()    -> the raw bytes (half as long as hex, 1 byte = 2 hex chars).
print("\n# 02. hashlib basics")
message = b"hello world"
for name in ["md5", "sha1", "sha256", "sha512", "blake2b", "sha3_256"]:
    # usedforsecurity=False keeps md5 working on locked-down (FIPS) systems
    h = hashlib.new(name, message, usedforsecurity=False) if name in ("md5", "sha1") else hashlib.new(name, message)
    print(f"{name:<9} {h.digest_size * 8:>3} bits  {h.hexdigest()[:32]}...")
sha = hashlib.sha256(message)
print("hexdigest:", sha.hexdigest())
print("digest   :", sha.digest()[:8], "... (", len(sha.digest()), "bytes )")
print("same input -> same hash:", hashlib.sha256(message).hexdigest() == sha.hexdigest())

try:
    hashlib.sha256("a str, not bytes")
except TypeError as e:
    print("TypeError:", e)

# 03. algorithms_guaranteed vs algorithms_available
# ------------------------------------
# - guaranteed: present on EVERY platform. available: depends on OpenSSL build.
print("\n# 03. algorithms_guaranteed")
print("guaranteed:", sorted(hashlib.algorithms_guaranteed))
print("# Write portable code with names from 'guaranteed'.")

# 04. Avalanche Effect - Tiny Change, Totally Different Hash
# ------------------------------------
# - A good hash flips about half of its bits when ONE input bit changes.
#   That is why you can't "close in" on an input by looking at hash similarity.
print("\n# 04. Avalanche effect")
h1 = hashlib.sha256(b"hello world").digest()
h2 = hashlib.sha256(b"hello worle").digest()  # one letter changed (d -> e)
diff_bits = bin(int.from_bytes(h1, "big") ^ int.from_bytes(h2, "big")).count("1")
print("hello world:", h1.hex()[:32], "...")
print("hello worle:", h2.hex()[:32], "...")
print(f"bits that differ: {diff_bits} of 256 (about half is expected)")

# 05. Incremental Hashing - update() in Pieces
# ------------------------------------
# - h.update(a); h.update(b) is identical to hashing a+b in one go.
# - This is how you hash data that does not fit in memory.
print("\n# 05. update() in pieces")
whole = hashlib.sha256(b"hello world").hexdigest()
parts = hashlib.sha256()
parts.update(b"hello ")
parts.update(b"world")
print("same as one-shot:", parts.hexdigest() == whole)

# 06. Hashing a Large File in Chunks
# ------------------------------------
# - Read, say, 64 KB at a time; memory stays tiny even for a 50 GB file.
print("\n# 06. Hashing a file in chunks")


def sha256_file(path, chunk_size=64 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):  # walrus: read until empty bytes
            h.update(chunk)
    return h.hexdigest()


with tempfile.TemporaryDirectory() as tmp:
    big = Path(tmp) / "big.bin"
    big.write_bytes(b"abc123" * 500_000)  # about 3 MB
    chunked = sha256_file(big, chunk_size=4096)
    in_memory = hashlib.sha256(big.read_bytes()).hexdigest()
    print("size:", big.stat().st_size, "bytes")
    print("chunked == whole-file hash:", chunked == in_memory)
    print("hash:", chunked[:32], "...")

    # 07. hashlib.file_digest (Python 3.11+)
    # ------------------------------------
    print("\n# 07. hashlib.file_digest (3.11+)")
    if sys.version_info >= (3, 11):
        with open(big, "rb") as f:
            d = hashlib.file_digest(f, "sha256")  # file must be opened in BINARY mode
        print("file_digest matches:", d.hexdigest() == chunked)
    else:
        print("SKIPPED: hashlib.file_digest needs Python 3.11+ (use the chunk loop above)")

# 08. Why md5/sha1 Are "Broken" for Security But Fine for Checksums
# ------------------------------------
# - "Broken" = attackers can CREATE two different inputs with the same hash
#   (a collision). md5 collisions take seconds on a laptop; sha1 was broken in 2017.
# - So never use md5/sha1 for: signatures, certificates, password storage,
#   or anything where someone may be trying to fool you.
# - They are still fine to detect ACCIDENTAL corruption (download check),
#   cache keys, or ETags - where nobody is attacking you.
# - Default choice today: sha256 (or blake2b / sha3 if you like). Speed note:
#   blake2b is usually faster than sha256 and just as safe.
print("\n# 08. md5/sha1 vs sha256")
print("md5   :", hashlib.md5(b"abc", usedforsecurity=False).hexdigest(), "(checksums only)")
print("sha1  :", hashlib.sha1(b"abc", usedforsecurity=False).hexdigest(), "(legacy; git still uses it)")
print("sha256:", hashlib.sha256(b"abc").hexdigest(), "(safe default)")
print("# Truncating is OK too: blake2b(digest_size=16) gives a short 128-bit id:")
print("blake2b-16:", hashlib.blake2b(b"abc", digest_size=16).hexdigest())

# 09. Password Hashing Done RIGHT
# ------------------------------------
# - NEVER store plain passwords. And NEVER store sha256(password) either:
#   sha256 is FAST - an attacker with a leaked database tries billions of
#   guesses per second, and identical passwords share identical hashes.
# - Use a deliberately SLOW, salted key-derivation function (KDF):
#     * hashlib.scrypt  (memory-hard, great default)
#     * hashlib.pbkdf2_hmac (available everywhere)
#     * or the 3rd-party argon2 / bcrypt packages in real projects.
# - SALT = random bytes unique per user, stored beside the hash. It makes
#   equal passwords hash differently and kills pre-computed "rainbow tables".
# - Compare with hmac.compare_digest (constant time) - a normal == can leak,
#   via timing, how many leading characters matched.
print("\n# 09. Password hashing (salt + slow KDF + compare_digest)")
HAS_SCRYPT = hasattr(hashlib, "scrypt")


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)  # secrets = cryptographically strong randomness
    if HAS_SCRYPT:
        digest = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
        scheme = "scrypt"
    else:
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000, dklen=32)
        scheme = "pbkdf2"
    return f"{scheme}${salt.hex()}${digest.hex()}"  # everything needed to verify later


def verify_password(password: str, stored: str) -> bool:
    scheme, salt_hex, hash_hex = stored.split("$")
    salt = bytes.fromhex(salt_hex)
    if scheme == "scrypt":
        candidate = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    else:
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 200_000, dklen=32)
    return hmac.compare_digest(candidate, bytes.fromhex(hash_hex))


stored_a = hash_password("correct horse battery staple")
stored_b = hash_password("correct horse battery staple")  # same password, new salt
print("scheme:", stored_a.split("$")[0], "| stored length:", len(stored_a))
print("same password, different stored values:", stored_a != stored_b)
print("verify right password:", verify_password("correct horse battery staple", stored_a))
print("verify wrong password:", verify_password("Tr0ub4dor&3", stored_a))
print("# Real systems also store the KDF cost params so they can raise them later.")

# 10. hmac - Keyed Hash for Signing and Verifying
# ------------------------------------
# - HMAC = hash(secret_key + message), built so extension attacks fail.
#   Only someone holding the key can produce a valid tag.
# - Use it for: webhook signatures (GitHub/Stripe style), signed cookies,
#   API request signing. NOT for passwords (use a KDF) and NOT for secrecy
#   (the message stays readable).
print("\n# 10. hmac signing and verifying")
secret_key = b"server-side-secret"
body = b'{"order": 42, "amount": 999}'
signature = hmac.new(secret_key, body, hashlib.sha256).hexdigest()
print("signature:", signature[:32], "...")


def is_valid(key, message, received_sig):
    expected = hmac.new(key, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, received_sig)  # timing-safe


print("untouched body valid:", is_valid(secret_key, body, signature))
print("tampered body valid :", is_valid(secret_key, b'{"order": 42, "amount": 1}', signature))
print("wrong key valid     :", is_valid(b"attacker-guess", body, signature))
print("# hmac.digest(key, msg, 'sha256') is a faster one-shot version.")

# 11. A Tiny Signed Token (like a cookie or JWT-lite)
# ------------------------------------
# - payload + "." + signature. Anyone can READ the payload (it's only base64),
#   but nobody can CHANGE it without the key. Good for "remember who I am".
print("\n# 11. Tiny signed token")
TOKEN_KEY = b"token-signing-key"


def make_token(user: str) -> str:
    payload = base64.urlsafe_b64encode(user.encode()).rstrip(b"=")
    sig = hmac.new(TOKEN_KEY, payload, hashlib.sha256).digest()
    return payload.decode() + "." + base64.urlsafe_b64encode(sig).rstrip(b"=").decode()


def read_token(token: str):
    payload, sig = token.split(".")
    expected = base64.urlsafe_b64encode(hmac.new(TOKEN_KEY, payload.encode(), hashlib.sha256).digest()).rstrip(b"=").decode()
    if not hmac.compare_digest(expected, sig):
        return None
    padded = payload + "=" * (-len(payload) % 4)
    return base64.urlsafe_b64decode(padded).decode()


token = make_token("alice")
print("token:", token[:40], "...")
print("read back:", read_token(token))
forged = base64.urlsafe_b64encode(b"admin").rstrip(b"=").decode() + "." + token.split(".")[1]
print("forged 'admin' token accepted:", read_token(forged))
print("# Real tokens also carry an expiry time inside the signed payload.")

# 12. base64 - Binary as Safe Text
# ------------------------------------
# - base64 maps any bytes to 64 printable characters (A-Z a-z 0-9 + /).
#   It makes data about 33% BIGGER. Used for: email attachments, data: URLs,
#   embedding images/keys in JSON, HTTP Basic auth headers.
# - It is ENCODING, not encryption: anyone can reverse it (shown below).
print("\n# 12. base64 basics")
raw = "Hello, Python!".encode()
encoded = base64.b64encode(raw)
print("encoded:", encoded, "| type:", type(encoded).__name__)
print("decoded:", base64.b64decode(encoded).decode())
print("size: 14 bytes ->", len(encoded), "chars (4 chars per 3 bytes, padded with '=')")

print("\n# 12b. Base64 is NOT encryption - anyone can reverse it")
leaked = "UGFzc3dvcmQxMjM="  # looks scrambled, right?
print("looks secret:", leaked, "-> reversed in one line:", base64.b64decode(leaked).decode())
print("# Basic-auth headers are base64('user:pass') - readable by anyone who sees them; use HTTPS.")

# 13. URL-safe base64 and Other Bases
# ------------------------------------
# - Standard base64 uses '+' and '/', which have special meaning in URLs/filenames.
#   urlsafe_b64encode swaps them for '-' and '_'.
print("\n# 13. urlsafe, b32, b16")
tricky = bytes([251, 255, 190, 63])  # produces '+' and '/' in standard base64
print("standard :", base64.b64encode(tricky).decode())
print("urlsafe  :", base64.urlsafe_b64encode(tricky).decode())
print("b32      :", base64.b32encode(b"Hi!").decode(), "(case-insensitive, used by 2FA secrets)")
print("b16 (hex):", base64.b16encode(b"Hi!").decode(), "| bytes.hex():", b"Hi!".hex())

# 14. The Padding Gotcha - Fixing Missing '='
# ------------------------------------
# - base64 output length is a multiple of 4, padded with '='. JWTs and many
#   URLs STRIP the padding, and then b64decode refuses to decode.
print("\n# 14. Padding gotcha")
stripped = "SGVsbG8"  # base64 of 'Hello' is "SGVsbG8=" - the trailing '=' was stripped
try:
    base64.b64decode(stripped)
except binascii.Error as e:
    print("binascii.Error:", e)


def b64decode_nopad(s: str) -> bytes:
    return base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))  # add back 0-3 '='


print("fixed:", b64decode_nopad(stripped))
print("# Also: b64decode silently DISCARDS junk characters unless validate=True.")
print("lenient :", base64.b64decode("SGVs!bG8="))
try:
    base64.b64decode("SGVs!bG8=", validate=True)
except binascii.Error as e:
    print("strict  : binascii.Error:", e)

# 15. binascii and bytes.hex
# ------------------------------------
# - bytes.hex() / bytes.fromhex() cover most hex needs in modern Python.
# - binascii is the older low-level module (hexlify/unhexlify, crc32...).
print("\n# 15. hex helpers")
data = b"\x00\xffAB"
print("bytes.hex()       :", data.hex())
print("bytes.fromhex()   :", bytes.fromhex("00ff4142"))
print("binascii.hexlify  :", binascii.hexlify(data), "(returns bytes, not str)")
print("hex with separator:", data.hex(":"), "(handy for MAC-address style output)")
try:
    bytes.fromhex("xyz")
except ValueError as e:
    print("ValueError:", e)

# 16. Percent-Encoding with urllib.parse
# ------------------------------------
# - URLs may only contain a safe set of ASCII characters. Everything else
#   becomes %XX (byte in hex). Another "encoding" - reversible, not secret.
# - quote: spaces -> %20, '/' is kept safe by default.
# - quote_plus: spaces -> '+', and '/' IS escaped. This is the HTML-form
#   (query-string) style.
print("\n# 16. Percent-encoding")
text = "name=Ana & Bob/Ünï"
print("quote       :", quote(text))
print("quote safe=''  :", quote(text, safe=""), "(escape EVERYTHING incl. '/')")
print("quote_plus  :", quote_plus(text))
print("unquote     :", unquote(quote(text)))
print("unquote_plus:", unquote_plus("a+b%2Bc"), "(a plus sign is a space, %2B is a real '+')")
print("# Use urllib.parse.urlencode({...}) to build whole query strings correctly.")

# 17. uuid - Unique Identifiers
# ------------------------------------
# - A UUID is a 128-bit id, shown as 32 hex digits in 8-4-4-4-12 groups.
# - uuid4(): random. The usual choice for "give this record a unique id"
#   without asking a central database. Collisions are practically impossible.
# - uuid5(namespace, name): DETERMINISTIC (sha1-based) - same namespace+name
#   always gives the same UUID. Great for stable ids derived from a URL/email.
#   (uuid3 is the md5 version - avoid, use uuid5.)
# - uuid1(): built from MAC address + timestamp -> it LEAKS the machine and
#   the time it was made. Avoid for public ids.
print("\n# 17. uuid")
u4 = uuid.uuid4()
print("uuid4 (random) version:", u4.version, "| str length:", len(str(u4)), "| differs each call:", u4 != uuid.uuid4())

a = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/page")
b = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/page")
print("uuid5 deterministic:", a, "| same on repeat:", a == b)
print("uuid5 other input  :", uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/other"))

u1 = uuid.uuid1()
print("uuid1 version:", u1.version, "| has a 48-bit 'node' (MAC-derived):", u1.node.bit_length() <= 48,
      "| has a timestamp:", u1.time > 0, " <- privacy leak, avoid")

# 18. UUID Objects: parsing, .hex, .int, .bytes
# ------------------------------------
print("\n# 18. UUID object attributes")
u = uuid.UUID("12345678-1234-5678-1234-567812345678")
print("str  :", str(u))
print("hex  :", u.hex)
print("int  :", u.int)
print("bytes:", u.bytes[:6], "...")
print("parsed from hex w/o dashes:", uuid.UUID("12345678123456781234567812345678") == u)
try:
    uuid.UUID("not-a-uuid")
except ValueError as e:
    print("ValueError:", e)

if hasattr(uuid, "uuid7"):  # added in Python 3.14
    u7 = uuid.uuid7()
    print("uuid7 (time-ordered) version:", u7.version, "- sorts by creation time, DB-index friendly")
else:
    print("SKIPPED: uuid.uuid7 needs Python 3.14+ (time-ordered ids; good for database keys)")

# 19. Checksums - zlib.crc32 and adler32
# ------------------------------------
# - Tiny, very fast, 32-bit "did the bytes change by accident?" checks.
# - They are NOT cryptographic: an attacker can craft a change that keeps
#   the same crc. Used inside ZIP/PNG/gzip files and network protocols.
print("\n# 19. crc32 / adler32")
payload = b"The quick brown fox"
print("crc32  :", zlib.crc32(payload), "| as hex:", format(zlib.crc32(payload), "08x"))
print("adler32:", zlib.adler32(payload))
print("one flipped letter crc32:", zlib.crc32(b"The quick brown fax"))
running = zlib.crc32(b"The quick ")
running = zlib.crc32(b"brown fox", running)  # pass the previous value to continue
print("incremental crc32 matches:", running == zlib.crc32(payload))

# 20. Mini Project: Content-Addressed Store and Duplicate Finder
# ------------------------------------
# - Content-addressed = the FILENAME is the hash of the CONTENT.
#   Same content -> same name -> stored once (dedupe). Git, Docker and
#   backup tools (restic, borg) all work this way.
print("\n# 20. Content-addressed store + dedupe")


def store(store_dir: Path, content: bytes) -> str:
    key = hashlib.sha256(content).hexdigest()
    target = store_dir / key[:2] / key  # 2-char folder keeps directories small
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
    return key


def find_duplicates(folder: Path):
    seen = {}  # hash -> first file with that content
    dups = []
    for p in sorted(folder.iterdir()):
        digest = sha256_file(p)
        if digest in seen:
            dups.append((p.name, seen[digest]))
        else:
            seen[digest] = p.name
    return dups


with tempfile.TemporaryDirectory() as tmp:
    tmp = Path(tmp)
    src = tmp / "src"
    src.mkdir()
    (src / "a.txt").write_text("same content")
    (src / "b.txt").write_text("different content")
    (src / "c_copy.txt").write_text("same content")  # duplicate of a.txt
    print("duplicates (copy, original):", find_duplicates(src))

    cas = tmp / "cas"
    keys = [store(cas, p.read_bytes()) for p in sorted(src.iterdir())]
    stored_files = [f for f in cas.rglob("*") if f.is_file()]
    print("files added: 3 | blobs actually stored:", len(stored_files), "(dedupe!)")
    print("a.txt and c_copy.txt share key:", keys[0] == keys[2])

# 21. Encoding vs Hashing vs Encryption vs Signing (comparison)
# ------------------------------------
print("\n# 21. Comparison table")
print("#               Reversible?       Needs key?   Goal                      Python tool")
print("# ----------------------------------------------------------------------------------------")
print("# Encoding      yes (by anyone)   no           safe format for transport base64, quote, hex")
print("# Hashing       NO (one-way)      no           fingerprint / integrity   hashlib.sha256")
print("# Password KDF  NO (one-way)      no (salt)    slow, safe pw storage     hashlib.scrypt / pbkdf2")
print("# Signing/HMAC  NO                shared key   authenticity + tamper     hmac")
print("# Encryption    yes (with key)    yes          secrecy                   3rd-party: cryptography")
print("# Checksum      NO                no           accidental-error check    zlib.crc32")
print("#")
print("# Rules of thumb:")
print("# - Need to hide data?              -> ENCRYPT (cryptography.fernet), never base64.")
print("# - Need to detect tampering?       -> HMAC (shared secret) or a digital signature.")
print("# - Need to compare / dedupe data?  -> hash it.")
print("# - Need to store a password?       -> scrypt/argon2 + salt, verify with compare_digest.")
print("# - Need random tokens/keys/salts?  -> secrets module (NOT random, which is predictable).")
print("# Example: secrets.token_urlsafe(16) ->", len(secrets.token_urlsafe(16)), "url-safe characters of randomness")

# 22. Gotchas Recap
# ------------------------------------
print("\n# 22. Gotchas recap")
print("# - hashlib needs bytes; encode str first, and always the same way (utf-8).")
print("# - hexdigest() = str, digest() = bytes - don't mix them when comparing.")
print("# - Never sha256(password). Use scrypt/pbkdf2 + random salt + compare_digest.")
print("# - '==' on secrets/signatures leaks timing; use hmac.compare_digest.")
print("# - base64 is reversible by everyone. It protects nothing.")
print("# - Missing '=' padding breaks b64decode - re-add it before decoding.")
print("# - uuid1 leaks MAC+time; uuid4 is random; uuid5 is repeatable.")
print("# - md5/sha1/crc32 are for accidental errors only, never for security.")
