# Tuples — Notes

## What this covers
Python's `tuple` type: creating, indexing/slicing, why tuples are immutable, tuple-specific methods, packing/unpacking, and why hashability makes tuples special.

## Key points
- Tuples are ordered, immutable, allow duplicates, created with `()` or `tuple()`.
- Single-item tuple needs a trailing comma: `("item",)` — without it, `("item")` is just a string.
- Since tuples can't change, "editing" means converting to a list, modifying, and converting back — or building a new tuple via concatenation.
- Methods are limited to what doesn't mutate: `len()`, `sum()`, `min()/max()`, `.count()`, `.index()`, `sorted()` (returns a list).
- Tuple packing: `x = 1, "hello", 3.14` (no parens needed). Unpacking: `a, b, c = packed_tuple`.
- `zip(*coordinate_pairs)` unzips a list of tuples back into separate sequences.

## Gotchas (the part worth revising twice)
- Immutability is shallow: a tuple's own slots can't be reassigned, but if it contains a mutable object (like a list), that inner object can still be mutated in place — `t[2].append(5)` "changes" an immutable tuple.
- A tuple is hashable (usable as dict key / set member) only if every element inside is also hashable — a tuple containing a list is NOT hashable. This is the main practical reason to pick a tuple over a list.
- Tuples are cheaper to create than lists (no over-allocated capacity needed) — prefer tuples for fixed collections that won't change.
- Three ways to hold a "record": plain tuple (fastest, access by position), `namedtuple` (still a tuple, but fields by name too), `dataclass` (mutable by default, best with methods/defaults).

## When it matters
Use tuples for fixed groups of values, function returns with multiple values, or anything you need as a dict key/set element. Reach for `namedtuple` when field names improve readability without giving up immutability.

## One-line recap example
```python
point = (3, 4)                 # tuple packing
x, y = point                   # tuple unpacking
cache = {point: "seen"}        # tuples are hashable -> usable as dict keys
```
