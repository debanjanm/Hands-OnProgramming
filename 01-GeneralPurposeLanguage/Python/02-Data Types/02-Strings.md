# Strings — Notes

## What this covers
Python's `str` type: creating, indexing/slicing, "editing" (via new strings, since strings are immutable), common methods, formatting, and some performance/encoding internals.

## Key points
- Strings are immutable, ordered, indexed sequences of characters — quote with `'...'`, `"..."`, or `'''...'''`/`"""..."""` (multi-line).
- Indexing/slicing works like lists: `s[0]`, `s[-1]`, `s[1:5]`, `s[::2]`.
- "Editing" a string means building a new one — via slicing+concatenation or methods like `.replace()`.
- Key methods: `.upper()/.lower()/.title()/.capitalize()/.swapcase()`, `.strip()/.lstrip()/.rstrip()`, `.split()/.join()`, `.find()/.startswith()/.endswith()`, `.replace()`, `.count()`.
- f-strings (`f"{name}"`) are the standard way to format; the format mini-language (`{value:>10.2f}`) controls width, alignment, decimals, commas, sign, percentage, hex.
- Padding: `ljust/rjust/center(w, fillchar)` and `zfill(w)`; the spec equivalents are `{:<10}` `{:>10}` `{:^10}` `{:*^10}` `{:010d}`. Text defaults to left-aligned, numbers to right-aligned.
- On strings the spec `.N` means "max N characters", so `{s:<10.5}` (or `f"{s:<{w}.{p}}"` with nested fields) truncates and pads in one go. Width/precision can be variables.
- Number codes: `,` / `_` thousands, `.2f`, `.3e`, `.1%`, `b o x X` (add `#` for the `0b/0o/0x` prefix), sign `+` or space.
- Debugging: `f"{x=}"` prints `x=7`; `!r` / `!s` / `!a` pick `repr` / `str` / `ascii`. Use `!r` to see quotes and escapes.
- Three formatting styles: f-strings (default), `.format()` (reusable templates), `%` (old code, logging).
- `str.maketrans()` + `.translate()` does many single-character substitutions in one pass — faster than chained `.replace()` calls.
- Raw strings (`r"..."`) treat backslashes literally — essential for regex and Windows paths.
- `.encode(encoding)` turns `str` into `bytes`; `.decode(encoding)` reverses it. UTF-8 is the standard.

## Gotchas (the part worth revising twice)
- `s += "x"` in a loop is O(n²) — each `+=` builds a brand-new string, copying everything before it. Use `"".join(list_of_strings)` instead — O(n).
- Short/identifier-like string literals get interned by CPython (equal literals can share the same object), so `"hello" is "hello"` may be `True` — still don't rely on `is` for string equality, use `==`.
- `bool("False")` is `True` — any non-empty string is truthy, `bool()` doesn't parse the text (see Type-Casting notes).
- `"café".encode("ascii")` raises `UnicodeEncodeError` — ASCII can't represent non-ASCII characters; use UTF-8.
- `ljust/rjust/center` never truncate, and `fillchar` must be exactly 1 character. `"-42".zfill(5)` gives `-0042` but `"-42".rjust(5, "0")` gives `00-42` (rjust ignores the sign).
- `"%s" % some_tuple` raises `TypeError` (the tuple is read as the arguments) — write `"%s" % (t,)`.
- Literal braces in f-strings / `.format()` must be doubled: `{{` `}}`. Before Python 3.12 you could not reuse the same quote type or a backslash inside `{...}`; 3.12+ allows both.
- You cannot assign to `s[0]` or `del s[0]` — strings don't support item assignment/deletion (immutability).

## When it matters
Constantly — text processing, formatting output, building keys, parsing input. Reach for `.join()` over `+=` whenever building a string from many pieces in a loop.

## One-line recap example
```python
words = ["a", "b", "c"]
result = "-".join(words)     # "a-b-c" — O(n), not the O(n^2) '+=' loop
print(f"{3.14159:.2f}")      # "3.14" — f-string format spec
```
