# Collections Module — Notes

## What this covers
The `collections` module — specialized container types that solve common problems the built-in `dict`/`list` handle awkwardly: counting, grouping, queues, and readable tuples.

## Key points
- **`Counter`** — counts hashable items. `counts["missing"]` returns `0` instead of raising `KeyError`. `.most_common(n)` gives the top N.
- **`Counter` arithmetic** — `+ - & |` act like set/multiset ops (add, subtract, min, max) and drop zero/negative results; `.subtract()` mutates in place and *does* allow negatives.
- **`defaultdict(factory)`** — auto-creates a value (via `list`, `int`, or any zero-arg callable) the first time a key is touched, so no manual "if key not in dict" checks.
- **`deque`** — double-ended queue, O(1) append/pop from *both* ends (a plain `list` is O(n) at the front). `dq.rotate(n)` shifts elements around.
- **`deque(maxlen=N)`** — fixed-size rolling buffer; once full, adding an item silently drops the oldest one. Good for "last N events".
- **`namedtuple`** — tuple with named fields (`p.x` instead of `p[0]`). `._asdict()`, `._replace()` (returns a new one, doesn't mutate), `._fields`.
- **`OrderedDict`** — regular dicts keep insertion order since 3.7 too, but `OrderedDict` adds extras like `.move_to_end()`.
- **`ChainMap`** — layers multiple dicts into one view; lookups check the first dict first, falling back to the next. Good for config overrides + defaults.
- **`UserDict`/`UserList`/`UserString`** — wrap a real dict/list/str internally, meant for subclassing when you want to override methods reliably.

## Gotchas (the part worth revising twice)
- Subclassing `dict`/`list` directly can misbehave — some built-in methods bypass your overrides. Use `UserDict`/`UserList`/`UserString` instead when you need reliable overriding.
- `Counter - Counter` (operator) silently drops zero/negative counts; `Counter.subtract()` does the opposite and keeps negatives. Easy to mix these up.
- `namedtuple` subclasses should set `__slots__ = ()` to stay lightweight (no per-instance `__dict__`).
- `defaultdict`'s factory is any zero-arg callable, not just `list`/`int` — you can pass a custom function that returns a whole dict.

## When it matters
Reach for these whenever a plain dict/list starts needing "if missing, do X" logic, when you're tallying/counting things, or when you need a queue/rolling buffer without hand-rolling one.

## One-line recap example
```python
from collections import Counter, defaultdict
counts = Counter(["a", "b", "a"])       # Counter({'a': 2, 'b': 1})
groups = defaultdict(list)
groups["x"].append(1)                   # no KeyError, auto-creates the list
```
