# Lists — Notes

## What this covers
Python's `list` type: creating, indexing/slicing, adding/editing/deleting items, common methods, comprehensions, and internals like over-allocation and shallow vs deep copy.

## Key points
- Lists are ordered, mutable, allow duplicates, created with `[]` or `list()`.
- Add items: `.append()` (end), `.insert(i, x)` (position), `.extend(iterable)` (merge another iterable in).
- Remove items: `.remove(value)` (first match), `.pop(i)` (by index, returns it), `del list[i]`, `.clear()`.
- Common methods: `len()`, `sum()`, `min()/max()`, `.count()`, `.index()`, `.reverse()` (in place), `.sort()` (in place) vs `sorted()` (returns new list), `.copy()` (shallow).
- Never add/remove items in the list you are looping over — the loop walks by index, so removing shifts items left and the next one is silently skipped (`[2,4,6,1,8]` removing evens leaves `[4, 1]`). Safe patterns: loop over a copy `lst[:]`, rebuild with a comprehension (`lst[:] = [...]` to keep the same object), iterate indexes in reverse, `filter()`, or collect indexes first and delete from the highest down.
- List comprehension: `[expr for item in iterable if condition]` — concise way to build a list.
- `enumerate()` gives index+value pairs while looping; `zip()` combines multiple lists element-wise (also handy for building a dict: `dict(zip(keys, values))`).

## Gotchas (the part worth revising twice)
- Lists over-allocate capacity so most `.append()` calls are O(1); occasionally a resize+copy happens (O(n)) — averaged out, append is "amortized O(1)."
- Shallow copy (`.copy()`, `list[:]`) only copies the outer list — nested mutable objects (like inner lists) are still shared. Mutating a nested item affects both copies. Use `copy.deepcopy()` for full independence.
- `list.pop(0)` or `.insert(0, x)` are O(n) — they shift every remaining element. For a queue (FIFO), use `collections.deque` instead, which is O(1) at both ends.
- Sort is stable (Timsort) — equal elements keep their original relative order, which matters for multi-key sorts. Use `operator.itemgetter`/`attrgetter` as a fast `key=` instead of a lambda.
- Appending/inserting while looping can run forever (the list grows as fast as you read it) — build a new list instead.
- `x = lst.sort()` makes `x` `None`: in-place methods (`sort`, `reverse`, `append`, `extend`...) return `None`. Use `sorted(lst)` when you need the new list.
- Sorting mixed types (`[3, "a"]`, or anything with `None`) raises `TypeError` — sort by a common `key=` (e.g. `key=str`) or split by type.
- List comprehensions are usually as fast as or faster than `map()`/`filter()` with a lambda, because they avoid a Python-level function call per element.

## When it matters
The default go-to collection for an ordered, changeable group of items. Use `deque` instead when you need fast operations at the front; use comprehensions for simple transforms/filters, a real loop for anything more complex.

## One-line recap example
```python
nums = [5, 2, 8, 1]
squares = [n**2 for n in nums if n % 2 == 0]   # list comprehension: filter + transform
print(sorted(nums), squares)
```
