# Comprehensions — Notes

## What this covers
The short syntax for building lists, sets, dicts, and generators from an iterable in one line — `[expr for item in iterable if condition]` and its set/dict/generator variants.

## Key points
- List comprehension: `[x**2 for x in range(1,6)]`; same shape works for sets `{...}` and dicts `{k: v for ...}`.
- Optional filter: `[x for x in range(20) if x % 2 == 0]`.
- Conditional expression (if-else) inside the expression part: `["even" if x%2==0 else "odd" for x in range(5)]`.
- Nested comprehensions can flatten (`[n for row in matrix for n in row]`) or transpose (`[[row[i] for row in matrix] for i in range(3)]`).
- Generator expression uses `()` instead of `[]` — lazily evaluated, produces one value at a time instead of building the whole thing in memory.
- The walrus operator `:=` lets you assign and use a value in the same expression — avoids computing an expensive thing twice inside a comprehension's filter and body.

## Gotchas (the part worth revising twice)
- In Python 3 (unlike Python 2), comprehensions have their own scope — the loop variable does NOT leak into the surrounding scope.
- A generator expression stays constant-size in memory regardless of the input size; a list comprehension builds and stores everything at once. Use a generator when you only need to iterate once and don't need indexing/`len()`.
- Comprehensions are usually faster than an equivalent loop + `.append()` because they compile to dedicated bytecode and skip the repeated `.append` attribute lookup.
- Nesting more than ~2 levels, or adding extra branching logic, makes a comprehension harder to read than a plain loop — switch to a real loop at that point.

## When it matters
Use comprehensions for short, single-expression transforms/filters. Reach for a generator expression instead of a list comprehension when processing something large or unbounded and you only need to iterate once.

## One-line recap example
```python
evens_squared = [x**2 for x in range(10) if x % 2 == 0]   # list comprehension: filter + transform
lazy_version  = (x**2 for x in range(10) if x % 2 == 0)    # same, but lazy (generator)
```
