# Advanced NumPy — Notes

## What this covers
Five specialized NumPy tools: structured arrays (record-style tables),
masked arrays (handling missing/invalid data), `meshgrid` (coordinate
grids), `polyfit`/`poly1d` (curve fitting), and `np.select` (multi-branch
vectorized selection).

## Key points
- **Structured arrays**: `np.dtype([('name', 'U10'), ('age', 'i4')])` defines
  named, typed fields; `arr['field']` pulls that column across all records —
  a lightweight table without pandas.
- **Masked arrays** (`numpy.ma`): `ma.masked_where(condition, data)` marks
  values invalid; `.mean()`, `.sum()`, etc. on the masked array automatically
  skip masked entries. `.compressed()` returns just the valid values.
- **`np.meshgrid(x, y)`**: turns two 1D coordinate arrays into 2D grids `X, Y`
  covering every `(x, y)` combination — used to evaluate `f(x, y)` over an
  entire 2D surface in one vectorized call.
- **`np.polyfit(x, y, deg)`**: least-squares fits polynomial coefficients to
  data points (`deg=1` = linear regression). `np.poly1d(coeffs)` wraps them
  into a callable function.
- **`np.select(condlist, choicelist, default=)`**: generalizes `np.where`
  (binary if/else) to many conditions, evaluated in order like an
  if/elif/elif chain — but vectorized across a whole array.

## Gotchas (the part worth revising twice)
- Forgetting to mask sentinel/error values (e.g. `-999` for a bad sensor
  reading) before averaging silently corrupts the result — plain `.mean()`
  on unmasked data includes the garbage values.
- `np.select` evaluates conditions **in order** and the first match wins —
  order your conditions from most to least specific, same as if/elif.
- `polyfit` coefficients come back **highest power first** — easy to
  transpose when reading them by hand.

## When it matters
Structured arrays and masked arrays show up in real datasets with mixed
fields or missing values (sensor logs, CSV imports). `meshgrid` is standard
for plotting surfaces/contours or grid-based simulations. `polyfit` is a
quick fit for trend lines. `np.select` replaces messy nested `np.where` or
loops when categorizing data into more than two buckets.

## One-line recap example
```python
import numpy as np
scores = np.array([95, 82, 60])
grades = np.select([scores >= 90, scores >= 80], ['A', 'B'], default='F')
```
