# GroupBy and Aggregation — Notes

## What this covers
The split-apply-combine model behind `.groupby()`, running aggregations with `.sum()`/`.mean()`/`.agg()`, the crucial difference between `.agg()` (collapses) and `.transform()` (broadcasts back), multi-column grouping, and `pivot_table()` as a groupby shortcut.

## Key points
- Split-apply-combine: split rows into groups by a key, apply a function to each group independently, combine the per-group results into one output indexed by the group key.
- `df.groupby('col')` alone is lazy — it builds a grouping plan but does no visible work until an aggregation (`.sum()`, `.mean()`, `.count()`, ...) is called on it.
- `.agg({'col1': 'sum', 'col2': ['sum', 'mean']})` applies different (or multiple) functions to different columns in a single call; named aggregation `.agg(total=('col', 'sum'))` gives clean flat output column names.
- `.transform('mean')` computes the same per-group aggregation as `.agg()`/`.mean()` but returns a result the same shape/index as the original DataFrame — every row gets its group's value attached, ready to use as a new column with no merge step.
- `groupby([col1, col2])` groups by every unique combination of the listed columns, producing a `MultiIndex` result; `.reset_index()` flattens it back to plain columns.
- `pd.pivot_table(df, values=, index=, columns=, aggfunc=)` is a groupby + reshape convenience wrapper — equivalent to `df.groupby([index, columns])[values].agg(aggfunc).unstack()`, but reads more naturally for a wide summary table.

## Gotchas (the part worth revising twice)
- Confusing `.agg()` and `.transform()` is the most common groupby mistake: `.agg()` collapses to one row per group (can't be assigned straight back as a column), `.transform()` keeps the original row count and index (can be).
- Aggregations like `.sum()`/`.mean()` silently drop non-numeric columns; `.count()` counts non-null values per column regardless of dtype — don't assume every column survives an aggregation the same way.
- A MultiIndex result from grouping by multiple columns needs `.loc[(key1, key2)]` (a tuple) to access one combination, and often `.reset_index()` before it can be merged/plotted like a normal DataFrame.

## When it matters
Summarizing data by category — total revenue per region, average score per student, counts per status — is one of the most common analysis tasks, and `pivot_table`/`groupby` are the direct pandas equivalent of a spreadsheet pivot table or a SQL `GROUP BY`.

## One-line recap example
```python
import pandas as pd
df = pd.DataFrame({"region": ["E", "E", "W"], "revenue": [10, 20, 30]})
df["region_avg"] = df.groupby("region")["revenue"].transform("mean")  # broadcast back, no merge
```
