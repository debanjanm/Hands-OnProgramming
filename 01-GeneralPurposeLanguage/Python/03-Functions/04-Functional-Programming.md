# Functional Programming — Notes

## What this covers
Using functional ideas in Python: functions as values, pure functions, immutable data, `map`/`filter`/`reduce` vs comprehensions, `partial`, `compose`/`pipe`, `operator` helpers, lazy vs eager evaluation, recursion limits, `lru_cache`, and one small log-processing pipeline written three ways. Python is **multi-paradigm** — borrow the ideas that help, don't force the whole style.

## Key points
- **Functional style** = combine small functions that take values in and give values out, instead of mutating shared state. Functions are values: store them in dicts, pass them, return them.
- **Pure function**: output depends only on its arguments, no side effects (no printing, no global writes, no mutating inputs). Easy to test (plain `assert`, no mocks), cache and run in parallel. `print` is a side effect too — keep it at the edges.
- **Immutability helpers**: `tuple`, `frozenset`, `@dataclass(frozen=True)` (with `dataclasses.replace` to copy-with-changes), `types.MappingProxyType` (read-only view of a dict).
- **`map`/`filter`** are lazy. They read well with an *existing named function* (`map(str.strip, xs)`, `map(int, xs)`, `filter(None, xs)`). If you need a `lambda`, a comprehension is clearer.
- **`functools.reduce(f, items, initial)`** folds many items into one value. The accumulator may be a different type than the items.
- **`lambda`** = exactly one expression (no assignment, `return`, loops, `try`). Its real job is `key=` for `sorted`/`min`/`max`.
- **`functools.partial`** pre-fills arguments; **`partialmethod`** does the same inside a class (keeps `self`).
- **`compose(f, g, h)(x)` = `f(g(h(x)))`** (right to left); **`pipe(f, g, h)(x)` = `h(g(f(x)))`** (left to right, reads like a recipe). Both are a few lines with `reduce`; every step takes one argument.
- **Currying** (`f(a)(b)(c)`) is mostly an exercise; `partial` covers real needs.
- **`operator.itemgetter / attrgetter / methodcaller`** replace the most common lambdas and accept several keys (`itemgetter(1, 2)`) for multi-level sorting.
- **itertools in FP style**: `accumulate` (running totals/max, `initial=`), `starmap`, `takewhile`, `dropwhile`, `chain.from_iterable`, `groupby`. Full tour: `05-Python Advanced/08-Itertools-And-Functools.py`.
- **Lazy vs eager**: a list computes and stores everything now; a generator computes one item at a time on demand — tiny memory, works on infinite sources, good for "first match".
- **Higher-order functions that return functions** (`make_multiplier`, `negate`, a mini decorator) configure behaviour once via a closure.
- **`lru_cache`** remembers results of a pure function with hashable arguments (`cache_info()`, `cache_clear()`).

## Gotchas (the part worth revising twice)
- **No tail-call optimisation in Python.** Even a tail-recursive function hits `RecursionError` (limit ~1000). Use a loop, `reduce`, or a built-in (`sum(range(...))`). Recursion is still fine for trees/nested data, where depth is small.
- **`reduce` with no initial value fails on an empty input** (`TypeError`). Always pass one. And never use `reduce` where `sum`, `max`, `min`, `any`, `all` or `"".join` already exist.
- **`reduce` that rebuilds a dict each step is O(n²)** — `collections.Counter` is better.
- **`itertools.groupby` only groups *consecutive* equal keys** — `sorted()` by the same key first, or one key appears in several groups. Also each group is a lazy view of one shared iterator: call `list(g)` inside the loop, or it comes out empty.
- **`dropwhile` keeps everything after the first failure**, even items that would match the test again.
- **Generators and `map`/`filter` objects are single-use**; a second pass is empty. No `len()` or indexing either.
- **Immutability is shallow**: a tuple holding a list still lets the list change. A `MappingProxyType` view is *live* — it only blocks writes through the view; copy the dict first for a snapshot.
- **Never `lru_cache` an impure function** (e.g. one using `random` or time) — the first answer is frozen forever. Unhashable arguments (lists) raise `TypeError`.
- **A plain `partial` in a class body doesn't bind `self`**; use `partialmethod`.
- `f = lambda ...` shows `<lambda>` in tracebacks — use `def` for anything you name.
- Long `map`/`filter`/`lambda` chains are harder to read than one comprehension. In the pipeline example the comprehension version is the most Pythonic; the `pipe`/`reduce` version is tidy in idea but noisy and slower in Python.

## When it matters
Data-processing code (parsing, filtering, aggregating), sorting with `key=`, caching expensive calculations, and anywhere you want logic that is easy to test. Keep the core pure and put I/O at the edges. Reach for comprehensions and generators first, `partial`/`itemgetter`/`pipe` second, `reduce` last.

## One-line recap example
```python
from functools import reduce
from operator import itemgetter
pipe = lambda *fs: lambda x: reduce(lambda acc, f: f(acc), fs, x)   # left-to-right composition
clean = pipe(str.strip, str.lower, str.split)
print(clean("  Hello World "), sorted([("b", 2), ("a", 9)], key=itemgetter(1)))
# ['hello', 'world'] [('b', 2), ('a', 9)]
```
