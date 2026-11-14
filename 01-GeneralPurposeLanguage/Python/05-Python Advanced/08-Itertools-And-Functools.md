# Itertools and Functools — Notes

## What this covers
Two toolkit modules: `itertools` for fast, memory-efficient iterator building blocks, and `functools` for working with functions (caching, partial application, dispatch, reduction).

## Key points
- `itertools.chain(a, b, c)` combines multiple iterables into one stream. `itertools.cycle(x)` repeats an iterable forever. `itertools.count(start, step)` is an infinite counter.
- `itertools.product()` gives the Cartesian product; `permutations()`/`combinations()` give orderings/selections of a fixed length.
- `itertools.groupby(data)` groups **consecutive** equal items (sort first if you want all-matching-items grouped, not just runs).
- `itertools.islice(iterable, n)` slices an iterator without needing it to support indexing (works on infinite iterators too).
- More recipes: `accumulate()` (running totals or running result of any binary function), `starmap()` (like `map()` but unpacks each item as `*args`), `zip_longest()` (pads instead of truncating), `filterfalse()` (opposite of `filter()`), `tee()` (splits one iterator into `n` independent copies).
- `functools.reduce(func, iterable, [initial])` cumulatively combines items into one result.
- `functools.lru_cache(maxsize=...)` memoizes a function's results by argument; `functools.cache` (3.9+) is a simpler alias for `lru_cache(maxsize=None)` — unbounded, slightly less overhead since there's no eviction/order tracking.
- `functools.partial(func, arg=value)` pre-fills some arguments, returning a new callable.
- `functools.singledispatch` lets a function have different implementations based on the **type** of its first argument (register with `@func.register`), avoiding long `isinstance` chains.
- `functools.cmp_to_key()` adapts an old-style two-argument comparator (`negative/zero/positive`) into a `key=` function for `sorted()`.
- `operator` module gives function versions of operators (`operator.add`, `operator.itemgetter`, etc.) — often clearer/faster than an equivalent lambda, and commonly paired with `reduce`, `sorted`, or `map`.

## Gotchas (the part worth revising twice)
- `lru_cache`/`cache` only work correctly on functions with **hashable** arguments — a list or dict argument will raise `TypeError`.
- `groupby()` only groups **consecutive** matching items — if the input isn't already sorted/ordered by the grouping key, you'll get more groups than you expect.
- Choose `lru_cache(maxsize=N)` over `cache` when the cache needs to stay bounded (e.g. long-running processes with unbounded input) — `cache`/`lru_cache(maxsize=None)` never evicts.
- `tee()` shares the same caveat here as in the Iterators file: don't keep using the original iterator after teeing, and don't let one copy race far ahead of the others (memory grows).

## When it matters
Reach for `itertools` whenever you'd otherwise hand-write a loop for combining/slicing/grouping iterables — it's faster and more memory-efficient. Reach for `functools` for caching expensive pure functions, or building specialized callables (`partial`) without writing a new `def` each time.

## One-line recap example
```python
import functools

@functools.cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

fib(30)   # computed once per n, cached forever after
```
