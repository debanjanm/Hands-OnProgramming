# Iterators — Notes

## What this covers
The difference between an iterable and an iterator, how `for` loops actually work under the hood, and how to build your own iterator classes and lazy pipelines.

## Key points
- **Iterable** = anything you can loop over (has `__iter__`). **Iterator** = the object that actually produces values one at a time (has `__next__`). Every iterator is an iterable, but not every iterable is an iterator.
- `iter(obj)` gets an iterator from an iterable. `next(it)` pulls the next value; when exhausted it raises `StopIteration`.
- A `for` loop is just `iter()` + repeated `next()` in a `try/except StopIteration` under the hood.
- Custom iterator class: implement `__iter__` (return `self`) and `__next__` (return next value or raise `StopIteration`).
- Best practice: separate the **iterable** (returns a fresh iterator each time `__iter__` is called) from the **iterator** (holds the position). This lets you loop over the same collection more than once.
- `iter(callable, sentinel)` keeps calling `callable()` until it returns the sentinel value.
- Built-ins like `sum()`, `max()`, `sorted()`, `enumerate()` all happily consume any iterator.
- `itertools.tee(source, n)` splits one iterator into `n` independent copies that share a buffer internally.
- Custom iterators can be chained/wrapped (e.g. one iterator that squares values fed from another) to build a lazy pipeline.
- `__length_hint__` gives an *estimate* of remaining items (used by `list()`/`tuple()` to pre-allocate) — unlike `__len__`, it's allowed to be wrong.

## Gotchas (the part worth revising twice)
- **Iterators are consumed once.** Once you've looped through one, it's empty — looping again gives nothing. This is a very common bug: passing the same iterator to two functions expecting both to see all values.
- Fix for the above: re-create the iterator, use `itertools.tee()`, or just iterate the original list/iterable instead of an already-obtained iterator.
- `tee()` caveat: don't keep using the original iterator after teeing it, and don't let one copy run far ahead of the others — the shared buffer grows in memory.
- An iterator holds only enough state to produce the *next* value — a `range(1_000_000)` iterator is tiny in memory compared to `list(range(1_000_000))`, even though both "represent" the same million numbers.

## When it matters
Reach for a custom iterator (or generator, see next file) whenever you need to process a sequence lazily — large/streaming data, infinite sequences, or a pipeline where each stage should only do work when a value is actually requested.

## One-line recap example
```python
it = iter([1, 2, 3])
list(it)   # [1, 2, 3]
list(it)   # [] — already exhausted, iterators are one-shot
```
