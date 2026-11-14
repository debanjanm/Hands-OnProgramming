# Unpacking and Packing — Notes

## What this covers
Assigning elements of an iterable to multiple variables at once (unpacking), and gathering multiple values into one collection (packing) — including `*args`/`**kwargs`, extended unpacking with `*`, and some real-world patterns.

## Key points
- Basic unpacking: `a, b, c = (1, 2, 3)` — works for any iterable, not just tuples.
- Swap without a temp variable: `x, y = y, x`.
- Extended unpacking with `*`: `first, *rest = [1,2,3,4,5]` — `*rest` gathers "everything else" into a list; works at the start, middle, or end.
- Use `_` to explicitly ignore a value you don't need: `first, _, third = (1, 2, 3)`.
- Nested unpacking works: `(a, b), c = (1, 2), 3`.
- `*args` unpacks a list/tuple into positional function arguments: `add(*numbers)`. `**kwargs` unpacks a dict into keyword arguments: `greet(**person)`.
- Merging with unpacking: `[*list1, *list2]` for lists, `{**dict1, **dict2}` for dicts (later keys win on conflict).
- Function definitions can *pack* incoming args: `def summarize(*args, **kwargs)` gathers extra positional args into a tuple and extra keyword args into a dict.
- A function that does `return a, b` is packing a tuple; the caller commonly unpacks it immediately: `low, high = min_max(...)`.
- `zip(*matrix)` is the classic unzip/transpose trick — unpacks each row as a separate arg to `zip()`, regrouping by column.

## Gotchas (the part worth revising twice)
- A generator/iterator can only be consumed once. Unpacking it exhausts it — unpacking or iterating it again silently yields nothing (or raises `ValueError` if you try to unpack again into the same number of names and it's now empty).
- The `first, *rest` starred pattern also works directly as a for-loop target, unpacking each row of a sequence-of-sequences per iteration.
- `{**dict1, **dict2}` resolves key conflicts with dict2 (the later one) winning — same rule as `dict.update()`.

## When it matters
Everywhere function signatures need flexibility (`*args`/`**kwargs`), whenever a function needs to "return multiple values," and whenever you're pulling apart tuples/rows in a loop. `zip(*matrix)` specifically is the go-to trick for transposing data.

## One-line recap example
```python
first, *rest = [1, 2, 3, 4]     # first=1, rest=[2, 3, 4]
def f(*args, **kwargs): pass    # packs extra positional/keyword args
f(*rest, key="value")           # unpacks rest back out as separate args
```
