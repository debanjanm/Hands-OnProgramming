# Bytes & Bytearray — Notes

## What this covers
How Python stores raw binary data: `bytes` (immutable), `bytearray` (mutable), `memoryview` (zero-copy window), and the tools around them (`struct`, `int.to_bytes`, `base64`, binary files, subprocess/sockets).

## Key points
- **`str` = Unicode text, `bytes` = raw integers 0-255.** An *encoding* (UTF-8) converts between them: `text.encode()` -> bytes, `data.decode()` -> str.
- Python 3 never mixes them: `"a" + b"b"` raises `TypeError`, and `"a" == b"a"` is just `False`.
- Ways to make bytes: `b"abc"` (ASCII only), `bytes(3)` (three zero bytes), `bytes([72, 105])`, `"hi".encode()`, `bytes.fromhex("48 69")`.
- `bytes` is immutable and hashable (dict key OK). `bytearray` is mutable (item/slice assignment, `append`, `extend`, `pop`, `insert`, `+=`) and NOT hashable.
- `bytes` has the familiar str methods (`split`, `join`, `replace`, `find`, `startswith`...) but arguments must also be bytes. Use `b"%d" % 5` for formatting.
- `.hex()` / `bytes.fromhex()` for readable debugging. `binascii.hexlify` is the old spelling.
- `.decode(errors=...)`: `"strict"` (default, raises), `"replace"` (inserts a replacement char), `"ignore"` (silently drops).
- `int.to_bytes(length, "big"|"little")` and `int.from_bytes(data, byteorder)`. **Big endian** = most significant byte first (how we write numbers); **little** = least significant first (x86/ARM memory). Negative numbers need `signed=True`.
- `struct.pack(">H f ? 4s", ...)` / `struct.unpack(...)` read and write fixed binary records. Start the format with `<`, `>` or `!`.
- `memoryview(buf)[a:b]` slices **without copying**; writes through the view change the original buffer.
- `base64.b64encode` makes bytes printable (about 33% bigger). It is encoding, not encryption.
- Files: `'rb'`/`'wb'` give/take bytes with no decoding or newline translation. Sockets, `hashlib`, and `subprocess` output (unless `text=True`) are bytes too.

## Gotchas (the part worth revising twice)
- **`b[0]` is an int, `b[0:1]` is bytes.** `b"hello"[0]` gives `104`, not `b"h"`; iterating bytes yields ints. `b[0] == "h"` is always False.
- **`bytes(5)` is five zero bytes, not the byte `5`.** To get `b"\x05"` use `bytes([5])`.
- One character can be several bytes in UTF-8 (`"é"` = 2, `"€"` = 3), so `len(text) != len(text.encode())`.
- `errors="ignore"` hides data loss. The real fix for a `UnicodeDecodeError` is using the *correct* encoding (`b"caf\xe9"` is latin-1, not UTF-8).
- Always give `struct` an explicit byte-order character. Native mode (`@`, the default) pads fields for alignment, so `calcsize("@bi")` is 8, not 5.
- A `memoryview` locks its bytearray: `append` raises `BufferError` until you `release()` the view.
- `open(path, "wb")` truncates the file immediately, even if the later write fails.
- Repeated `bytes += chunk` builds a new object each time. Use `b"".join(chunks)` or a `bytearray`.
- `b[i] = 300` or `bytes([256])` -> `ValueError` (values must be 0-255). `(256).to_bytes(1, "big")` -> `OverflowError`.

## When it matters
Any time data crosses a boundary: files (images, zips), network protocols, hashing, subprocess output, binary formats. Rule of thumb: decode bytes to `str` as soon as data comes in, work with `str` inside your program, encode only when sending out.

## One-line recap example
```python
data = "café".encode("utf-8")          # b'caf\xc3\xa9'  (5 bytes for 4 characters)
print(data[0], data[0:1])              # 99 b'c'  -> index gives int, slice gives bytes
buf = bytearray(data); buf[0] = 67     # mutable edit -> bytearray(b'Caf\xc3\xa9')
print(int.from_bytes(b"\x01\x02", "big"))   # 258
```
