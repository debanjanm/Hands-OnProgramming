# 01. What an ndarray Really Is
# 02. Strides
# 03. C Order vs Fortran Order
# 04. Contiguity Flags
# 05. Views vs Copies
# 06. Checking Memory Sharing
# 07. Transpose, Reshape and Hidden Copies
# 08. as_strided and sliding_window_view
# 09. dtype Internals
# 10. view(dtype) vs astype
# 11. Casting Rules
# 12. Integer Overflow and Wraparound
# 13. Float Precision and eps
# 14. nan and inf
# 15. np.errstate
# 16. Memory Cost
# 17. np.frombuffer
# 18. memmap
# 19. nditer Basics
# 20. Cross-References
#
# Related: 01 (array basics), 03 (reshape), 04 (broadcasting - uses stride 0 trick),
# 08 (performance), 09 (file IO).

import os
import tempfile

import numpy as np
from numpy.lib.stride_tricks import as_strided, sliding_window_view

# 01. What an ndarray Really Is
# ----------------------------
# - An ndarray = ONE flat block of bytes + a small header that says how to read it.
# - The header holds: dtype, shape, strides, and flags.
# - Same bytes can be read in many ways (transpose, slice, reshape) by only
#   changing the header. That is why views are cheap.

a = np.arange(12, dtype=np.int32).reshape(3, 4)
print("a =\n", a)
print("shape =", a.shape, ", dtype =", a.dtype, ", itemsize =", a.itemsize, "bytes")
print("size =", a.size, ", nbytes =", a.nbytes, "(size * itemsize)")
print("ndim =", a.ndim)
print("# Gotcha: nbytes counts only the data buffer, not the small header object.")
print()

# 02. Strides
# ----------------------------
# - strides = how many BYTES to jump to reach the next element along each axis.
# - For a C-order int32 (3, 4): next column = 4 bytes, next row = 4 * 4 = 16 bytes.
# - Address of a[i, j] = start + i * strides[0] + j * strides[1].

print("a.strides =", a.strides, "(row jump, column jump) in bytes")
print("a.T.strides =", a.T.strides, "(transpose just swaps the strides - no data moved)")
print("a[:, ::2].strides =", a[:, ::2].strides, "(every 2nd column -> column jump doubles)")
print("a[::2].strides =", a[::2].strides, "(every 2nd row -> row jump doubles)")
b = np.arange(5, dtype=np.int64)
print("b[::-1].strides =", b[::-1].strides, "(negative stride = reading backwards)")
print("# Gotcha: strides are in BYTES, not elements. Divide by itemsize for element steps.")
print()

# 03. C Order vs Fortran Order
# ----------------------------
# - C order ('C', row-major): last axis changes fastest in memory.
# - Fortran order ('F', column-major): first axis changes fastest.
# - Same logical array, different memory layout. Indexing results are identical.

c = np.arange(6, dtype=np.int32).reshape(2, 3)
f = np.asfortranarray(c)
print("c (C order) =\n", c)
print("f (F order) =\n", f)
print("equal as arrays:", np.array_equal(c, f))
print("c.strides =", c.strides, ", f.strides =", f.strides)
print("memory of c:", c.ravel(order="K"), "(order='K' = as laid out in memory)")
print("memory of f:", f.ravel(order="K"))
print("f.ravel('C') =", f.ravel("C"), ", f.ravel('F') =", f.ravel("F"))
print("np.zeros((2,3), order='F').flags.f_contiguous =", np.zeros((2, 3), order="F").flags.f_contiguous)
print("reshape with order='F':", np.arange(6).reshape(2, 3, order="F").tolist())
print("# Gotcha: reshape/ravel read elements in C order by default, whatever the memory layout is.")
print("#   order='F' changes the READING order, not the memory.")
print()

# 04. Contiguity Flags
# ----------------------------
# - flags.c_contiguous / f_contiguous say whether the data is one unbroken block
#   in that order. Slicing with a step or taking columns usually breaks it.
# - Many fast C routines (and np.frombuffer / .view) need contiguous data.

print("a C/F contiguous:", a.flags.c_contiguous, a.flags.f_contiguous)
print("a.T C/F contiguous:", a.T.flags.c_contiguous, a.T.flags.f_contiguous)
print("a[:, :2] C/F contiguous:", a[:, :2].flags.c_contiguous, a[:, :2].flags.f_contiguous)
print("a[::2] C contiguous:", a[::2].flags.c_contiguous)
print("a[0] (one row) C contiguous:", a[0].flags.c_contiguous)
print("1-D b is both C and F contiguous:", b.flags.c_contiguous, b.flags.f_contiguous)
print("a.flags.owndata =", a.flags.owndata, ", a[:2].flags.owndata =", a[:2].flags.owndata)
print("a.flags.writeable =", a.flags.writeable)
d = np.ascontiguousarray(a.T)
print("np.ascontiguousarray(a.T) C contiguous:", d.flags.c_contiguous, "(made a real copy)")
print("# Gotcha: a.T of a C array is F-contiguous, not C-contiguous. Looping over it row by row")
print("#   jumps around memory and is slower on big arrays (cache misses).")
print()

# 05. Views vs Copies
# ----------------------------
# - VIEW: new header, SAME data buffer. Writing through a view changes the original.
# - COPY: new data buffer. Independent.
# - Basic slicing (a[1:3], a[:, 0], a[::2]), .T, .reshape (when possible), .view(), .ravel()
#   (when possible) -> views.
# - Fancy (integer-array) indexing, boolean masks, .copy(), .flatten(), astype -> copies.

x = np.arange(6)
v = x[1:4]
v[0] = 100
print("x after v[0]=100 (slice is a view):", x)
fancy = x[[1, 2, 3]]
fancy[0] = -1
print("x after fancy[0]=-1 (fancy index is a copy):", x)
mask_copy = x[x > 3]
mask_copy[:] = 0
print("x after writing to boolean-mask result:", x)
print("v.base is x:", v.base is x, ", x.base is None:", x.base is None)
print("x.flatten() is a copy, x.ravel() is a view when possible:",
      x.flatten().base is None, x.ravel().base is x)
# Writing INTO a fancy-indexed target does modify the original (it is an assignment).
x[[0, 1]] = 7
print("x after x[[0,1]] = 7 (assignment form works):", x)
print("# Gotcha: a[idx] = value modifies a, but b = a[idx]; b[...] = value does NOT.")
print("#   Chained fancy assignment like a[[0,1]][0] = 5 silently writes to a temporary copy.")
t = np.arange(4)
t[[0, 1]][0] = 55
print("t after t[[0,1]][0] = 55:", t, "(unchanged - the write went to a temporary)")
print()

# 06. Checking Memory Sharing
# ----------------------------
# - arr.base: the array that owns the memory (None if arr owns its data).
# - np.shares_memory(a, b): exact answer (can be slow for odd layouts).
# - np.may_share_memory(a, b): fast bounds check only - may say True when the
#   arrays interleave but never actually overlap.

base = np.arange(10)
ev = base[::2]
od = base[1::2]
print("np.shares_memory(base, ev):", np.shares_memory(base, ev))
print("np.shares_memory(ev, od):", np.shares_memory(ev, od), "(interleaved, no real overlap)")
print("np.may_share_memory(ev, od):", np.may_share_memory(ev, od), "(only compares memory bounds)")
print("np.shares_memory(base, base.copy()):", np.shares_memory(base, base.copy()))
print("ev.base is base:", ev.base is base)
vv = ev[1:]
print("view of a view: vv.base is base:", vv.base is base, "(base always points to the owner)")
print("# Gotcha: .base is None does NOT mean 'copy' for sure - np.arange(...).reshape(...) has a base")
print("#   but np.array(x) has none. Prefer np.shares_memory when you need a real answer.")
print()

# 07. Transpose, Reshape and Hidden Copies
# ----------------------------
# - .T and swapaxes are always views (strides swapped).
# - reshape returns a view IF the strides allow it, otherwise silently copies.
# - ravel() same rule; flatten() always copies.
# - Setting arr.shape = ... instead of reshape raises an error if a copy would be needed.

m = np.arange(6).reshape(2, 3)
print("m.T is a view:", np.shares_memory(m, m.T))
print("m.reshape(3,2) is a view:", np.shares_memory(m, m.reshape(3, 2)))
print("m.T.reshape(6) is a view:", np.shares_memory(m, m.T.reshape(6)), "(needs a copy)")
print("m.T.ravel() =", m.T.ravel(), "(copy made silently)")
try:
    mt = m.T
    mt.shape = (6,)
except AttributeError as e:
    print("m.T.shape = (6,) ->", type(e).__name__, ":", str(e)[:60])
print("# Gotcha: whether reshape gives a view or copy depends on the layout, so never rely on")
print("#   'reshape then write' to modify the original. Check np.shares_memory if it matters.")
print()

# 08. as_strided and sliding_window_view
# ----------------------------
# - as_strided(x, shape, strides) builds ANY view you describe - no safety checks.
# - Wrong shape/strides = reads memory outside the array = garbage or crash. Use with care.
# - sliding_window_view(x, window) is the SAFE read-only version for rolling windows.
# - Broadcasting itself is the stride-0 trick: np.broadcast_to makes a read-only view.

s = np.arange(6, dtype=np.int64)
manual = as_strided(s, shape=(4, 3), strides=(s.strides[0], s.strides[0]))
print("as_strided windows of length 3:\n", manual)
safe = sliding_window_view(s, 3)
print("sliding_window_view(s, 3):\n", safe)
print("same result:", np.array_equal(manual, safe))
print("rolling mean (window 3):", safe.mean(axis=1))
print("window view is read-only:", not safe.flags.writeable)
print("2-D windows shape:", sliding_window_view(np.arange(16).reshape(4, 4), (2, 2)).shape)
bt = np.broadcast_to(np.array([1, 2, 3]), (4, 3))
print("broadcast_to strides:", bt.strides, "(row stride 0 = same row reused), writeable:", bt.flags.writeable)
print("# Gotcha: windows overlap, so many 'rows' share the same bytes. Never write into an")
print("#   as_strided view; a single write changes several windows.")
print()

# 09. dtype Internals
# ----------------------------
# - dtype describes how to read bytes: kind, size, byte order.
# - kind codes: 'i' signed int, 'u' unsigned, 'f' float, 'c' complex, 'b' bool,
#   'U' str, 'M' datetime64, 'm' timedelta64, 'O' object.
# - byteorder: '<' little endian, '>' big endian, '=' native, '|' not applicable.
# - itemsize = bytes per element.

for dt in (np.int8, np.uint16, np.int32, np.float32, np.float64, np.complex128, np.bool_):
    t_ = np.dtype(dt)
    print(f"{t_.name:<11} kind={t_.kind!r} itemsize={t_.itemsize} char={t_.char!r}")
little = np.dtype("<i4")
big = np.dtype(">i4")
print("'<i4' byteorder:", little.byteorder, ", '>i4' byteorder:", big.byteorder)
arr_big = np.array([1, 256], dtype=">i4")
print("big-endian bytes of [1, 256]:", arr_big.tobytes().hex())
arr_little = np.array([1, 256], dtype="<i4")
print("little-endian bytes of [1, 256]:", arr_little.tobytes().hex())
print("values equal despite different bytes:", np.array_equal(arr_big, arr_little))
print("np.dtype('U5').itemsize =", np.dtype("U5").itemsize, "(4 bytes per char)")
print("np.dtype('S5').itemsize =", np.dtype("S5").itemsize, "(1 byte per char)")
print("np.dtype('O').itemsize is a pointer size - object arrays hold references, not values.")
print("np.iinfo(np.int16):", np.iinfo(np.int16).min, "to", np.iinfo(np.int16).max)
print("np.iinfo(np.uint8):", np.iinfo(np.uint8).min, "to", np.iinfo(np.uint8).max)
print("# Gotcha: np.int_ / default integer size depends on platform (64-bit on most Linux/macOS,")
print("#   32-bit on older Windows builds). Always name the dtype when size matters.")
print()

# 10. view(dtype) vs astype
# ----------------------------
# - astype(new): CONVERTS the values (makes a copy).
# - view(new): REINTERPRETS the same bytes as another dtype (no copy, shape may change).
# - view needs compatible sizes and a contiguous last axis.

fl = np.array([1.0, 2.0], dtype=np.float32)
print("astype(int32):", fl.astype(np.int32), "(values converted)")
print("view(int32):", fl.view(np.int32), "(raw bit patterns of the floats)")
print("float32 1.0 in hex bits:", hex(int(fl.view(np.uint32)[0])))
u8 = np.array([1, 0, 0, 0, 2, 0, 0, 0], dtype=np.uint8)
print("uint8 x8 viewed as int32:", u8.view("<i4"), "(shape changed: 8 -> 2)")
print("view shares memory:", np.shares_memory(u8, u8.view("<i4")))
print("astype shares memory:", np.shares_memory(fl, fl.astype(np.int32)))
print("astype(copy=False) same dtype reuses the array:", fl.astype(np.float32, copy=False) is fl)
print("# Gotcha: .view(np.int32) on float data does NOT round numbers. It exposes raw bits.")
print("#   Use astype for value conversion, view only when you mean 'same bytes, new meaning'.")
print()

# 11. Casting Rules
# ----------------------------
# - np.result_type tells what dtype an operation will produce.
# - Mixing int and float -> float. Mixing bool and int -> int.
# - Python scalars are "weak" in NumPy 1.x value-based casting: int8_array + 1000 may upcast.
# - astype(..., casting='safe') refuses lossy conversions; default for astype is 'unsafe'.
# - np.can_cast checks without doing it.

print("result_type(int8, int16):", np.result_type(np.int8, np.int16))
print("result_type(int32, float32):", np.result_type(np.int32, np.float32), "(float32 can't hold all int32)")
print("result_type(int64, float32):", np.result_type(np.int64, np.float32))
print("result_type(bool, int8):", np.result_type(np.bool_, np.int8))
print("result_type(uint8, int8):", np.result_type(np.uint8, np.int8), "(signed + unsigned -> bigger signed)")
print("can_cast(int32 -> float64, 'safe'):", np.can_cast(np.int32, np.float64, "safe"))
print("can_cast(float64 -> int32, 'safe'):", np.can_cast(np.float64, np.int32, "safe"))
print("can_cast(float64 -> int32, 'same_kind'):", np.can_cast(np.float64, np.int32, "same_kind"))
try:
    np.array([1.5, 2.5]).astype(np.int32, casting="safe")
except TypeError as e:
    print("astype(casting='safe') ->", type(e).__name__)
print("float -> int truncates toward zero:", np.array([1.9, -1.9]).astype(np.int32))
print("int8 array + 1 stays:", (np.array([1], dtype=np.int8) + 1).dtype)
print("int8 array + 1000 (value-based, NumPy 1.x):", (np.array([1], dtype=np.int8) + 1000).dtype)
print("true division of ints gives:", (np.array([4, 2], dtype=np.int32) / 2).dtype)
print("# Gotcha: casting rules for Python scalars changed in NumPy 2.0 (NEP 50). On 1.26 the")
print("#   value decides the type; on 2.x the array dtype wins and 1000 would overflow int8.")
print()

# 12. Integer Overflow and Wraparound
# ----------------------------
# - Fixed-size integers WRAP AROUND silently with no error (array math).
# - Python ints never overflow, so lists and arrays behave differently.
# - Use a bigger dtype (or float) for sums, products and accumulators.

u = np.array([250, 255], dtype=np.uint8)
print("uint8 [250, 255] + 10 =", u + np.uint8(10), "(wraps past 255)")
i = np.array([127], dtype=np.int8)
print("int8 127 + 1 =", i + np.int8(1), "(wraps to -128)")
print("uint8 0 - 1 =", np.array([0], dtype=np.uint8) - np.uint8(1))
print("int8 abs(-128) =", np.abs(np.array([-128], dtype=np.int8)), "(no +128 in int8)")
img = np.array([200, 100], dtype=np.uint8)
print("uint8 sum of [200, 100] with default accumulator:", img.sum(), ", dtype:", img.sum().dtype.kind)
print("uint8 sum with dtype=np.uint8:", img.sum(dtype=np.uint8), "(wrapped: 300 - 256)")
print("uint8 mean (uses float64 internally):", img.mean())
print("uint8 [200] * 2 =", np.array([200], dtype=np.uint8) * np.uint8(2))
big_prod = np.array([3_000_000_000], dtype=np.int64) * 4
print("int64 3e9 * 4 =", big_prod, "(fine in int64)")
print("int32 same:", np.array([3_000_000_000 // 3], dtype=np.int32) * np.int32(4), "(wrapped - 1e9*4 > 2^31)")
print("python int 2**64 + 1 =", 2**64 + 1)
try:
    np.array([2**64])
    print("np.array([2**64]).dtype =", np.array([2**64]).dtype, "(falls back to object)")
except OverflowError as e:
    print("OverflowError:", e)
print("# Gotcha: image arithmetic in uint8 (brightness + 50) wraps instead of clipping. Cast to")
print("#   int16/float first, then np.clip(..., 0, 255).astype(np.uint8).")
print()

# 13. Float Precision and eps
# ----------------------------
# - float64 has ~15-16 decimal digits, float32 ~7. np.finfo tells the limits.
# - eps = gap between 1.0 and the next float. Not a general 'error size' - gaps grow with magnitude.
# - Never test floats with ==. Use np.isclose / np.allclose.

print("0.1 + 0.2 == 0.3:", 0.1 + 0.2 == 0.3)
print("np.isclose(0.1 + 0.2, 0.3):", np.isclose(0.1 + 0.2, 0.3))
print("float64 eps:", np.finfo(np.float64).eps)
print("float32 eps:", np.finfo(np.float32).eps)
print("float64 max:", np.finfo(np.float64).max)
print("float64 smallest normal:", np.finfo(np.float64).tiny)
print("float32 1e8 + 1 == 1e8:", np.float32(1e8) + np.float32(1) == np.float32(1e8), "(1 is below the gap)")
print("float64 1e16 + 1 == 1e16:", 1e16 + 1 == 1e16)
print("np.spacing(1.0):", np.spacing(1.0), ", np.spacing(1e10):", np.spacing(1e10))
print("np.nextafter(1.0, 2.0) - 1.0:", np.nextafter(1.0, 2.0) - 1.0)
print("float32(0.1) printed as float64:", float(np.float32(0.1)))
tiny = np.full(10**5, 0.1, dtype=np.float32)
print("sum of 1e5 float32 0.1 (pairwise summation):", float(tiny.sum()), "vs exact 10000.0")
print("allclose with rtol/atol:", np.allclose([1.0, 1e-9], [1.0 + 1e-9, 0.0], rtol=1e-5, atol=1e-8))
print("np.round(2.5), np.round(3.5), np.round(-0.5):", np.round(2.5), np.round(3.5), np.round(-0.5), "(banker's rounding)")
print("# Gotcha: isclose is not symmetric and atol matters near 0. isclose(1e-10, 0) is True by")
print("#   default atol=1e-8, which may be too loose for tiny-scale data.")
print()

# 14. nan and inf
# ----------------------------
# - nan = 'not a number' (undefined result). inf = overflow or division by zero.
# - nan != nan, so use np.isnan. Any arithmetic with nan gives nan.
# - nan is a float; integer arrays cannot hold it.

n = np.array([1.0, np.nan, 3.0, np.inf])
print("n =", n)
print("nan == nan:", np.nan == np.nan)
print("np.isnan(n):", np.isnan(n))
print("np.isinf(n):", np.isinf(n))
print("np.isfinite(n):", np.isfinite(n))
print("n.sum():", n.sum(), ", np.nansum(n):", np.nansum(n))
print("np.nanmax(n[np.isfinite(n)]):", np.nanmax(n[np.isfinite(n)]))
print("max with nan:", np.max(np.array([1.0, np.nan])), "| np.fmax:", np.fmax(1.0, np.nan))
print("inf - inf:", np.inf - np.inf, ", inf * 0:", np.inf * 0, ", 1/inf:", 1 / np.inf)
print("nan in a comparison:", np.nan < 1, ", np.nan > 1:", np.nan > 1)
print("np.nan_to_num(n):", np.nan_to_num(n, nan=0.0, posinf=999.0))
print("-0.0 == 0.0:", -0.0 == 0.0, ", np.signbit(-0.0):", np.signbit(-0.0))
print("np.unique treats nans as equal (1.21+):", np.unique(np.array([np.nan, np.nan, 1.0])))
try:
    np.array([1, 2, 3], dtype=np.int32)[0] = np.nan
except ValueError as e:
    print("int array = nan ->", type(e).__name__)
print("# Gotcha: nan in a boolean mask silently makes the comparison False: arr > 0 drops nan rows.")
print("#   Use ~np.isnan(arr) deliberately when cleaning data.")
print()

# 15. np.errstate
# ----------------------------
# - NumPy float errors (divide by zero, overflow, underflow, invalid) give a warning
#   and keep going. np.errstate sets what to do inside a with-block.
# - Choices: 'ignore', 'warn', 'raise', 'call', 'print', 'log'.
# - Integer division by zero is a separate case (also warns, returns 0).

x0 = np.array([1.0, 0.0])
with np.errstate(divide="ignore", invalid="ignore"):
    print("1/[1,0] ignoring errors:", 1.0 / x0)
    print("0/0:", np.float64(0.0) / np.float64(0.0))
try:
    with np.errstate(divide="raise"):
        1.0 / x0
except FloatingPointError as e:
    print("divide='raise' ->", type(e).__name__, ":", e)
try:
    with np.errstate(over="raise"):
        np.float32(3e38) * np.float32(10)
except FloatingPointError as e:
    print("over='raise' ->", e)
with np.errstate(all="ignore"):
    print("int divide by zero ignored:", np.array([5], dtype=np.int32) // np.array([0], dtype=np.int32))
print("np.geterr() default keys:", sorted(np.geterr()))
print("# Gotcha: errstate is per-thread and only for floating point. Integer overflow never")
print("#   triggers it (see section 12). Use np.seterr(all='raise') in tests to catch bugs early.")
print()

# 16. Memory Cost
# ----------------------------
# - Memory = number of elements * itemsize. Pick the smallest dtype that fits the data.
# - Intermediate temporaries cost too: a*b+c builds a*b first.
# - In-place ops (out=, +=) avoid temporaries.

n_items = 1_000_000
for dt in (np.float64, np.float32, np.float16, np.int8, np.bool_):
    print(f"{n_items} x {np.dtype(dt).name:<8}: {np.dtype(dt).itemsize * n_items / 1e6:.1f} MB")
print("object arrays store one pointer per slot PLUS the Python objects themselves - far heavier than int64.")
print("a.T.nbytes =", a.T.nbytes, "(logical size - a view allocates no new data, yet nbytes still reports it)")
w = np.ones(5)
w2 = w * 2
before = w
w *= 2
print("w *= 2 keeps the same array object:", before is w, "| w * 2 builds a new one:", w2 is not w)
out = np.empty(5)
np.add(w, w, out=out)
print("np.add(..., out=out) =", out)
print("float16 range max:", np.finfo(np.float16).max, ", eps:", np.finfo(np.float16).eps)
print("# Gotcha: a huge np.zeros((100000, 100000)) may succeed instantly (lazy pages) and then")
print("#   crash when you write to it. Estimate nbytes BEFORE allocating.")
print()

# 17. np.frombuffer
# ----------------------------
# - np.frombuffer(buf, dtype) wraps existing bytes WITHOUT copying.
# - From bytes -> read-only. From bytearray -> writable and linked to the buffer.
# - Compare np.fromstring (deprecated for binary) - use frombuffer.

raw = (1).to_bytes(4, "little") + (2).to_bytes(4, "little") + (3).to_bytes(4, "little")
fb = np.frombuffer(raw, dtype="<i4")
print("frombuffer(bytes):", fb, ", writeable:", fb.flags.writeable)
ba = bytearray(raw)
fw = np.frombuffer(ba, dtype="<i4")
fw[0] = 99
print("frombuffer(bytearray) after write:", fw, "| bytearray first 4 bytes:", list(ba[:4]))
print("count/offset: ", np.frombuffer(raw, dtype="<i4", count=2, offset=4))
print("tobytes round trip:", np.array_equal(np.frombuffer(np.arange(4, dtype="<f8").tobytes(), dtype="<f8"), np.arange(4)))
print("memoryview of array has shape:", memoryview(np.arange(6, dtype=np.int32).reshape(2, 3)).shape)
try:
    np.frombuffer(b"\x00\x01\x02", dtype="<i4")
except ValueError as e:
    print("bad length ->", type(e).__name__, ":", str(e))
print("# Gotcha: the result keeps the source buffer alive and linked. Changing the bytearray")
print("#   changes the array. Use .copy() if you want independence.")
print()

# 18. memmap
# ----------------------------
# - np.memmap maps a FILE as an array; only pages you touch are loaded.
# - Good for arrays bigger than RAM. Modes: 'r' read, 'r+' read/write, 'w+' create, 'c' copy-on-write.
# - Always flush() or delete the object so data reaches disk.
# - Compare with 09 (file IO): np.save/np.load reads everything into memory.

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "data.dat")
    mm = np.memmap(path, dtype="<f4", mode="w+", shape=(4, 3))
    mm[:] = np.arange(12, dtype=np.float32).reshape(4, 3)
    mm[1, 1] = -1.0
    mm.flush()
    print("memmap shape/dtype:", mm.shape, mm.dtype, ", file size bytes:", os.path.getsize(path), "(4*3*4 = 48)")
    del mm
    ro = np.memmap(path, dtype="<f4", mode="r", shape=(4, 3))
    print("read back:\n", ro)
    print("is ndarray subclass:", isinstance(ro, np.ndarray), ", writeable:", ro.flags.writeable)
    part = np.memmap(path, dtype="<f4", mode="r", offset=12, shape=(2,))
    print("offset=12 bytes skips 3 floats:", part)
    cow = np.memmap(path, dtype="<f4", mode="c", shape=(4, 3))
    cow[0, 0] = 777.0
    print("copy-on-write changed memory only:", cow[0, 0], "| file still has:", ro[0, 0])
    print("np.fromfile alternative:", np.fromfile(path, dtype="<f4")[:4])
    del ro, part, cow
print("temp directory removed after the with-block.")
print("# Gotcha: you MUST give dtype and shape yourself - the file has no header. A wrong dtype")
print("#   gives silent garbage. On Windows an open memmap blocks deleting the file.")
print()

# 19. nditer Basics
# ----------------------------
# - np.nditer walks array elements efficiently, handling broadcasting and memory order.
# - Default iteration order is 'K' = memory order (fastest), not necessarily C order.
# - Use flags=['multi_index'] to get indexes, op_flags=['readwrite'] to modify.
# - For most jobs ufuncs or np.ndenumerate are simpler; nditer is the low-level tool.

g = np.arange(6).reshape(2, 3)
print("C-order iteration:", [int(v_) for v_ in np.nditer(g, order="C")])
print("F-order iteration:", [int(v_) for v_ in np.nditer(g, order="F")])
print("default on g.T (memory order):", [int(v_) for v_ in np.nditer(g.T)], "vs g.T.ravel():", g.T.ravel().tolist())
it = np.nditer(g, flags=["multi_index"])
print("with multi_index:", [(it.multi_index, int(v_)) for v_ in it])
h = np.arange(4)
with np.nditer(h, op_flags=["readwrite"]) as it2:
    for cell in it2:
        cell[...] = cell * 10
print("modified in place:", h)
print("two operands broadcast together:", [(int(p), int(q)) for p, q in np.nditer([np.arange(3), np.array([[10], [20]])])])
print("ndenumerate:", [(idx, int(v_)) for idx, v_ in np.ndenumerate(np.array([[5, 6], [7, 8]]))])
print("# Gotcha: nditer's default order can differ from what you expect for transposed arrays.")
print("#   Pass order='C' when the order matters. In a Python loop it is still slow - prefer ufuncs.")
print()

# 20. Cross-References
# ----------------------------
# - 03-Reshaping-And-Manipulation: reshape/ravel/transpose (here: when they copy).
# - 04-Operations-And-Broadcasting: broadcasting (here: stride 0 behind it).
# - 08-Performance-And-Vectorization: speed (here: why layout and dtype affect it).
# - 09-File-IO: save/load (here: memmap and frombuffer for raw files).
# - 12-Advanced-Indexing-Ufuncs-And-Sorting: take/put and ufunc methods with out=.

print("Quick checklist: shape, dtype, strides, flags.owndata, np.shares_memory - five questions that explain most surprises.")
