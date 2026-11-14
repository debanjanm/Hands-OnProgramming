# NumPy Statistical and Math Functions — Notes

## What this covers
Reducing arrays with `sum`/`mean`/`std`/`var`/`min`/`max`, understanding what `axis=` actually does, running totals with `cumsum`/`cumprod`, sorting with `sort`/`argsort`, locating extremes with `argmax`/`argmin`, and both forms of `np.where`.

## Key points
- Without `axis=`, reductions (`sum`, `mean`, `std`, `var`, `min`, `max`) collapse the whole array to one scalar.
- **`axis=N` means "this axis disappears from the result."** For a `(2, 3)` matrix: `sum(axis=0)` removes axis 0 (rows) and gives one value **per column** (shape `(3,)`); `sum(axis=1)` removes axis 1 (columns) and gives one value **per row** (shape `(2,)`).
- `cumsum`/`cumprod` return a running total/product, same size as the input.
- `np.sort(arr)` returns a new sorted array; `arr.sort()` sorts in place and returns `None`. `np.argsort(arr)` returns the indices that would sort it — useful for sorting one array by another's order.
- `argmax`/`argmin` return the **index** of the extreme value, not the value itself.
- `np.where(condition)` (1-arg) returns a tuple of index arrays (like `nonzero`) — not the matching values. `np.where(condition, if_true, if_false)` (3-arg) is a vectorized ternary, building a new array elementwise.

## Gotchas (the part worth revising twice)
- Mixing up axis 0 vs axis 1 is the single most common NumPy confusion — remember: the axis you name is the one that gets collapsed away, not the one that survives.
- `np.where(condition)` alone gives you indices, not values — you still need `data[np.where(condition)]` (or just `data[condition]`) to get the actual matching values.
- `np.sort` vs `.sort()`: one is non-mutating (safe, returns new array), the other mutates in place and returns `None` — assigning `x = arr.sort()` gives you `None`, not the sorted array.

## When it matters
Per-column vs per-row aggregation (axis) comes up in almost every real dataset — averaging feature columns, summing per-sample rows. `np.where`'s 3-arg form is the standard way to build derived columns/labels without writing a loop.

## One-line recap example
```python
import numpy as np
m = np.array([[1, 2], [3, 4]])
print(m.sum(axis=0))              # [4, 6] - one sum per column
print(np.where(m > 2, m, 0))      # [[0, 0], [3, 4]] - keep, else 0
```
