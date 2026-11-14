# Type Casting — Notes

## What this covers
Converting values between types in Python — implicit (automatic) vs explicit (manual, via `int()`, `float()`, `str()`, `bool()`, `list()`, `tuple()`, `set()`, `dict()`), and how a class can customize its own casting behavior.

## Key points
- Implicit casting only happens in numeric contexts Python considers safe, e.g. `5 + 2.5` promotes the int to float automatically. It never happens between unrelated types like `str` and `int`.
- `int()` converts from float (truncates decimals), string (must look like an integer), or bool (`True`→1, `False`→0).
- `float()` converts from int, string (`"3.14"` or `"123"`), or bool.
- `str()` converts almost anything to its text representation — numbers, bools, lists, tuples, dicts, sets.
- `bool()`: everything is truthy except `False`, `None`, `0`, `0.0`, and empty containers/strings (`""`, `[]`, `()`, `{}`, `set()`).
- `list()`/`tuple()`/`set()` can build from any iterable — string (→ characters), another sequence, or a dict (defaults to iterating keys; use `.values()`/`.items()` for the rest).
- `dict()` can be built from a list of 2-item tuples, or from a `zip()` object of keys and values.

## Gotchas (the part worth revising twice)
- `bool("False")` is `True` — any non-empty string is truthy; `bool()` on a string only checks emptiness, it does not parse the text.
- `int("3.5")` raises `ValueError` — `int()` can't parse a decimal point from a string directly. Go through `float()` first: `int(float("3.5"))`.
- `int()` strips surrounding whitespace automatically (`int("  42  ")` works) but does not tolerate other stray characters (`int("42abc")` fails).
- A class controls its own casting via dunder methods: `__int__`, `__float__`, `__str__`, `__bool__`. If `__bool__` isn't defined, Python falls back to `__len__` (0 → False); if neither exists, every instance is truthy.

## When it matters
Whenever data crosses a boundary that expects a specific type — parsing user input, reading from files/APIs, preparing data for display. Watch especially for the string-truthiness and `int("3.5")` traps.

## One-line recap example
```python
class Money:
    def __init__(self, cents): self.cents = cents
    def __int__(self): return self.cents // 100
    def __bool__(self): return self.cents != 0

print(int(Money(1050)))   # 10 -- calls __int__
```
