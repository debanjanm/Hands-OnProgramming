# Dictionary — Notes

## What this covers
Python's `dict` type: key-value pairs — creating, accessing, adding/editing/deleting, iteration, comprehensions, and internals like insertion order and hash collisions.

## Key points
- Dicts store key-value pairs, keys are unique and must be hashable (immutable), created with `{}` or `dict()`.
- Access: `d["key"]` (raises `KeyError` if missing) or `d.get("key", default)` (returns `None` or a default instead).
- Add/edit: `d["key"] = value`, or `.update({...})` / `.update(**kwargs)` to merge/overwrite multiple at once.
- Delete: `.pop(key)` (returns value), `.popitem()` (removes last inserted pair), `del d[key]`, `.clear()`.
- Iterate: `for k in d` (keys), `.values()`, `.items()` (key-value pairs) — these return live "view" objects, not lists.
- Dict comprehension: `{k: v for k, v in ... }`.
- Merging: `dict1 | dict2` (new dict, 3.9+), `dict1.update(dict2)` (in place), `dict1 |= dict2` (in-place operator version) — right-hand side wins on key conflicts.
- Safe key removal/addition while looping: `for k in list(d)` (snapshot), rebuild with a dict comprehension, collect keys then delete, or loop over `d.copy()`. `.pop(k, default)` never raises; `del d[k]` and `.pop(k)` raise `KeyError` on a missing key.
- Read a key with `d[k]` (KeyError), `d.get(k, default)` (no error) or test with `k in d` — `in` checks KEYS only; `v in d.values()` is an O(n) scan (build a reverse dict if you search by value a lot).
- `dict.setdefault(key, default)` and `collections.defaultdict(factory)` both avoid manual "if key not in dict" checks, handy for grouping/counting.

## Gotchas (the part worth revising twice)
- Since Python 3.7, insertion order is a language guarantee, not an implementation detail — `dict.fromkeys(items)` is a handy order-preserving dedup trick.
- Dicts are hash tables like sets: O(1) average lookup/insert/delete, collisions resolved via open addressing. A separate insertion-order array is what preserves order without losing O(1) lookups.
- `sorted(d)`/`min(d)`/`max(d)` operate on keys by default — use `key=d.get` to sort/min/max by value instead.
- Adding or removing a key while looping raises `RuntimeError: dictionary changed size during iteration` (the hash table may be resized, which would invalidate the iterator). Changing the VALUE of existing keys is allowed.
- `dict.fromkeys(keys, [])` gives every key the SAME list — one `append` shows up everywhere. Use `{k: [] for k in keys}` (or `defaultdict(list)`); `fromkeys` is fine for immutable values like `0` or `None`.
- `d.get(k)` can't tell "missing" from "stored as `None`" — use `k in d`.
- Keys must be hashable: list/dict/set keys raise `TypeError`; tuples and frozensets work (a tuple holding a list does not). A custom class that defines `__eq__` without `__hash__` becomes unhashable; define both consistently (equal objects must have equal hashes).
- Defining `__missing__(self, key)` on a `dict` subclass lets you customize missing-key behavior — this is literally how `defaultdict` works under the hood.

## When it matters
The default choice for any lookup-by-key structure — caches, counting, grouping, config, JSON-like data. Use `defaultdict` for grouping/counting to skip the "does this key exist yet" boilerplate.

## One-line recap example
```python
from collections import defaultdict
groups = defaultdict(list)
for word in ["apple", "banana", "avocado"]:
    groups[word[0]].append(word)   # missing key auto-creates []
```
