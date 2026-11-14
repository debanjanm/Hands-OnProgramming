# NumPy Indexing and Slicing — Notes

## What this covers
How to pull data out of arrays with basic indexing, slicing, boolean masks, and fancy indexing — and the single biggest gotcha in NumPy: which of these share memory with the original array and which don't.

## Key points
- Basic indexing: `arr[0]`, `arr[-1]` for 1D; `arr[row, col]` for 2D (preferred over `arr[row][col]`, which builds a temp array first).
- Slicing (`arr[1:3]`, `arr[:, 0]`, `arr[::-1]`) extends Python's `start:stop:step` syntax to any axis; a bare `:` means "everything along this axis".
- Boolean/mask indexing: `arr[arr > 5]` — a comparison produces a same-shape boolean array, and indexing with it returns matching elements, always flattened to 1D.
- Combine boolean conditions with `&`, `|`, `~` (not `and`/`or`/`not`) and wrap each condition in parentheses: `(arr > 2) & (arr < 9)`.
- Fancy indexing: `arr[[0, 2, 4]]` selects those exact positions, in the given order, repeats allowed.

## Gotchas (the part worth revising twice)
- **Slices return VIEWS** — they share memory with the original array. Mutating a slice mutates the source array too.
- **Boolean and fancy indexing return COPIES** — independent memory, mutating the result never touches the original.
- Verify with `np.shares_memory(a, b)` when unsure whether you're holding a view or a copy.
- Call `.copy()` on a slice whenever you need an independent array you can safely mutate.

## When it matters
This is the #1 source of "I changed one array and a totally different variable changed too" bugs. Any pipeline that slices data and then mutates it (in-place normalization, filtering before an update) needs to know whether it's holding a view or a copy.

## One-line recap example
```python
import numpy as np
a = np.array([1, 2, 3, 4, 5])
view = a[1:3]; view[0] = 99      # a becomes [1, 99, 3, 4, 5] - shared memory
copy = a[[1, 2]]; copy[0] = -1   # a is untouched - fancy indexing copies
```
