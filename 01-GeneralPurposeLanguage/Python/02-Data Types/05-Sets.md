# Sets — Notes

## What this covers
Python's `set` type: creating, membership testing, adding/removing items, set algebra (union/intersection/difference), and why sets are fast — plus `frozenset`.

## Key points
- Sets are unordered, store only unique values, unindexed (no `set[0]`), created with `{}` (non-empty only) or `set()` — `{}` alone makes an empty **dict**, not a set.
- Add: `.add(item)` (one), `.update(iterable)` (many). Remove: `.remove(item)` (raises `KeyError` if missing), `.discard(item)` (no error), `.pop()` (arbitrary item), `.clear()`.
- Set algebra: `union()`/`|`, `intersection()`/`&`, `difference()`/`-`, `symmetric_difference()`/`^`. In-place versions: `update()`, `intersection_update()`, `difference_update()`.
- Set comprehension: `{expr for item in iterable}`.
- `frozenset` is the immutable, hashable version of set — usable as a dict key or nested inside another set (a plain `set` cannot be).

## Gotchas (the part worth revising twice)
- Sets are backed by a hash table — membership (`x in my_set`) is O(1) average, versus O(n) for `x in my_list` which scans every item. This is why only hashable objects can be set elements.
- `{[1, 2]}` raises `TypeError` — a list has no stable hash, so it can't go in a set (or be a dict key).
- Fast dedup: `list(set(items))` is O(n) but doesn't preserve order. The naive "check if in list, then append" approach is O(n²). For order-preserving dedup, use `dict.fromkeys(items)` instead.
- `set.pop()` removes an *arbitrary* item, not a specific one, since sets have no order.

## When it matters
Reach for a set whenever you need fast membership checks, need to dedupe, or need set algebra (finding common/different items between two collections). Use `frozenset` when the set itself needs to be hashable.

## One-line recap example
```python
a, b = {1, 2, 3}, {2, 3, 4}
print(a & b)           # {2, 3} - intersection, O(len(a)+len(b))
print(3 in a)           # O(1) average, unlike list membership
```
