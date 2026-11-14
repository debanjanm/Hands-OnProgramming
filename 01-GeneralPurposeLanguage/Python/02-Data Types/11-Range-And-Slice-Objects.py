## 0.  range is a lazy immutable sequence (not a list)
## 1.  range() forms and off-by-one rules
## 2.  What a range can do: len, index, count, reversed, equality
## 3.  Slicing a range gives a range
## 4.  Why range(1.5) fails (and what to use instead)
## 5.  Slicing rules for sequences
## 6.  slice objects and .indices()
## 7.  Naming slices: fixed-width record parsing
## 8.  Slice assignment and deletion on lists
## 9.  Slices copy (shallowly), strings/tuples are immutable
## 10. Ellipsis (...) briefly
## 11. A custom class whose __getitem__ accepts ints AND slices
## 12. operator.index
## 13. itertools.islice: slicing things you can't index

# Python range & slice Explanation

import sys
import time

# 0. range is a lazy immutable sequence (not a list)
# ------------------------------------
# - range(...) does NOT build the numbers. It stores only start, stop, step
#   (three ints) and computes item i as  start + i*step  on demand.
# - So range(10**12) costs the same memory and time as range(5).
# - It is a real Sequence: supports len(), indexing, slicing, `in`, reversed(),
#   .index(), .count(), and is immutable and hashable.
# - Unlike a generator, a range can be iterated again and again.
# - Python 2 had a list-building range() and a lazy xrange(). Python 3's
#   range IS xrange.

print("\n# 0. range is a lazy immutable sequence (not a list)")
print("# ------------------------------------")

r = range(10**12)                       # a trillion numbers: instant
print("range(10**12)            :", r)
print("len(r)                   :", len(r))
print("r[999_999_999_999]       :", r[999_999_999_999])
print("sys.getsizeof(range(5))  :", sys.getsizeof(range(5)), "bytes")
print("sys.getsizeof(range(10**12)):", sys.getsizeof(range(10**12)), "bytes  <- same! only 3 ints stored")
print("sys.getsizeof(list(range(1000))):", sys.getsizeof(list(range(1000))), "bytes (the list pays for every slot)")

# Membership is O(1) ARITHMETIC for int ranges, not a scan:
#   x in range(a, b, s)  <=>  a <= x < b and (x - a) % s == 0
N = 1_000_000
as_range = range(N)
as_list = list(range(N))
target = N - 1                          # worst case for the list: the last item

t0 = time.perf_counter()
for _ in range(20):
    target in as_list                   # scans up to a million items each time
t_list = time.perf_counter() - t0

t0 = time.perf_counter()
for _ in range(20):
    target in as_range                  # one comparison + one modulo
t_range = time.perf_counter() - t0

print(f"\n'{target} in list'  x20 : {t_list * 1000:10.4f} ms   (linear scan)")
print(f"'{target} in range' x20 : {t_range * 1000:10.4f} ms   (arithmetic)")
print("range membership faster :", t_range < t_list)
print("10**15 in range(10**18) :", 10**15 in range(10**18), "(instant, no scan)")
print("7 in range(0, 100, 5)   :", 7 in range(0, 100, 5), "| 35 in range(0, 100, 5):", 35 in range(0, 100, 5))

# range is iterable AND re-iterable (a generator would be exhausted)
r5 = range(3)
print("\nlist(r5) twice          :", list(r5), list(r5), "<- a range can be reused")
try:
    next(r5)
except TypeError as e:
    print("next(range) -> TypeError:", e, "(it's an iterable, not an iterator)")
print("iter(r5) type           :", type(iter(r5)).__name__)

# A gotcha at the extremes: len() must fit in a C ssize_t
try:
    len(range(10**30))
except OverflowError as e:
    print("\nlen(range(10**30)) -> OverflowError:", e)
print("...but the range itself works -> range(10**30)[5]:", range(10**30)[5], "| 5 in range(10**30):", 5 in range(10**30))

# 1. range() forms and off-by-one rules
# ------------------------------------
# - range(stop)              : 0, 1, ... stop-1
# - range(start, stop)       : start ... stop-1
# - range(start, stop, step) : start, start+step, ... while before stop
# - STOP IS EXCLUSIVE. It's what makes  len(range(a, b)) == b - a  and
#   range(a, b) + range(b, c) join with no gap or overlap.
# - Negative step counts down: then start must be GREATER than stop.
# - A step of 0 is an error; an "impossible" direction is just empty (no error).

print("\n# 1. range() forms and off-by-one rules")
print("# ------------------------------------")

print("list(range(5))            :", list(range(5)))
print("list(range(2, 7))         :", list(range(2, 7)), "<- 7 is NOT included")
print("list(range(0, 10, 3))     :", list(range(0, 10, 3)))
print("list(range(10, 0, -3))    :", list(range(10, 0, -3)), "<- 0 not included either")
print("list(range(5, 0))         :", list(range(5, 0)), "<- empty: step is +1 but start > stop")
print("list(range(5, 0, -1))     :", list(range(5, 0, -1)))
print("len(range(3, 8))          :", len(range(3, 8)), "= stop - start")
print("len(range(0, 10, 3))      :", len(range(0, 10, 3)), "= ceil((10 - 0) / 3)")

a_range, b_range, c_range = 0, 4, 9
print("\nrange(0,4) + range(4,9) tile perfectly:", list(range(a_range, b_range)) + list(range(b_range, c_range)) == list(range(a_range, c_range)))

try:
    range(0, 10, 0)
except ValueError as e:
    print("range(0, 10, 0) -> ValueError:", e)

# Classic off-by-one: to loop over indices 0..len-1, stop is len(x), not len(x)-1
items = ["a", "b", "c"]
print("\nrange(len(items))         :", list(range(len(items))), "(correct: indices 0,1,2)")
print("range(len(items) - 1)     :", list(range(len(items) - 1)), "(bug: last index dropped)")
print("# Prefer enumerate(items) over range(len(items)) when you need index + value.")
for i, item in enumerate(items):
    print("   enumerate ->", i, item)

# 2. What a range can do: len, index, count, reversed, equality
# ------------------------------------

print("\n# 2. What a range can do")
print("# ------------------------------------")

r = range(10, 30, 5)                      # 10, 15, 20, 25
print("r                    :", r, "->", list(r))
print("r.start/stop/step    :", r.start, r.stop, r.step)
print("r[0], r[-1]          :", r[0], r[-1], "(negative indexes work)")
print("r.index(20)          :", r.index(20), "(position of the value, O(1))")
print("r.count(20), r.count(21):", r.count(20), r.count(21))
print("reversed(r)          :", list(reversed(r)), "| type:", type(reversed(r)).__name__)
print("# reversed(range) is lazy too: it builds an iterator, no list copy.")
print("min/max/sum          :", min(r), max(r), sum(r))
print("hashable             :", hash(range(3)) == hash(range(3)))

try:
    r[10]
except IndexError as e:
    print("\nr[10] -> IndexError:", e)
try:
    r.index(21)
except ValueError as e:
    print("r.index(21) -> ValueError:", e)
try:
    r[0] = 99
except TypeError as e:
    print("r[0] = 99 -> TypeError:", e, "(immutable)")

# Equality compares the SEQUENCE OF VALUES, not (start, stop, step):
print("\nrange(0) == range(5, 5)        :", range(0) == range(5, 5), "(both empty)")
print("range(0, 3) == range(0, 3, 1)  :", range(0, 3) == range(0, 3, 1))
print("range(0, 5, 10) == range(0, 1) :", range(0, 5, 10) == range(0, 1), "(both are just [0])")
print("range(3) == [0, 1, 2]          :", range(3) == [0, 1, 2], "(a range is not a list)")
print("list(range(3)) == [0, 1, 2]    :", list(range(3)) == [0, 1, 2])
print("range(3) is range(3)           :", range(3) is range(3), "(each call makes a new object)")

# range can't mix types: only integers (or objects with __index__)
print("\nbool is an int, so range(True):", list(range(True)))

# 3. Slicing a range gives a range
# ------------------------------------
# - Slicing a list copies items. Slicing a range just computes a NEW
#   (start, stop, step), still lazy, still tiny.

print("\n# 3. Slicing a range gives a range")
print("# ------------------------------------")

r = range(0, 20)
s = r[5:15:2]
print("r[5:15:2]           :", s, "->", list(s))
print("type                :", type(s).__name__)
print("r[::-1]             :", r[::-1], "(a range counting down)")
print("r[-3:]              :", r[-3:], "->", list(r[-3:]))
print("range(10**12)[10**11:10**11 + 3]:", range(10**12)[10**11:10**11 + 3], "<- still instant")
print("range(10)[2:4][0]   :", range(10)[2:4][0], "(chained slices stay lazy)")

# 4. Why range(1.5) fails (and what to use instead)
# ------------------------------------
# - range only handles integers: its math (len, index, `in`) relies on exact
#   integer arithmetic. Floats would give rounding surprises.
# - For float steps:
#     * list comprehension:     [i * 0.25 for i in range(4)]   (no drift)
#     * numpy.arange / linspace  (numpy is covered in 07-NumPy)
#     * itertools.count(start, step) + islice for an endless/lazy float sequence

print("\n# 4. Why range(1.5) fails")
print("# ------------------------------------")

try:
    range(1.5)
except TypeError as e:
    print("range(1.5)    -> TypeError:", e)
try:
    range(0, 1, 0.25)
except TypeError as e:
    print("range(0,1,.25)-> TypeError:", e)
try:
    range("3")
except TypeError as e:
    print("range('3')    -> TypeError:", e)

print("\nfloat steps via comprehension :", [i * 0.25 for i in range(4)])

from itertools import count, islice
print("float steps via itertools     :", list(islice(count(0, 0.25), 4)), "(first value is the int 0 you passed)")
print("# Warning: repeatedly adding 0.1 drifts. Multiply an int index instead:")
acc = 0.0
for _ in range(10):
    acc += 0.1
print("   10 x (+0.1)  =", acc, "| 10 * 0.1 =", 10 * 0.1, "| 1.0 == acc:", acc == 1.0)

try:
    import numpy as np
    print("numpy.arange(0, 1, 0.25)      :", np.arange(0, 1, 0.25))
except ImportError:
    print("numpy not installed: skipping the np.arange demo (see 07-NumPy).")

# 5. Slicing rules for sequences
# ------------------------------------
# - seq[start:stop:step] works on list, tuple, str, bytes, range...
# - start is INCLUSIVE, stop is EXCLUSIVE. Any part may be omitted.
# - Negative numbers count from the end: -1 is the last item.
# - Omitted start/stop default to "the whole thing in the step direction".
# - BIG DIFFERENCE with indexing:
#       seq[i]    with i out of range  -> IndexError
#       seq[a:b]  with a/b out of range -> silently CLIPPED, never an error.
# - Step -1 walks backwards; with a negative step, defaults flip:
#   start defaults to the END and stop defaults to "before the beginning".

print("\n# 5. Slicing rules for sequences")
print("# ------------------------------------")

L = [10, 20, 30, 40, 50, 60]
print("L                :", L)
print("L[1:4]           :", L[1:4], "(index 1,2,3)")
print("L[:3] / L[3:]    :", L[:3], L[3:], "(split at 3, nothing lost or repeated)")
print("L[-2:]           :", L[-2:], "| L[:-2]:", L[:-2])
print("L[::2]           :", L[::2], "(every 2nd)")
print("L[1::2]          :", L[1::2])
print("L[::-1]          :", L[::-1], "(reversed copy)")
print("L[::-2]          :", L[::-2])
print("L[4:1:-1]        :", L[4:1:-1], "(backwards from 4 down to, not incl., 1)")
print("L[1:4:-1]        :", L[1:4:-1], "<- empty! direction and bounds disagree")

print("\nOut-of-range:")
print("L[2:100]         :", L[2:100], "(stop clipped to len)")
print("L[-100:2]        :", L[-100:2], "(start clipped to 0)")
print("L[100:200]       :", L[100:200], "(empty, no error)")
try:
    L[100]
except IndexError as e:
    print("L[100]           -> IndexError:", e)

print("\nSame rules everywhere:")
print("'python'[1:4]    :", "python"[1:4])
print("'python'[::-1]   :", "python"[::-1])
print("(1,2,3,4)[1:3]   :", (1, 2, 3, 4)[1:3])
print("b'abcdef'[::2]   :", b"abcdef"[::2])

try:
    L[::0]
except ValueError as e:
    print("\nL[::0] -> ValueError:", e)
try:
    L["a":2]
except TypeError as e:
    print("L['a':2] -> TypeError:", e)
try:
    L[1.0]
except TypeError as e:
    print("L[1.0]  -> TypeError:", e, "(floats are never valid indexes)")

# 6. slice objects and .indices()
# ------------------------------------
# - L[1:4:2] is sugar for L[slice(1, 4, 2)]. The [] operator receives ONE
#   argument: a slice object. You can build, store, pass around that object.
# - slice(stop)  or  slice(start, stop[, step]).  Omitted parts are None.
# - .indices(length) resolves negatives/None/out-of-range for a sequence of
#   that length and returns (start, stop, step) as real, clipped integers.
#   It's the tool you use when WRITING your own sequence class.
# - range(*slc.indices(n)) gives exactly the positions the slice would select.

print("\n# 6. slice objects and .indices()")
print("# ------------------------------------")

sl = slice(1, 5, 2)
print("slice(1, 5, 2)         :", sl)
print("attributes             :", sl.start, sl.stop, sl.step)
print("L[sl]                  :", L[sl], "== L[1:5:2]:", L[sl] == L[1:5:2])
print("slice(3)               :", slice(3), "-> start=None stop=3 step=None")
print("slice(None, None, -1)  :", slice(None, None, -1), "-> that's [::-1]")
print("L[slice(None, None, -1)]:", L[slice(None, None, -1)])

print("\n.indices() for a length-6 sequence:")
print("slice(None, None, None).indices(6) :", slice(None, None, None).indices(6))
print("slice(-2, None).indices(6)         :", slice(-2, None).indices(6), "<- -2 became 4")
print("slice(2, 100).indices(6)           :", slice(2, 100).indices(6), "<- 100 clipped to 6")
print("slice(None, None, -1).indices(6)   :", slice(None, None, -1).indices(6), "<- start 5, stop -1 (before index 0)")
print("positions picked by [::-2]         :", list(range(*slice(None, None, -2).indices(6))))
print("slice(1, 4).indices(6) -> range    :", range(*slice(1, 4).indices(6)))

# A slice object can be built from variables, unlike the [a:b] literal syntax,
# and reused on many sequences:
last_three = slice(-3, None)
print("\nreuse one slice on many types:")
print("   list :", [1, 2, 3, 4, 5][last_three])
print("   str  :", "abcdef"[last_three])
print("   tuple:", (7, 8, 9, 10)[last_three])
print("   range:", range(100)[last_three])

# 7. Naming slices: fixed-width record parsing
# ------------------------------------
# - Magic numbers like line[10:20] are unreadable. Give each slice a NAME once.
# - Typical use: fixed-width text files, binary headers, log formats.

print("\n# 7. Naming slices: fixed-width record parsing")
print("# ------------------------------------")

#            0         1         2
#            012345678901234567890123456
record = "ALICE     0042  2024-05-17 OK"
NAME = slice(0, 10)
QTY = slice(10, 14)
DATE = slice(16, 26)
STATUS = slice(27, 29)

print("raw record :", repr(record))
print("name       :", repr(record[NAME].strip()))
print("quantity   :", int(record[QTY]))
print("date       :", record[DATE])
print("status     :", record[STATUS])

# The same names work on several lines:
rows = ["BOB       0007  2024-05-18 OK", "CARLA     0100  2024-05-19 NO"]
print("parsed rows:", [(row[NAME].strip(), int(row[QTY]), row[STATUS]) for row in rows])

# The unreadable alternative, for contrast:
print("without names -> record[0:10], record[10:14], record[16:26] ... what is each one?")

# 8. Slice assignment and deletion on lists
# ------------------------------------
# - Lists (and bytearray) are mutable: a slice on the LEFT of = REPLACES that
#   region in place.
# - Plain slices (step 1): the replacement can be ANY length: list shrinks/grows.
# - Extended slices (a step other than 1): the lengths MUST match, else ValueError.
# - The right side only has to be iterable.
# - `del a[start:stop:step]` removes the region.
# - Pure insertion without removing: a[i:i] = [...]

print("\n# 8. Slice assignment and deletion on lists")
print("# ------------------------------------")

a = [0, 1, 2, 3, 4, 5]
a[1:3] = ["x", "y", "z"]                # replace 2 items with 3 -> list grows
print("a[1:3] = ['x','y','z']  :", a)
a[1:4] = []                             # replace 3 items with nothing -> deletion
print("a[1:4] = []             :", a)
a[1:1] = ["ins1", "ins2"]               # empty slice => pure insertion
print("a[1:1] = ['ins1','ins2']:", a)
a[len(a):] = [99]                       # slice at the end => append
print("a[len(a):] = [99]       :", a)
a[:2] = "ab"                            # any iterable on the right (str -> chars)
print("a[:2] = 'ab'            :", a)
a[:] = [7, 8, 9]                        # replace EVERYTHING in place (same list object)
print("a[:] = [7, 8, 9]        :", a)

nums = list(range(10))
del nums[::2]                           # delete every 2nd item
print("\ndel nums[::2]          :", nums)
del nums[1:3]
print("del nums[1:3]           :", nums)
nums[::2] = ["E", "F"]                  # extended slice: sizes must match
print("nums[::2] = ['E','F']   :", nums, "(2 slots, 2 values)")

try:
    nums[::2] = [0]
except ValueError as e:
    print("\nnums[::2] = [0]  -> ValueError:", e)
try:
    nums[1:3] = 5
except TypeError as e:
    print("nums[1:3] = 5    -> TypeError:", e, "(right side must be iterable)")

# `a[:] = x` and `a = x` are different: the first mutates the object, which
# every other name sees; the second just rebinds this one name.
orig = [1, 2, 3]
alias = orig
orig[:] = [9, 9]
print("\nalias after orig[:] = [9, 9]:", alias, "(same object mutated)")
orig = [0]
print("alias after orig = [0]      :", alias, "(rebinding left it alone)")

# Slice assignment on immutables fails:
try:
    "text"[0:2] = "ab"
except TypeError as e:
    print("str slice assignment -> TypeError:", e)

# 9. Slices copy (shallowly), strings/tuples are immutable
# ------------------------------------
# - A slice of a list builds a NEW list, but its items are the SAME objects
#   (a shallow copy). Fine for ints/strs, a trap for nested lists.
# - L[:] is the classic "make a copy" idiom (equivalent: L.copy(), list(L)).
# - For str/tuple/bytes a slice also builds a new object (they are immutable, so
#   sharing would be harmless). CPython may even return the SAME object for a
#   full slice t[:], an optimisation, not a language guarantee.
# - Deep vs shallow copies are explored in 12-Mutability-And-Memory-Model.py.

print("\n# 9. Slices copy (shallowly)")
print("# ------------------------------------")

nested = [[1, 2], [3, 4]]
copy_slice = nested[:]
print("copy_slice is nested        :", copy_slice is nested, "(new outer list)")
print("copy_slice[0] is nested[0]  :", copy_slice[0] is nested[0], "(same inner list!)")
copy_slice[0].append("!")
print("mutating the inner list shows in both:", nested)
copy_slice.append([5, 6])
print("appending to the outer copy leaves the original:", nested)

t = (1, 2, 3)
print("\nt[:] is t (CPython detail)   :", t[:] is t)
print("t[:2] is t                   :", t[:2] is t, "(a real new tuple)")
s = "hello"
print("s[1:3] -> new str            :", s[1:3], "| original unchanged:", s)

# 10. Ellipsis (...) briefly
# ------------------------------------
# - `...` is a built-in singleton called Ellipsis. It's a real object.
# - Plain Python uses it as: a placeholder body (`def f(): ...`), "unfinished"
#   marker, and in type hints (tuple[int, ...] = tuple of any length).
# - Lists/tuples don't give `...` any slicing meaning, but your own
#   __getitem__ receives it as the key. NumPy uses it as "all the dimensions
#   I didn't mention":   arr[..., 0]  ==  arr[:, :, 0] for a 3-D array.

print("\n# 10. Ellipsis (...) briefly")
print("# ------------------------------------")

print("... is Ellipsis       :", ... is Ellipsis, "| type:", type(...).__name__, "| repr:", repr(...))
print("bool(...)             :", bool(...))


def todo_function():
    ...                                 # valid, does nothing: a body placeholder


print("todo_function() returns:", todo_function())


class ShowKey:
    def __getitem__(self, key):
        return key


show = ShowKey()
print("\nShowKey()[1]          :", show[1])
print("ShowKey()[1:5:2]      :", show[1:5:2], "(a slice)")
print("ShowKey()[1:2, ::3]   :", show[1:2, ::3], "(a TUPLE of slice objects)")
print("ShowKey()[..., 0]     :", show[..., 0], "(a tuple holding Ellipsis)")

try:
    ellipsis_key = ...
    [1, 2, 3][ellipsis_key]
except TypeError as e:
    print("\n[1, 2, 3][...] -> TypeError:", e, "(lists don't understand Ellipsis)")

try:
    import numpy as np
    arr = np.arange(24).reshape(2, 3, 4)
    print("numpy: arr[..., 0] == arr[:, :, 0]:", (arr[..., 0] == arr[:, :, 0]).all(), "| shape:", arr[..., 0].shape)
except ImportError:
    print("numpy not installed: skipping the arr[..., 0] demo (see 07-NumPy).")

# 11. A custom class whose __getitem__ accepts ints AND slices
# ------------------------------------
# - x[key] calls type(x).__getitem__(x, key).
# - key is an int for x[3], a slice object for x[1:4], and could be anything.
# - To support both: check isinstance(key, slice).
# - Convention: a slice returns the SAME kind of container, an int returns
#   one element.
# - Use key.indices(len(self)) so negatives/None/out-of-range behave exactly
#   like built-in sequences.
# - Raise IndexError for bad int positions: that's also what makes the old
#   iteration protocol (for-loops over __getitem__) stop.

print("\n# 11. A custom class whose __getitem__ accepts ints AND slices")
print("# ------------------------------------")


class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            start, stop, step = key.indices(len(self))
            print(f"   (slice {key} resolved with len={len(self)} -> start={start}, stop={stop}, step={step})")
            return Playlist(self._songs[i] for i in range(start, stop, step))
        if isinstance(key, int):
            if key < 0:
                key += len(self)         # support negative index
            if not 0 <= key < len(self):
                raise IndexError("playlist index out of range")
            return self._songs[key]
        raise TypeError(f"Playlist indices must be integers or slices, not {type(key).__name__}")

    def __repr__(self):
        return f"Playlist({self._songs})"


p = Playlist(["intro", "verse", "chorus", "bridge", "outro"])
print("p            :", p)
print("p[0]         :", p[0])
print("p[-1]        :", p[-1])
print("p[1:4]       :", p[1:4], "<- a Playlist, not a list")
print("p[::-1]      :", p[::-1])
print("p[10:20]     :", p[10:20], "<- clipped to empty, like a list")
print("type(p[1:3]) :", type(p[1:3]).__name__)

try:
    p[10]
except IndexError as e:
    print("\np[10]  -> IndexError:", e)
try:
    p["x"]
except TypeError as e:
    print("p['x'] -> TypeError:", e)

# Because __getitem__ raises IndexError at the end, iteration and `in` work for free:
print("for-loop works (old protocol):", [song for song in p])
print("'bridge' in p                  :", "bridge" in p)
print("list(reversed(p))              :", list(reversed(p)), "(reversed() needs __len__ + __getitem__)")

# 12. operator.index
# ------------------------------------
# - operator.index(x) converts x to a real int ONLY if x is integer-like
#   (int, bool, numpy ints, anything defining __index__). Floats are refused.
# - That is the exact check built-in indexing/slicing/range use.
# - So in a custom __getitem__, use operator.index(key) instead of
#   isinstance(key, int) to also accept numpy integers and custom int-likes.
# - __index__ is different from __int__ (int(3.7) happily truncates).

import operator

print("\n# 12. operator.index")
print("# ------------------------------------")

print("operator.index(5)     :", operator.index(5))
print("operator.index(True)  :", operator.index(True), "(bool is an int)")
try:
    operator.index(5.0)
except TypeError as e:
    print("operator.index(5.0) -> TypeError:", e)
print("int(5.7) truncates    :", int(5.7), "<- __int__ is lenient, __index__ is strict")


class Slot:
    """An int-like object: usable as an index because it defines __index__."""

    def __init__(self, n):
        self.n = n

    def __index__(self):
        return self.n


print("\n['a','b','c'][Slot(1)]   :", ["a", "b", "c"][Slot(1)])
print("'abcdef'[Slot(1):Slot(4)] :", "abcdef"[Slot(1):Slot(4)])
print("range(Slot(3))            :", list(range(Slot(3))))
print("hex(Slot(255)), bin(Slot(5)):", hex(Slot(255)), bin(Slot(5)))
print("operator.index(Slot(7))   :", operator.index(Slot(7)))


class Playlist2(Playlist):
    """Same class, but integer keys go through operator.index."""

    def __getitem__(self, key):
        if isinstance(key, slice):
            return super().__getitem__(key)
        i = operator.index(key)         # TypeError automatically for str/float
        return super().__getitem__(i)


p2 = Playlist2(["a", "b", "c"])
print("Playlist2[Slot(2)]        :", p2[Slot(2)])
try:
    p2[1.0]
except TypeError as e:
    print("Playlist2[1.0] -> TypeError:", e)

# 13. itertools.islice: slicing things you can't index
# ------------------------------------
# - Generators, file objects, map(), zip(), itertools.count() have NO len and
#   NO indexing, so gen[2:5] is a TypeError.
# - itertools.islice(iterable, [start,] stop [, step]) gives a LAZY slice.
# - It walks the iterator from the front (cannot jump), so skipping costs time.
# - It CONSUMES the underlying iterator: items it passes over are gone.
# - Negative values are not allowed (the length is unknown!).
# - Perfect for "first N of an infinite stream".

print("\n# 13. itertools.islice")
print("# ------------------------------------")

from itertools import islice, count


def squares():
    n = 0
    while True:                         # infinite generator
        yield n * n
        n += 1


g = squares()
try:
    g[2:5]
except TypeError as e:
    print("generator[2:5] -> TypeError:", e)

print("first 5 squares         :", list(islice(squares(), 5)))
print("items 2..4 (islice 2,5) :", list(islice(squares(), 2, 5)))
print("every 3rd of first 10   :", list(islice(squares(), 0, 10, 3)))
print("count(10) first 4       :", list(islice(count(10), 4)))

# Consumption gotcha:
it = iter(range(10))
print("\nfirst islice(it, 3)     :", list(islice(it, 3)))
print("second islice(it, 3)    :", list(islice(it, 3)), "<- continues where the first stopped!")
print("remaining              :", list(it))

# Compare: the same slice on a SEQUENCE is repeatable because it's indexing
seq = list(range(10))
print("seq[:3] twice           :", seq[:3], seq[:3])

try:
    list(islice(squares(), -1))
except ValueError as e:
    print("\nislice(.., -1) -> ValueError:", e)

# Reading just the first lines of a (possibly huge) file lazily:
import tempfile
import os

with tempfile.TemporaryDirectory() as tmp:
    path = os.path.join(tmp, "lines.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(f"line {i}" for i in range(1000)) + "\n")
    with open(path, encoding="utf-8") as f:
        head = [ln.strip() for ln in islice(f, 3)]    # reads only ~3 lines
    print("first 3 file lines via islice:", head)

# "Last N" of an iterator is NOT a job for islice (can't know where the end is):
from collections import deque
print("last 3 of an iterator via deque(maxlen=3):", list(deque(iter(range(10)), maxlen=3)))

if sys.version_info >= (3, 12):
    from itertools import batched
    print("itertools.batched (3.12+):", list(batched(range(7), 3)))
else:
    print("Skipped: itertools.batched needs Python 3.12+")

print("\n# Recap: range = lazy integer sequence (O(1) memory, O(1) membership).")
print("# slice object = the thing inside []; .indices(n) resolves it for length n.")
print("# Slices clip, indexes raise. Use islice for iterators, __getitem__ + isinstance")
print("# (or operator.index) to build your own sliceable classes.")
print("\n# End of range & slice Explanation")
