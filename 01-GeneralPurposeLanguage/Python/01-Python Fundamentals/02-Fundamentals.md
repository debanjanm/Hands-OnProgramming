# Python Fundamentals — Notes

## What this covers
The absolute basics: what Python is, how it looks, and how it stores data.
This is the file to skim before anything else in the repo.

## Key points
- **Python** = high-level, interpreted, readable-by-design. No compile step — you run `.py` files directly.
- **Indentation is not style, it's syntax.** A wrong indent is a real error, not a warning (unlike `{}`-based languages).
- **Dynamically typed**: `x = 5` then later `x = "hello"` is legal — the variable's type is whatever it currently holds, not fixed.
- **Comments**: `#` for one line, `'''...'''`/`"""..."""` for a block (also doubles as a docstring).
- **Core built-in types**: `int`, `float`, `complex`, `str`, `list`, `tuple`, `dict`, `set`, `bool`.
- **Literals** = values written directly in code (`5`, `"hi"`, `True`) — the raw material variables are built from.
- **Operators**: arithmetic (`+ - * / // % **`), comparison (`== != < >`), logical (`and or not`).
- **Expressions** = anything that evaluates to a value (`2 + 2`, a function call, `x > 3`).

## Gotchas (the part worth revising twice)
- `is` checks **identity** (same object in memory), `==` checks **equality** (same value). Small ints (-5 to 256) and short strings are cached, so `is` can look like it "works" for them — don't rely on that, it breaks for anything else.
- `and`/`or` don't return `True`/`False` — they return one of the actual operands (short-circuit evaluation). `"" or "default"` gives `"default"`, not `True`.
- Floats aren't exact: `0.1 + 0.2 != 0.3`. Use `math.isclose()` or `Decimal` when precision matters (money, comparisons).
- Chained comparisons (`1 < x < 10`) work like math notation in Python — most other languages don't support this directly.

## When it matters
Every other file in this repo assumes you're comfortable with this one. Revisit it if a later topic's syntax feels unfamiliar.

## One-line recap example
```python
x = 5          # dynamically typed, no declaration needed
y = "5"
print(x == int(y))   # True (value)  |  print(x is int(y)) -> usually False (different objects)
```
