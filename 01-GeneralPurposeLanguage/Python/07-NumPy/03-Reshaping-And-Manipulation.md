# NumPy Reshaping and Manipulation — Notes

## What this covers
Changing an array's shape without changing its data: `reshape`, flattening, transposing, joining arrays together, splitting them apart, and adding/removing dimensions.

## Key points
- `arr.reshape(rows, cols)` reinterprets the same data with a new shape — total element count must match; pass `-1` for one dimension to let NumPy compute it.
- `ravel()` flattens to 1D as a view when possible (cheap); `flatten()` always returns an independent copy (safer, costs memory).
- `.T` / `.transpose()` swaps axes — for 2D, rows become columns.
- `np.concatenate([a, b], axis=...)` joins along an existing axis; `vstack` = axis 0 (rows), `hstack` = axis 1 (columns) for 2D arrays.
- `np.split(arr, n)` requires an exact equal division and errors otherwise; `np.array_split(arr, n)` tolerates uneven splits.
- `np.newaxis` (or `np.expand_dims`) inserts a new length-1 axis, e.g. to turn a 1D vector into a row or column vector; `.squeeze()` removes all length-1 axes.

## Gotchas (the part worth revising twice)
- `reshape()` and `ravel()` return **views** when the data layout allows it — mutating the reshaped/raveled array can mutate the original. `flatten()` is the one that's always a safe, independent copy.
- `np.split` throws `ValueError` on an uneven division; `np.array_split` silently distributes the remainder instead — pick based on whether an uneven split should be an error.
- `reshape(-1, n)` and `reshape(n, -1)` give different results (rows vs. columns) — the `-1` fills whichever slot it's placed in.

## When it matters
Reshaping is constant in data prep for ML models (flattening images, adding a batch dimension with `newaxis`), and joining/splitting arrays is routine when combining datasets or batching data for processing.

## One-line recap example
```python
import numpy as np
img = np.arange(12).reshape(3, 4)     # reshape data into a 3x4 grid
batch = img[np.newaxis, :, :]         # add a batch dimension -> shape (1, 3, 4)
```
