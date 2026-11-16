# Advanced GroupBy, Window and Method Chaining — Notes

## What this covers
The advanced side of groupby (`transform`, `filter`, `apply`, named aggregation, `rank`, `cumcount`/`ngroup`, `nth`/`head`), window functions (`rolling`, `expanding`, `ewm`, with `min_periods`, `center`, `closed`, time windows and `apply`), cumulative ops (`cumsum`, `diff`, `pct_change`), method chaining with `pipe`/`assign`/`query`, and a set of handy tools: `crosstab`, `merge_asof`, merge `indicator`/`validate`, `explode`, `combine_first`, `clip`, `nlargest`/`nsmallest`, `describe` options and `sample`. Basics are in 05 (groupby), 06 (merge) and 08 (resample); `query`/`eval`/`where` are in 11.

## Key points
- `transform` returns the same index as the input, so group means, shares and z-scores can be assigned straight back as columns.
- `groupby.filter(func)` keeps or drops WHOLE groups (func returns one True/False per group).
- `apply` is the flexible, slowest option. On pandas 2.2 select columns after `groupby` (or `include_groups=False`) so the grouping columns are not passed in; `group_keys=False` keeps the original index.
- Named aggregation `agg(total=("revenue", "sum"))` gives flat column names and avoids MultiIndex columns.
- Built-in aggregation names run in compiled code; a custom function is called once per group in Python. Prefer built-ins and combine columns afterwards.
- `rank(method=..., ascending=..., pct=True)` inside a group; `rank <= N` gives top N per group.
- `cumcount()` numbers rows inside each group; `ngroup()` gives one integer id per group.
- `head`, `tail`, `nth` are filters: they keep the original index and use the CURRENT row order (sort first).
- `rolling(n)`: first `n-1` values are NaN unless `min_periods` is lower; `center=True` centres the window; `closed="left"` excludes the current row (avoids look-ahead); a string window such as `"2D"` on a DatetimeIndex is calendar based.
- `rolling(n).apply(func, raw=True)` runs custom logic per window (raw=True passes NumPy arrays: faster).
- `expanding()` is a running statistic; `ewm` weights recent values more (`span`, `alpha`, `halflife`; `adjust` changes early values).
- `pct_change(fill_method=None)` is the clean form in pandas 2.2; `diff`, `cumsum` and friends restart per group when used after `groupby`.
- Chaining: one step per line inside brackets, `assign(col=lambda d: ...)` for new columns, `pipe(func, *args)` to insert your own function.
- `pd.crosstab` makes frequency tables (`margins=True`, `normalize="index"`, or `values=` plus `aggfunc=`).
- `merge_asof` joins each row to the nearest earlier (or later) key; both sides must be sorted; use `by=` for groups and `tolerance=` to limit distance.
- `merge(..., indicator=True)` shows which side each row came from; `validate="one_to_one"` etc. raises `MergeError` on wrong key relationships.
- `explode` gives one row per list item (index is repeated; use `ignore_index=True`). `combine_first` patches NaN from a second frame (union of labels). `clip` caps values. `nlargest`/`nsmallest` are faster than a full sort. `sample(random_state=...)` is repeatable.

## Gotchas (the part worth revising twice)
- `groupby(...).rolling(n)` adds the group key to the index; use `.droplevel(0)` before assigning back.
- `nth`, `head` and `tail` follow the present row order, so "first" is wrong if data is not sorted.
- `merge_asof` raises if either side is unsorted, and a `by=` group missing in the right frame just gives NaN.
- A duplicated key on the "one" side of a merge multiplies rows silently; `validate=` makes it an error.
- A custom lambda in `agg` can be hundreds of times slower than a built-in; several unnamed lambdas get confusing auto names.
- `ewm` with `adjust=True` and `adjust=False` give different early values; pick one on purpose.
- `pct_change()` without `fill_method=None` forward-fills NaN first (and warns in 2.2).
- `explode` leaves an `object` column and duplicates the index; empty lists become NaN rows.
- `sample` without `random_state` is not repeatable; with `frac=` the result order is shuffled.

## When it matters
Feature engineering (group shares, rank within group, previous value, rolling average), time-aligned joins (trades with the latest quote), cleaning list-like columns, and writing readable pipelines. Choosing `agg`/`transform`/built-ins over `apply` is often the difference between seconds and minutes on large data.

## One-line recap example
```python
import pandas as pd
df = pd.DataFrame({"k": list("aabb"), "v": [1, 2, 3, 5]})
df["roll"] = df.groupby("k")["v"].rolling(2, min_periods=1).mean().droplevel(0)  # per-group rolling, aligned back
```
