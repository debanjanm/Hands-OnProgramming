# Hashing and Encoding — Notes

## What this covers
How to fingerprint, sign and re-format data with `hashlib`, `hmac`, `base64`, `binascii`, `urllib.parse`, `uuid` and `zlib` — and, more importantly, which tool is for which job (encoding vs hashing vs encryption vs signing).

## Key points
- **Four different ideas**: *encoding* (change format, anyone can reverse), *hashing* (one-way fingerprint), *encryption* (reversible only with a key), *signing/HMAC* (hash + secret key = proof nobody tampered).
- **`hashlib`** works on **bytes**: `hashlib.sha256("text".encode())`. `.hexdigest()` gives a hex string, `.digest()` gives raw bytes.
- Same input -> same hash. Change one character -> about half of the bits change (**avalanche effect**).
- `update()` can be called many times — same result as hashing everything at once. Use it to hash big files in chunks (e.g. 64 KB at a time). `hashlib.file_digest(f, "sha256")` does it for you on 3.11+.
- `hashlib.algorithms_guaranteed` lists algorithms present on every platform.
- **Good default**: sha256 (or blake2b, which is often faster). **md5 / sha1** have known collisions — fine for accidental-corruption checks and cache keys, never for security.
- **Passwords**: random **salt** + a deliberately **slow** KDF (`hashlib.scrypt` or `hashlib.pbkdf2_hmac`), store `scheme$salt$hash`, verify with `hmac.compare_digest`. Never plain `sha256(password)`.
- **`hmac.new(key, msg, hashlib.sha256)`** signs a message. Verify by recomputing and comparing with `hmac.compare_digest` (timing-safe). Basis of webhook signatures and signed cookies/tokens.
- **`base64`**: `b64encode / b64decode` turn bytes into safe text (about 33% bigger). `urlsafe_b64encode` swaps `+/` for `-_`. `b32encode` and `b16encode` are the other bases.
- `bytes.hex()` / `bytes.fromhex()` cover most hex needs; `binascii.hexlify` is the old low-level version.
- **`urllib.parse`**: `quote` (space -> `%20`, keeps `/`), `quote_plus` (space -> `+`, escapes `/`), `unquote`, `unquote_plus`. Percent-encoding is encoding, not secrecy.
- **`uuid`**: `uuid4()` random (default choice), `uuid5(namespace, name)` same input -> same UUID, `uuid1()` leaks MAC + time. `UUID(str)` parses; `.hex`, `.int`, `.bytes` convert. `uuid7` only exists on 3.14+.
- **Checksums**: `zlib.crc32` / `zlib.adler32` — tiny and fast, catch accidents, not attackers.
- **Content-addressed storage**: name each blob by the hash of its content -> identical files are stored once (how git and backup tools dedupe).
- Random tokens/salts/keys come from **`secrets`**, never `random`.

## Gotchas (the part worth revising twice)
- **Base64 is NOT encryption.** `base64.b64decode("UGFzc3dvcmQxMjM=")` gives the password instantly. HTTP Basic auth is only base64.
- Hashing a `str` raises `TypeError` — encode first, and always with the same encoding or hashes won't match.
- `==` on signatures/hashes can leak timing; use `hmac.compare_digest`.
- Fast hashes are wrong for passwords — attackers try billions of guesses per second. Use scrypt/pbkdf2/argon2 with a unique salt per user.
- Missing `=` padding makes `b64decode` raise `binascii.Error: Incorrect padding` (JWTs and URLs strip it). Re-add with `s + "=" * (-len(s) % 4)`.
- `b64decode` silently drops junk characters unless you pass `validate=True`.
- `hexdigest()` is `str`, `digest()` is `bytes` — comparing one against the other is always `False`.
- A signed token is readable by anyone (the payload is only base64); the signature only stops *changes*. Add an expiry inside the payload.
- `uuid1` reveals the machine and creation time; don't expose it publicly.

## When it matters
Verifying downloads, deduplicating files, storing user passwords, checking webhook signatures, building URLs and query strings, generating unique ids, and embedding binary data in JSON or email.

## One-line recap example
```python
import hashlib, hmac
print(hashlib.sha256(b"hello").hexdigest()[:12])                 # 2cf24dba5fb0 -> one-way fingerprint
print(hmac.compare_digest("abc", "abc"))                         # True -> timing-safe compare
```
