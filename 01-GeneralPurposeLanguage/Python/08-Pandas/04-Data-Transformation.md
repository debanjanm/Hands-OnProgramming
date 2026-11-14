# Data Transformation — Notes

## What this covers
Applying custom logic with `.apply()`/`.map()`, why vectorized operations should be the first reach instead of `.apply()`, sorting, distinct-value inspection, and value substitution with `.replace()`.

## Key points
- `Series.apply(func)` calls `func` per element; `DataFrame.apply(func, axis=0)` (default) calls it per column; `axis=1` calls it per row — use `axis=1` when a computation genuinely needs multiple columns together.
- `.map()` exists only on a Series — it substitutes values via a dict, another Series, or a function. Values missing from a dict/Series mapping become `NaN`.
- Vectorized operations (`df['a'] * df['b']`, comparisons, `.str`/`.dt` accessors, `np.where`) run as compiled loops and are dramatically faster than `.apply()`, which pays Python function-call overhead per row/element — `.apply()` is a last resort, not a first reach.
- `.sort_values(by=col_or_list, ascending=...)` sorts by column value(s) (accepts a list for multi-column sort); `.sort_index()` sorts by the row index label instead.
- `.value_counts()` gives distinct-value counts sorted descending by default (`normalize=True` gives proportions); `.unique()` gives distinct values in first-appearance order; `.nunique()` gives the count of distinct values.
- `.replace(old_to_new)` swaps specific values; unlike `.map()`, values not in the mapping are left **unchanged** rather than becoming `NaN`.

## Gotchas (the part worth revising twice)
- `.apply(axis=1)` looks convenient but was measured here at roughly 3000x slower than the vectorized equivalent on 200,000 rows — always check whether the same result can be expressed as direct arithmetic/comparison/built-in Series method first.
- `.map()` turns unmapped values into `NaN`; `.replace()` leaves them as-is — picking the wrong one silently loses or silently keeps data depending on which behavior you actually wanted.
- `.map()` is Series-only; calling it on a DataFrame is a common source of `AttributeError` — use `.apply()` or `.applymap()`-style per-column mapping for DataFrame-wide substitution instead.

## When it matters
Almost every real transformation — deriving a column from others, recoding categories, ranking, deduplicating value lists — goes through one of these tools; picking `.apply()` by default instead of vectorized code is the most common performance mistake in pandas scripts.

## One-line recap example
```python
import pandas as pd
s = pd.Series(["Widget", "Gadget"])
s.map({"Widget": "Hardware"})       # ['Hardware', nan]   - unmapped -> NaN
s.replace({"Widget": "Hardware"})   # ['Hardware', 'Gadget'] - unmapped unchanged
```
