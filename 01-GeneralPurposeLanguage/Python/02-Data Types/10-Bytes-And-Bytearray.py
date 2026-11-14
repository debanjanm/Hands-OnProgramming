## 0.  Text vs Bytes: the core idea
## 1.  Creating bytes
## 2.  Indexing vs Slicing (the int/bytes gotcha)
## 3.  bytes is immutable, bytearray is mutable
## 4.  Methods that mirror str
## 5.  hex() and decode() with error handling
## 6.  Integers <-> bytes (endianness)
## 7.  struct: packing/unpacking binary records
## 8.  memoryview: zero-copy slicing
## 9.  base64 and binascii
## 10. Hashing and comparing bytes
## 11. Binary files: why open(..., 'rb') gives bytes
## 12. bytes vs str in subprocess / sockets

# Python bytes & bytearray Explanation

import sys

# 0. Text vs Bytes: the core idea
# ------------------------------------
# - str   = a sequence of Unicode CHARACTERS (text, what humans read).
# - bytes = a sequence of raw INTEGERS in range 0..255 (what disks/networks store).
# - To go between them you need an ENCODING (UTF-8 is the standard one):
#       str  --.encode("utf-8")-->  bytes
#       bytes --.decode("utf-8")--> str
# - Python 3 NEVER mixes the two implicitly. Python 2 did, and it caused
#   decades of "UnicodeError" bugs. The strictness is a feature.
# - One character may be MORE than one byte ("é" is 2 bytes, "€" is 3 in UTF-8).
#   So len(text) and len(text.encode()) can differ!

print("\n# 0. Text vs Bytes: the core idea")
print("# ------------------------------------")

text = "café €5"
data = text.encode("utf-8")
print("text            :", text, "| type:", type(text).__name__, "| len:", len(text))
print("encoded bytes   :", data, "| type:", type(data).__name__, "| len:", len(data))
print("-> 7 characters became", len(data), "bytes because 'é' takes 2 and '€' takes 3.")
print("round trip back :", data.decode("utf-8"))

# Python never mixes them implicitly:
try:
    print("hello " + b"world")
except TypeError as e:
    print("\nstr + bytes -> TypeError:", e)

# And note: == between str and bytes is simply False (no error, silently!)
print("'abc' == b'abc' :", "abc" == b"abc", "(different types never equal)")
# - Running python with `-b` turns that silent False into a BytesWarning.

# 1. Creating bytes
# ------------------------------------
# - b"literal"       : ASCII characters only inside the literal.
# - bytes(n)         : n zero bytes (NOT the number n as a byte!).
# - bytes([65, 66])  : from an iterable of ints 0..255.
# - "text".encode()  : from text.
# - bytes.fromhex()  : from a hex string like "48 65 6c 6c 6f".
# - Non-ASCII in a b"" literal is a SyntaxError: use \x escapes instead.

print("\n# 1. Creating bytes")
print("# ------------------------------------")

print("a) literal            :", b"Hello")
print("b) bytes(5)           :", bytes(5), "<- five zero bytes, not b'\\x05'")
print("c) bytes([72, 105])   :", bytes([72, 105]))
print("d) 'Hi'.encode()      :", "Hi".encode())
print("e) fromhex            :", bytes.fromhex("48 65 6c 6c 6f"))
print("f) escapes            :", b"\x00\x01\xff", "(non-printable bytes shown as \\x..)")
print("g) empty              :", b"", bytes())

try:
    bytes([256])
except ValueError as e:
    print("\nh) value out of 0..255 -> ValueError:", e)

try:
    eval('b"café"')
except SyntaxError as e:
    print("i) non-ASCII in b'' literal -> SyntaxError:", e.msg)

# 2. Indexing vs Slicing (the int/bytes gotcha)
# ------------------------------------
# - With a str:   s[0] -> 'h'      (a 1-char str)   and s[0:1] -> 'h'
# - With bytes:   b[0] -> 104      (an INT!)        and b[0:1]  -> b'h'
# - Why? A byte has no "character" meaning, so Python gives you the number.
# - To get a 1-byte bytes object, slice: b[0:1], or use bytes([b[0]]).

print("\n# 2. Indexing vs Slicing")
print("# ------------------------------------")

b = b"hello"
print("b[0]    :", b[0], type(b[0]).__name__, "<- an int")
print("b[0:1]  :", b[0:1], type(b[0:1]).__name__, "<- a bytes")
print("b[-1]   :", b[-1])
print("b[1:4]  :", b[1:4])
print("list(b) :", list(b), "<- iterating gives ints too")
print("b[0] == 'h'  :", b[0] == "h", "(int vs str, never equal)")
print("b[0] == ord('h') :", b[0] == ord("h"), "| chr(b[0]) =", chr(b[0]))
print("b[0:1] == b'h'   :", b[0:1] == b"h")

# 3. bytes is immutable, bytearray is mutable
# ------------------------------------
# - bytes: like str/tuple, can't change in place; "edits" make new objects.
# - bytearray: same API plus in-place edits, append, extend, pop, insert...
# - Use bytearray when building/patching a buffer (protocol packets, file
#   chunks) to avoid creating a new bytes object for each change.

print("\n# 3. bytes is immutable, bytearray is mutable")
print("# ------------------------------------")

try:
    b[0] = 72
except TypeError as e:
    print("bytes item assignment -> TypeError:", e)

ba = bytearray(b"hello")
print("\nbytearray        :", ba)
ba[0] = 72                       # assign an INT 0..255
print("ba[0] = 72       :", ba)
ba[1:3] = b"EY"                  # slice assignment with bytes
print("ba[1:3] = b'EY'  :", ba)
ba.append(33)                    # append an int
print("append(33)       :", ba)
ba.extend(b" ok")                # extend with bytes-like
print("extend(b' ok')   :", ba)
last = ba.pop()
print("pop()            :", last, "->", ba)
ba.insert(0, 62)
print("insert(0, 62)    :", ba)
ba += b"?"                       # in-place concat, SAME object
print("+= b'?'          :", ba)
print("freeze to bytes  :", bytes(ba), "| thaw to bytearray:", bytearray(b"x"))

try:
    ba[0] = 300
except ValueError as e:
    print("ba[0] = 300 -> ValueError:", e)

print("bytes  size for 100 items :", sys.getsizeof(bytes(100)), "bytes")
print("bytearray size for 100    :", sys.getsizeof(bytearray(100)), "bytes (extra room to grow)")
print("# Mutability and identity are covered in 12-Mutability-And-Memory-Model.py")

# Why a mutable buffer matters: repeated += on bytes builds a new object each time
n = 5
chunks = [b"ab"] * n
slow = b""
for c in chunks:
    slow += c                    # new bytes object every iteration
fast = bytearray()
for c in chunks:
    fast += c                    # amortised in-place growth
print("\nsame result via bytes+= and bytearray+=:", slow == fast)
print("# For many chunks prefer b''.join(chunks) or a bytearray.")

# 4. Methods that mirror str
# ------------------------------------
# - bytes has most str methods: split, join, replace, strip, find, count,
#   startswith, endswith, upper, lower, isdigit, ...
# - Arguments must ALSO be bytes (b"x", not "x"), else TypeError.
# - No .format() / f-strings for bytes in the str sense. Use b"%d" % 5 (%-style).

print("\n# 4. Methods that mirror str")
print("# ------------------------------------")

line = b"GET /index.html HTTP/1.1"
print("split()             :", line.split())
print("split(b'/', 1)      :", line.split(b"/", 1))
print("b' '.join(...)      :", b" ".join([b"a", b"b", b"c"]))
print("replace             :", line.replace(b"GET", b"POST"))
print("startswith(b'GET')  :", line.startswith(b"GET"))
print("endswith(b'1.1')    :", line.endswith(b"1.1"))
print("find(b'index')      :", line.find(b"index"), "| find(b'zzz'):", line.find(b"zzz"))
print("count(b'/')         :", line.count(b"/"))
print("upper()             :", line.upper())
print("strip               :", b"  pad \n".strip())
print("b'%d items' % 5     :", b"%d items" % 5)
print("b'%s=%s' % (...)    :", b"%s=%s" % (b"k", b"v"))

try:
    line.split(" ")
except TypeError as e:
    print("\nsplit with a str arg -> TypeError:", e)

# 5. hex() and decode() with error handling
# ------------------------------------
# - .hex() turns bytes into a readable hex string (handy for debugging).
# - .decode(encoding, errors=...):
#       "strict"  (default) raise UnicodeDecodeError on invalid bytes
#       "replace" put U+FFFD (the replacement char) in place of bad bytes
#       "ignore"  silently DROP bad bytes (dangerous: hides data loss)
# - The decode must use the SAME encoding the bytes were produced with.

print("\n# 5. hex() and decode() with error handling")
print("# ------------------------------------")

raw = "héllo".encode("utf-8")
print("raw bytes      :", raw)
print("raw.hex()      :", raw.hex())
print("hex with sep   :", raw.hex(" "))

broken = b"caf\xe9"      # 0xE9 is 'é' in latin-1, but invalid on its own in UTF-8
try:
    broken.decode("utf-8")
except UnicodeDecodeError as e:
    print("\nstrict decode -> UnicodeDecodeError:")
    print("   ", e)
print("errors='replace':", broken.decode("utf-8", errors="replace"))
print("errors='ignore' :", broken.decode("utf-8", errors="ignore"), "<- the 'é' vanished silently")
print("right encoding  :", broken.decode("latin-1"), "<- the real fix: use the correct encoding")

# Encoding can fail too:
try:
    "café".encode("ascii")
except UnicodeEncodeError as e:
    print("\n'café'.encode('ascii') -> UnicodeEncodeError:", e.reason)
print("encode errors='replace':", "café".encode("ascii", errors="replace"))
print("encode errors='backslashreplace':", "café".encode("ascii", errors="backslashreplace"))

# 6. Integers <-> bytes (endianness)
# ------------------------------------
# - int.to_bytes(length, byteorder) / int.from_bytes(bytes, byteorder)
# - Endianness = which end of a multi-byte number is stored first.
#       "big"    : most significant byte first    (how we WRITE numbers: 0x0102)
#       "little" : least significant byte first   (how x86/ARM CPUs store them)
#   Network protocols typically use big ("network byte order").
# - If the number doesn't fit in `length` bytes -> OverflowError.
# - Negative numbers need signed=True.

print("\n# 6. Integers <-> bytes (endianness)")
print("# ------------------------------------")

n = 258                                   # 258 = 0x0102 = 1*256 + 2
print("258 big-endian    :", n.to_bytes(2, "big"), "-> [0x01, 0x02]")
print("258 little-endian :", n.to_bytes(2, "little"), "-> [0x02, 0x01]")
print("same bytes, different order, different number:")
print("   from_bytes(b'\\x01\\x02', 'big')    =", int.from_bytes(b"\x01\x02", "big"))
print("   from_bytes(b'\\x01\\x02', 'little') =", int.from_bytes(b"\x01\x02", "little"))
print("sys.byteorder (this machine):", sys.byteorder)

try:
    (256).to_bytes(1, "big")
except OverflowError as e:
    print("\n(256).to_bytes(1) -> OverflowError:", e)
print("(-2).to_bytes(2,'big',signed=True):", (-2).to_bytes(2, "big", signed=True))
print("from_bytes(b'\\xff\\xfe', signed=True):", int.from_bytes(b"\xff\xfe", "big", signed=True))
if sys.version_info >= (3, 11):
    print("Python 3.11+ lets you omit args (length=1, byteorder='big'): (5).to_bytes() ->", (5).to_bytes())
else:
    print("Skipped: (5).to_bytes() with default args needs Python 3.11+")

# 7. struct: packing/unpacking binary records
# ------------------------------------
# - struct converts between Python values and fixed-layout C-like binary records.
# - A FORMAT string describes the layout:
#       first char: byte order  "<" little, ">" big, "!" network(big), "=" native
#       then codes: b/B 1 byte, h/H 2 bytes, i/I 4 bytes, q/Q 8 bytes,
#                   f 4-byte float, d 8-byte float, s N-byte string, ? bool
#   (lowercase = signed, uppercase = unsigned)
# - Always give an explicit byte-order char: otherwise "native" mode adds
#   alignment padding and your file isn't portable.

import struct

print("\n# 7. struct: packing/unpacking binary records")
print("# ------------------------------------")

# Record: id (uint16), temperature (float32), flag (bool), name (4 bytes)
fmt = ">H f ? 4s"
packed = struct.pack(fmt, 42, 36.6, True, b"abcd")
print("format          :", fmt)
print("packed          :", packed)
print("packed hex      :", packed.hex(" "))
print("record size     :", struct.calcsize(fmt), "bytes (len(packed) =", len(packed), ")")

uid, temp, flag, name = struct.unpack(fmt, packed)
print("unpacked        :", (uid, temp, flag, name))
print("note the float  :", temp, "<- float32 can't store 36.6 exactly")

# Native mode pads for alignment: the same fields take MORE bytes
print("\nsize with '<'   :", struct.calcsize("<bi"), "(1 + 4, no padding)")
print("size native '@' :", struct.calcsize("@bi"), "(padding inserted before the int)")

try:
    struct.unpack(">H", b"\x01")
except struct.error as e:
    print("\nwrong buffer size -> struct.error:", e)

# iter_unpack walks many identical records:
stream = struct.pack("<3H", 1, 2, 3)
print("iter_unpack     :", [v[0] for v in struct.iter_unpack("<H", stream)])

# 8. memoryview: zero-copy slicing
# ------------------------------------
# - Slicing bytes/bytearray COPIES the data. For a 100 MB buffer that is slow.
# - memoryview(buf) is a window onto the SAME memory: slicing it copies nothing.
# - Writing through a view of a bytearray changes the bytearray (and vice versa).
# - Caveat: while a view exists, the bytearray can't be resized.

import time

print("\n# 8. memoryview: zero-copy slicing")
print("# ------------------------------------")

buf = bytearray(b"abcdefgh")
view = memoryview(buf)
part = view[2:5]
print("buf               :", buf)
print("view[2:5] as bytes:", bytes(part))

buf[2] = ord("X")                       # modify the UNDERLYING buffer...
print("after buf[2]='X'  :", bytes(part), "<- the view saw the change (shared memory)")
part[0] = ord("Z")                      # ...or modify through the view
print("after part[0]='Z' :", buf, "<- the buffer saw it")

print("view is read-only?:", view.readonly, "| memoryview(b'x').readonly:", memoryview(b"x").readonly)
print("view.obj is buf   :", view.obj is buf)

try:
    buf.append(1)
except BufferError as e:
    print("\nresize while a view exists -> BufferError:", e)
part.release()
view.release()
buf.append(33)                          # fine after releasing
print("after release, append works:", buf)

big = bytearray(50_000_000)             # 50 MB
t0 = time.perf_counter()
copy_slice = big[10:40_000_000]         # copies ~40 MB
t_copy = time.perf_counter() - t0

bigview = memoryview(big)
t0 = time.perf_counter()
view_slice = bigview[10:40_000_000]     # zero-copy
t_view = time.perf_counter() - t0

print("\nslice 40MB of a 50MB bytearray:")
print(f"   bytearray slice : {t_copy * 1000:9.3f} ms, new object size ~{sys.getsizeof(copy_slice) // 1_000_000} MB")
print(f"   memoryview slice: {t_view * 1000:9.3f} ms, new object size  {sys.getsizeof(view_slice)} bytes")
print("   view is much faster:", t_view < t_copy)
del copy_slice, view_slice, bigview, big
# - Typical use: parsing network/file buffers in chunks without copying each chunk.

# 9. base64 and binascii
# ------------------------------------
# - base64 encodes ARBITRARY bytes as safe printable ASCII (4 chars per 3 bytes).
#   Used for e-mail attachments, JSON payloads, data: URLs. It is encoding,
#   NOT encryption: anyone can reverse it.
# - base64 works on bytes and RETURNS bytes: call .decode() for a str.
# - binascii.hexlify is the older spelling of bytes.hex() (but returns bytes).

import base64
import binascii

print("\n# 9. base64 and binascii")
print("# ------------------------------------")

payload = b"\x00\x01binary\xff"
b64 = base64.b64encode(payload)
print("b64encode        :", b64, "| as str:", b64.decode("ascii"))
print("b64decode        :", base64.b64decode(b64))
print("urlsafe variant  :", base64.urlsafe_b64encode(b"\xfb\xff\xfe"), "(uses - and _ instead of + and /)")
print("size overhead    :", len(payload), "->", len(b64), "bytes (~33% bigger)")
print("binascii.hexlify :", binascii.hexlify(b"Hi"), "| same as bytes.hex():", b"Hi".hex())
print("binascii.unhexlify:", binascii.unhexlify("4869"), "| same as bytes.fromhex")

try:
    base64.b64decode("not base64!!", validate=True)
except binascii.Error as e:
    print("\nbad base64 with validate=True -> binascii.Error:", e)

# 10. Hashing and comparing bytes
# ------------------------------------
# - bytes is immutable => hashable => OK as dict key / set member.
# - bytearray is mutable => NOT hashable (same rule as list).
# - bytes compare lexicographically by byte value, like str.
# - bytes == bytearray compares content (so b"a" == bytearray(b"a") is True).

print("\n# 10. Hashing and comparing bytes")
print("# ------------------------------------")

cache = {b"key1": "value1"}
cache[b"key2"] = "value2"
print("bytes as dict keys:", cache, "| lookup:", cache[b"key1"])

try:
    {bytearray(b"k"): 1}
except TypeError as e:
    print("bytearray as key -> TypeError:", e)

print("b'abc' < b'abd'       :", b"abc" < b"abd")
print("b'a' == bytearray(b'a'):", b"a" == bytearray(b"a"))
print("b'a' in b'cat'        :", b"a" in b"cat", "| 97 in b'cat' (int):", 97 in b"cat")
print("hash stable in-run    :", hash(b"x") == hash(b"x"))
print("# Hash values of bytes/str change between runs (PYTHONHASHSEED), never store them.")

# 11. Binary files: why open(..., 'rb') gives bytes
# ------------------------------------
# - Text mode ('r'/'w'): Python DECODES on read / ENCODES on write using an
#   encoding (always pass encoding="utf-8" explicitly!) and translates newlines.
# - Binary mode ('rb'/'wb'): no decoding, no newline translation. You get the
#   raw bytes, which is the ONLY truthful view of a file: images, zips, pdfs.
# - Text mode on a binary file will usually crash with UnicodeDecodeError or,
#   worse, silently corrupt data.
# - See 05-Python Advanced for more on file handling and context managers.

import os
import tempfile

print("\n# 11. Binary files: why open(..., 'rb') gives bytes")
print("# ------------------------------------")

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "sample.bin")

    header = struct.pack(">4sH", b"DEMO", 1)          # magic + version
    body = bytes(range(0, 256, 51))                   # 0, 51, 102, 153, 204, 255
    with open(path, "wb") as f:                       # write bytes, not str
        f.write(header)
        f.write(body)

    with open(path, "rb") as f:
        content = f.read()
    print("file size on disk :", os.path.getsize(path), "bytes")
    print("read in 'rb'      :", content, "| type:", type(content).__name__)

    magic, version = struct.unpack(">4sH", content[:6])
    print("parsed header     :", magic, version)
    print("body values       :", list(content[6:]))

    with open(path, "rb") as f:
        f.seek(4)                                     # jump to the version field
        raw_version = f.read(2)
        print("seek(4) + read(2) :", raw_version, "->", int.from_bytes(raw_version, "big"))

    try:
        with open(path, "r", encoding="utf-8") as f:  # WRONG mode for binary data
            f.read()
    except UnicodeDecodeError as e:
        print("\nreading binary in text mode -> UnicodeDecodeError:", e.reason)

    # readinto: fill a pre-allocated bytearray, no new bytes objects per read
    scratch = bytearray(4)
    with open(path, "rb") as f:
        n_read = f.readinto(scratch)
    print("readinto          :", n_read, "bytes ->", scratch)

    try:
        with open(path, "wb") as f:                   # NOTE: 'wb' truncates the file at open()!
            f.write("text")                           # str into a binary file
    except TypeError as e:
        print("write(str) to 'wb' file -> TypeError:", e)
    print("file size after the failed 'wb' open:", os.path.getsize(path), "(opening with 'w'/'wb' already emptied it)")
# The temp directory (and the file) is removed automatically on leaving the `with`.
print("temp dir cleaned up:", not os.path.exists(path))

# 12. bytes vs str in subprocess / sockets
# ------------------------------------
# - Anything that talks to the OUTSIDE world (sockets, pipes, subprocess output,
#   hashlib, os.read) speaks bytes. YOU choose where to encode/decode.
# - subprocess.run(..., capture_output=True) -> stdout is bytes by default.
#   Add text=True (or encoding="utf-8") to get str.
# - socket.send/recv always use bytes: sock.send("hi") is a TypeError.
# - hashlib.sha256("text") is a TypeError: hash the .encode()d bytes.
# - Good habit ("Unicode sandwich"): decode bytes to str AT THE EDGE when data
#   comes in, work with str inside your program, encode AT THE EDGE going out.

import hashlib
import subprocess

print("\n# 12. bytes vs str in subprocess / sockets")
print("# ------------------------------------")

result = subprocess.run([sys.executable, "-c", "print('héllo')"], capture_output=True)
print("subprocess stdout (default):", result.stdout, "<- bytes")
print("decoded                    :", result.stdout.decode("utf-8").strip())

result_text = subprocess.run(
    [sys.executable, "-c", "print('héllo')"],
    capture_output=True, text=True, encoding="utf-8",
)
print("with text=True             :", repr(result_text.stdout), "<- str")

try:
    hashlib.sha256("text")
except TypeError as e:
    print("\nhashlib.sha256(str) -> TypeError:", e)
print("sha256(b'text')[:16]       :", hashlib.sha256(b"text").hexdigest()[:16], "...")

# socketpair gives two connected sockets without any network access
import socket
a, b2 = socket.socketpair()
a.sendall("ping".encode("utf-8"))                     # must be bytes
print("socket recv                :", b2.recv(16), "<- bytes")
try:
    a.send("ping")
except TypeError as e:
    print("sock.send(str) -> TypeError:", e)
a.close()
b2.close()

print("\n# Recap: str = text, bytes = raw data. Encode/decode at the edges,")
print("# bytearray when you need to edit, memoryview when you must not copy,")
print("# struct/int.from_bytes for binary formats, 'rb'/'wb' for binary files.")
print("\n# End of bytes & bytearray Explanation")
