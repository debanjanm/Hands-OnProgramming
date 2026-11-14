# Generators — Notes

## What this covers
Generators: functions that use `yield` to produce values lazily, one at a time, instead of building a whole list upfront. Includes two-way communication (`send`), delegation (`yield from`), and generator-based pipelines.

## Key points
- A generator function uses `yield` instead of `return`. Calling it doesn't run the body — it returns a generator object; code runs (and pauses) as you call `next()` on it.
- Generator expressions: same syntax as a list comprehension but with `()` instead of `[]` — lazily evaluated, one value at a time.
- `StopIteration` is raised automatically once a generator's body finishes — same protocol as any iterator.
- `yield from other_gen` delegates to another generator/iterable, yielding all of its values in place.
- `gen.send(value)` sends a value INTO the generator at the point it's paused (received as the result of the `yield` expression). You must `next(gen)` once first to "prime" it (advance to the first `yield`).
- `gen.throw(Exception)` injects an exception at the current yield point; `gen.close()` stops the generator and runs any `finally` block.
- Infinite generators (`while True: yield ...`) are safe because nothing is computed until you actually pull values.
- Generators chain naturally into pipelines — each stage pulls from the previous one, nothing runs until the final consumer starts pulling (true lazy evaluation, useful for ETL-style filter -> transform -> aggregate).
- `next(gen, default)` returns `default` instead of raising `StopIteration` once exhausted — avoids a try/except for exhaustion checks.
- `@contextlib.contextmanager` is built on generators: code before `yield` acts as `__enter__`, code after acts as `__exit__` (full depth in the Context-Managers file).

## Gotchas (the part worth revising twice)
- You must call `next(gen)` once before the first `.send()` — sending into a generator that hasn't reached its first `yield` yet raises an error.
- A list comprehension materializes the whole thing in memory immediately; the generator-expression equivalent stays at a tiny, near-constant size no matter how large the range — this is the real reason to prefer generators for big data.
- Once a generator is exhausted, it stays exhausted — same one-shot behavior as iterators in general.
- `yield` pauses and resumes function state (locals, position) exactly the way `__enter__`/`__exit__` need to — that's *why* `@contextmanager` can be built from a plain generator function with a single `yield` splitting setup from teardown.

## When it matters
Use generators for large or streaming data (files, DB cursors, ETL pipelines), infinite sequences, or any time you want computation to happen only as values are actually consumed rather than all at once.

## One-line recap example
```python
def count_up_to(limit):
    n = 1
    while n <= limit:
        yield n
        n += 1

print(list(count_up_to(3)))  # [1, 2, 3] — computed lazily, one at a time
```
