# End-To-End Data Analysis — Notes

## What this covers
One complete small workflow on a seeded synthetic orders/customers/products dataset: load, inspect, clean with written decisions, validate with assertions, merge, engineer features, compute KPIs, top-N, a cohort retention table, rolling trends, outlier flags, a `pipe` pipeline, a data-quality checklist, saving and reading back results, and four common pandas anti-patterns with their fixes.

## Key points
- Follow a fixed order: load, inspect, clean, validate, enrich, analyse, save, report. Keep the raw data untouched and work on copies.
- Write each cleaning decision (drop, fill, flag) with its reason, and print row counts after every step as a cleaning log.
- Turn assumptions into `assert` checks right after cleaning: unique keys, no nulls in critical columns, valid ranges, expected date window.
- Merge with `validate="m:1"` and `indicator=True`, then assert the row count did not change.
- Features: vectorized arithmetic, `.dt` parts, `groupby().transform`, `pd.cut`, `np.select`.
- KPIs with named aggregation; compute ratios (AOV) after aggregating. Top-N with `nlargest` or sort + `groupby().head(n)`.
- Cohort table: cohort = first order month, index = months since, `pivot_table(..., aggfunc="nunique")`, divide by the month-0 column for retention.
- Resample to a regular daily series before `rolling`. Flag outliers (IQR, z-score) instead of silently deleting them.
- Small functions plus `df.pipe(f).pipe(g)` make a repeatable, testable pipeline; compare it to the step-by-step result.
- A quality-report function returning a PASS/FAIL table can run before and after cleaning on every new data drop.
- Save to a `tempfile.TemporaryDirectory()`, read back and compare. Parquet keeps dtypes; guard with `try/except ImportError`.

## Gotchas (the part worth revising twice)
- `iterrows` is slow and promotes mixed int/float rows to all float. Use column math, `np.where`, or `itertuples`.
- `df[mask]["col"] = v` edits a temporary copy and does not change `df`. Use `df.loc[mask, "col"] = v`; take `.copy()` after slicing if you will edit.
- `pd.concat` in a loop copies everything every time (quadratic) and can drift dtypes. Collect pieces in a list and concat once.
- `apply(axis=1)` runs Python per row; use vectorized operations, `.str`, `.dt`, `np.where`, or `map`.
- A merge with duplicate keys on the right silently multiplies rows unless you pass `validate=`.
- IQR flags many points on skewed money data; z-scores hide extremes because the outlier inflates the std. Neither means "delete".
- CSV loses dtypes (dates, categories, Period); parquet keeps them but needs an engine installed.
- Cohort cells for recent cohorts are NaN (not yet observed), not zero.
- Rolling over irregular rows counts rows, not days. Resample first.

## When it matters
Any real analysis handed to someone else: it must be re-runnable, auditable and checked. The same skeleton works for sales, web logs, surveys and finance data.

## One-line recap example
```python
import pandas as pd
raw = pd.DataFrame({"q": [1, 1, -1], "d": ["2024-01-01", "2024-01-01", "x"]})
clean = (raw.assign(d=lambda t: pd.to_datetime(t["d"], format="%Y-%m-%d", errors="coerce"))
            .drop_duplicates().dropna(subset=["d"]).query("q > 0"))
assert clean["q"].gt(0).all()
```
