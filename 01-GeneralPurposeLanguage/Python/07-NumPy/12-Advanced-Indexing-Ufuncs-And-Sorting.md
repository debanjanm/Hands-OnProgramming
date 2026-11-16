# Advanced Indexing, Ufuncs and Sorting — Notes

## What this covers
Index-based tools beyond basic slicing (`take`, `put`, `take_along_axis`, `ix_`, `ravel_multi_index`), ufunc methods (`reduce`, `accumulate`, `outer`, `at`, `reduceat`), why `np.vectorize` is not fast, `einsum`, lookup and counting tools (`searchsorted`, `digitize`, `unique`, `bincount`, `histogram`), set operations, sorting (`kind`, `partition`, `lexsort`), nan-aware functions, cumulative ops, `diff`/`gradient`/`convolve`/`correlate`, and rounding/clipping variants.

## Key points
- `np.take(a, idx, axis, mode)` = fancy indexing with an axis and `mode='clip'|'wrap'`; `np.put` writes into the **flattened** array.
- `take_along_axis` / `put_along_axis` apply per-row/column index arrays (the partner of `argsort`, `argmax(keepdims=True)`).
- `a[np.ix_(rows, cols)]` selects a sub-grid; `a[rows, cols]` selects paired points. `ravel_multi_index` / `unravel_index` convert between 2-D and flat positions.
- Every binary ufunc has `.reduce`, `.accumulate`, `.outer`, `.at`, `.reduceat`. `np.add.reduce` is `sum`, `np.maximum.accumulate` is a running max.
- `np.add.at(a, idx, v)` handles repeated indexes; `a[idx] += v` does not.
- `np.vectorize` and `np.frompyfunc` are syntax helpers - still one Python call per element. `apply_along_axis` is also a loop.
- `einsum`: letters name axes; letters missing after `->` are summed. Covers dot, outer, trace, transpose, matmul, batched matmul.
- `searchsorted` = binary search (insertion point); `digitize` = bin index; `bincount` = fast integer counts (with `weights=` for group sums); `unique(..., return_index/inverse/counts)`.
- `histogram` bins are half-open except the last; `histogram2d` rows are X bins.
- Set ops (`union1d`, `intersect1d`, `setdiff1d`, `setxor1d`) return sorted unique values; `np.isin` keeps shape and order.
- Sorting: `np.sort` copies, `a.sort()` is in place; `kind='stable'` keeps ties in order; `partition`/`argpartition` give O(n) top-k; `lexsort` sorts by many keys (last key is primary).
- `nansum`, `nanmean`, `nanmax`, ... skip nans. `cumsum`, `cumprod`, `diff`, `gradient`, `convolve`, `correlate` are the signal/series basics.
- `clip`, `round`/`rint` (half to even), `floor`, `ceil`, `trunc`, `floor_divide`, `mod` vs `fmod`.

## Gotchas (the part worth revising twice)
- `a[[0,0,1]] += 1` counts index 0 only once; use `np.add.at` or `np.bincount`.
- `searchsorted` and `digitize` need sorted bins; unsorted input gives silent garbage.
- `scores[argsort_result]` indexes rows, not within-row elements - use `take_along_axis`.
- `argmax` on 2-D returns a flat index; `np.unravel_index` gives (row, col).
- `np.vectorize` guesses output dtype from the first result (can truncate floats to ints) and fails on empty input without `otypes=`.
- `np.sort` default is not stable; multi-pass sorting requires `kind='stable'`. NaNs sort last.
- `lexsort` keys are reversed: the last key is the main one. Negate numbers for descending.
- `bincount` allocates `max+1` slots - huge labels waste memory; negatives raise `ValueError`.
- `np.round(2.5) == 2.0` (half to even); `astype(int)` truncates toward zero, not floor.
- `np.convolve` flips the kernel; `np.correlate` does not. `'same'` mode zero-pads the edges.
- `np.max` and `np.mean` propagate nan; `nanargmax` raises on an all-nan slice.
- `cumprod` overflows silently on fixed-size ints.

## When it matters
Group-by style work without pandas (`bincount` with weights, `add.at`), top-k selection, lookups of "which bucket / nearest value", per-row ranking, deduplication, and writing compact tensor code with `einsum`. Knowing which tools are really loops (`vectorize`, `apply_along_axis`) tells you where speed will not come from.

## One-line recap example
```python
import numpy as np
labels, vals = np.array([0, 2, 2, 1]), np.array([1.0, 2.0, 3.0, 4.0])
print(np.bincount(labels, weights=vals))   # group sums: [1. 4. 5.]
```
