# NumPy Recipes and Real Patterns — Notes

## What this covers
Worked, realistic patterns that combine earlier topics: scaling and standardising data, one-hot encoding, pairwise distances by broadcasting, moving averages and running maxima, image-like 3D arrays, seeded Monte Carlo, a tiny k-means, batch matrix operations, `datetime64`/`timedelta64` and business-day functions, boolean-mask idioms, loop-avoidance patterns, a least-squares regression, and a loop-vs-vectorized cheat sheet.

## Key points
- Min-max `(x - lo) / (hi - lo)` and z-score `(x - mean) / std` per column: `axis=0` with `keepdims=True`, and guard zero spread.
- One-hot: `np.eye(K)[labels]` or `labels[:, None] == np.arange(K)`; for text use `np.unique(return_inverse=True)` first.
- Pairwise distances: `P[:, None, :] - P[None, :, :]` makes `(n, n, d)`; sum squares on the last axis. The dot-product trick `|a|^2 + |b|^2 - 2 a.b` saves memory.
- Moving average: `np.convolve(..., 'valid')`, cumsum difference, or `sliding_window_view(...).mean(axis=1)`. Running max: `np.maximum.accumulate`.
- Images are `(H, W, 3)` uint8. Crops and flips are views; grayscale is `img @ [0.299, 0.587, 0.114]`; brightness math needs a wider dtype and `np.clip`.
- Monte Carlo: one seeded `np.random.default_rng(seed)`, draw in bulk, error shrinks like `1/sqrt(N)`.
- k-means-lite: assignment by broadcasting + `argmin`, update by masked means; only the iteration loop remains.
- `@` / `matmul` / `solve` / `det` broadcast over leading batch axes.
- `datetime64[unit]` + `timedelta64`; `np.arange` makes date ranges; divide a timedelta by `np.timedelta64(1, 'W')` for numbers.
- `np.is_busday`, `busday_count`, `busday_offset` support `weekmask`, `holidays`, and `roll=`.
- Mask idioms: `& | ~` with parentheses, `mask.sum()`, `mask.mean()`, `np.flatnonzero`, `np.where`, `np.select`, `~np.isnan`.
- Regression: design matrix with a ones column, `np.linalg.lstsq(X, y, rcond=None)`, R² from residuals.

## Gotchas (the part worth revising twice)
- Forgetting `axis=0` scales every feature by one global min/max. Fit scaling constants on training data only.
- A constant column gives `0/0 = nan`; replace the zero spread with 1.
- The dot-product distance trick can produce tiny negative squares - `np.maximum(..., 0)` before `sqrt`.
- Moving-average output is `w - 1` shorter than the input; `'same'` mode is zero-padded at the edges.
- Slicing a crop gives a view: writing to it edits the image. `img + 100` on uint8 wraps; widen, add, clip, cast back.
- `tiny.T` on an image reverses all axes including channels; use `transpose(1, 0, 2)`.
- Monte Carlo results are reproducible only with a fixed seed AND the same draw order.
- `np.dot` on 3-D stacks does not batch; use `@`.
- `busday_count` excludes the end date; `busday_offset` raises on a weekend start unless `roll=` is given.
- `argmax` of an all-False mask returns 0 - check `mask.any()` first.
- Forgetting the ones column in regression forces the line through the origin.
- Vectorizing tiny arrays can be slower; recursions (EMA, state machines) still need a loop.

## When it matters
These are the bread-and-butter steps of data preparation, feature engineering, simulation and basic modelling. Knowing the idiom for each lets you write short, loop-free code and check it against a tiny loop version.

## One-line recap example
```python
import numpy as np
X = np.array([[1.0, 200.0], [2.0, 400.0], [4.0, 800.0]])
print((X - X.min(axis=0)) / np.ptp(X, axis=0))   # per-column min-max scaling
```
