# Performance and Vectorization (NumPy) — Notes

## What this covers
Why NumPy is fast: a timed loop-vs-vectorized comparison, the reason
vectorization wins, how arrays are laid out in memory (C-order vs F-order,
strides), and the cost difference between views and copies.

## Key points
- A Python `for` loop pays interpreter overhead and allocates a new Python
  object per element. A vectorized NumPy op runs a single call into a
  pre-compiled C loop over raw, contiguous memory — measured here at roughly
  10-15x faster for squaring a million numbers.
- Vectorization is fast because of: no per-element Python object overhead,
  C-level loops, and SIMD (CPU processes multiple elements per instruction).
- `order='C'` (default): row-major, elements of the same row are contiguous.
  `order='F'`: column-major, elements of the same column are contiguous.
  Check with `.flags['C_CONTIGUOUS']` / `.flags['F_CONTIGUOUS']`.
- `.strides` (bytes to step per axis to move one index) reveals the real
  physical memory layout behind the logical shape.
- Basic slicing (`arr[::2]`) returns a **view** — near-instant, shares memory.
  `.copy()`, fancy indexing, and boolean masks allocate **new** memory and
  copy every element — cost scales with array size.

## Gotchas (the part worth revising twice)
- Timing numbers are machine-dependent — the exact speedup varies, but
  vectorized code reliably beats a Python loop by an order of magnitude or more.
- Iterating along the non-contiguous axis of an array (e.g. columns of a
  C-order array) is slower due to poor CPU cache usage, even though it's
  logically valid.
- `view.base is None` is `False` for a view (points back to the original);
  a genuine copy has `.base is None`. Use this to check what you're holding.

## When it matters
Any time you're tempted to write a Python loop over a NumPy array — replace
it with a vectorized expression. This matters most in data processing, image
manipulation, and numerical simulation where arrays have thousands to
millions of elements.

## One-line recap example
```python
import numpy as np
arr = np.arange(1_000_000)
squared = arr ** 2   # vectorized: no Python-level loop needed
```
