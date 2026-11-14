# Primitive Data Types — Notes

## What this covers
Python's basic single-value types: `int`, `float`, `complex`, `bool`, and `None` — what they are, how to create them, and a few CPython internals worth knowing.

## Key points
- `int`: whole numbers, unlimited length (no overflow like other languages).
- `float`: decimal numbers, IEEE-754 double precision — has limited exactness.
- `complex`: `a + bj` form, with `.real` / `.imag` attributes, `.conjugate()`, and `abs()` for magnitude.
- `bool`: `True`/`False`, subtype of `int` (`True == 1`, `False == 0` in numeric context).
- `None`: represents "no value" — its own type `NoneType`, not the same as `0`, `False`, or `""`.
- Bitwise ops on ints: `& | ^ ~ << >>`; `n.bit_length()` gives bits needed to represent `n`.
- `sys.getsizeof()` shows an object's memory footprint in bytes.

## Gotchas (the part worth revising twice)
- CPython caches small ints from -5 to 256 as singletons, so `is` "works" for them by accident. Never rely on `is` for value comparison outside that range — always use `==`.
- `0.1 + 0.2 != 0.3` because floats can't represent every decimal exactly. Use `decimal.Decimal` for money/finance (exact base-10), `fractions.Fraction` for exact ratios.
- `bool` is a subclass of `int` — `bool(0)` is `False`, `bool(1)` is `True`, but also any non-empty container/string is truthy and empty ones are falsy.
- `float` objects are a fixed size in memory regardless of value, but `int` objects grow bigger for bigger values (unlimited precision has a memory cost).

## When it matters
Almost every program touches these. Reach for `Decimal`/`Fraction` specifically when floating-point rounding errors would be unacceptable (currency, exact ratios).

## One-line recap example
```python
from decimal import Decimal
print(0.1 + 0.2)                       # 0.30000000000000004 (float imprecision)
print(Decimal("0.1") + Decimal("0.2")) # 0.3 (exact)
```
