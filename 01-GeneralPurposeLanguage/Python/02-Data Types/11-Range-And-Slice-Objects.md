# Range and Slice Objects — Notes

## What this covers
`range` (a lazy integer sequence), slicing rules, the `slice` object and `.indices()`, slice assignment, writing your own sliceable class, `operator.index`, and `itertools.islice` for things you can't index.

## Key points
- **`range` is not a list.** It stores only `start`, `stop`, `step` and computes item `i` as `start + i*step`. `range(10**12)` costs the same tiny memory as `range(5)`.
- It is a real immutable sequence: `len`, indexing, slicing, `in`, `reversed`, `.index`, `.count`, hashable. A range can be iterated again and again (a generator can't).
- **`x in range(...)` is arithmetic**, not a scan, so it is instant even for huge ranges.
- **Stop is exclusive**: `len(range(a, b)) == b - a`, and `range(a, b) + range(b, c)` join with no gap or overlap.
- Slicing a range gives a new (lazy) range, not a list.
- `range` only takes integers (or objects with `__index__`). For float steps use `[i * 0.25 for i in range(4)]`.
- **Slice rules** (`seq[start:stop:step]`): start inclusive, stop exclusive, negatives count from the end, any part may be left out. Works the same on list, tuple, str, bytes, range.
- **Slice object**: `L[1:4:2]` is sugar for `L[slice(1, 4, 2)]`. You can store it, name it, and reuse it on many sequences.
- **`slice.indices(n)`** resolves `None`, negatives and out-of-range values for a length `n` into real `(start, stop, step)`. `range(*s.indices(n))` gives exactly the picked positions. Use it in your own `__getitem__`.
- **Slice assignment** (lists, bytearray): `a[1:3] = [...]` replaces a region and may change the length; `a[i:i] = [...]` inserts; `del a[::2]` removes. Extended slices (step other than 1) need equal lengths.
- Name your slices (`NAME = slice(0, 10)`) for fixed-width records instead of magic numbers.
- A custom `__getitem__` gets an `int` for `x[3]` and a `slice` for `x[1:4]`. Check with `isinstance(key, slice)`.
- `operator.index(x)` accepts int-likes (int, bool, numpy ints, anything with `__index__`) and rejects floats. This is what built-in indexing uses.
- **`itertools.islice(it, [start,] stop[, step])`** is the lazy slice for generators, files, `count()`. It walks from the front and consumes the iterator.

## Gotchas (the part worth revising twice)
- **Indexing raises, slicing clips.** `L[100]` is an `IndexError`; `L[2:100]` and `L[100:200]` quietly give the clipped result or `[]`.
- `range(5, 0)` is empty (no error) because the step is `+1`. Use `range(5, 0, -1)`. A step of `0` is a `ValueError`.
- Off-by-one: loop over indices with `range(len(x))`, not `range(len(x) - 1)`. Better, use `enumerate`.
- `L[1:4:-1]` is empty: direction and bounds disagree. With a negative step, start defaults to the end.
- `range(3) == [0, 1, 2]` is `False` (a range is not a list), but `range(0) == range(5, 5)` is `True` (equal values).
- `next(range(3))` fails: a range is an iterable, not an iterator. Call `iter()` first.
- `len(range(10**30))` raises `OverflowError` (length must fit a C integer), though indexing and `in` still work.
- A list slice is a **shallow** copy: new outer list, same inner objects. `nested[:][0].append(...)` changes `nested` too.
- `a[:] = x` mutates the list in place (every alias sees it); `a = x` only rebinds the name.
- `nums[::2] = [0]` is a `ValueError` (extended slice, sizes must match). `nums[1:3] = 5` is a `TypeError` (right side must be iterable).
- `islice` **consumes**: a second `islice(it, 3)` continues where the first stopped. No negative values ever, and it cannot do "last N" (use `deque(it, maxlen=N)`).
- Repeatedly adding `0.1` drifts; multiply an integer index instead.

## When it matters
Looping and indexing in almost every program; `slice`/`__getitem__` when building your own sequence-like class; `islice` when reading the first lines of a huge file or taking the first N items of an infinite generator.

## One-line recap example
```python
from itertools import islice
print(list(range(10)[2:8:3]), "hello"[::-1], list(islice(iter(range(100)), 3)))  # [2, 5] olleh [0, 1, 2]
```
