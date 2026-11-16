# Strides and Memory Layout — Notes

## What this covers
How an ndarray is really stored (one flat byte buffer plus a header), what strides and contiguity mean, when you get a view versus a copy, how dtypes work at byte level (casting, overflow, float precision, nan/inf), and tools for raw memory: `as_strided`, `sliding_window_view`, `np.frombuffer`, `np.memmap`, `np.nditer`.

## Key points
- An array = data buffer + header (`dtype`, `shape`, `strides`, `flags`). Transpose, slice and reshape usually change only the header.
- `strides` are **bytes** to step along each axis. C order `(3,4)` int32 -> `(16, 4)`; `.T` just swaps them.
- C order (row-major) vs Fortran order (column-major) change memory layout, not the values you see. `order='F'` in `reshape`/`ravel` changes the reading order.
- `flags.c_contiguous` / `f_contiguous` / `owndata` / `writeable` describe the layout; `np.ascontiguousarray` makes a C-contiguous copy when needed.
- Views: basic slicing, `.T`, `.view()`, often `reshape`/`ravel`. Copies: fancy indexing, boolean masks, `.copy()`, `.flatten()`, `astype`.
- Check sharing with `.base`, `np.shares_memory` (exact) and `np.may_share_memory` (fast, bounds only).
- `sliding_window_view` gives safe read-only rolling windows; `as_strided` is the unsafe low-level version. Broadcasting is a stride-0 view.
- dtype: `kind`, `itemsize`, `byteorder`; `np.iinfo` / `np.finfo` give limits.
- `astype` converts values (copy); `view(dtype)` reinterprets the same bytes.
- `np.result_type`, `np.can_cast`, and `casting=` control and explain type promotion.
- Fixed-size integers wrap around silently; floats have limited precision (`eps`) and special values `nan`/`inf`.
- `np.errstate` controls float warnings (`ignore`, `warn`, `raise`).
- Memory cost = elements x itemsize; use smaller dtypes and in-place ops (`out=`, `+=`).
- `np.frombuffer` wraps bytes without copying; `np.memmap` maps a file as an array; `np.nditer` is the low-level iterator.

## Gotchas (the part worth revising twice)
- `b = a[idx_array]; b[0] = 1` does NOT change `a` (copy), but `a[idx_array] = 1` does. `a[[0,1]][0] = 5` writes to a throwaway copy.
- `reshape` / `ravel` return a view only when strides allow; otherwise they silently copy. Never depend on it for writing.
- `.view(np.int32)` on floats exposes raw bits; it does not convert. Use `astype` for values.
- `uint8` / `int8` arithmetic wraps with no error (`250 + 10 -> 4`). `sum(dtype=np.uint8)` wraps too. Widen first, then `np.clip`.
- Default integer size is platform-dependent; name the dtype when size matters.
- Python-scalar casting changed in NumPy 2.0 (NEP 50): on 1.26 `int8_array + 1000` upcasts to int16, on 2.x it overflows.
- `nan != nan`; comparisons with nan are `False`; `sum` with a nan gives nan (use `nansum`). Integer arrays cannot hold nan.
- Never compare floats with `==`; use `np.isclose` / `np.allclose`, and mind `atol` near zero.
- `as_strided` has no bounds checks: wrong arguments read garbage memory; windows overlap so writes hit several cells.
- `np.memmap` has no header: you must supply the correct dtype and shape. `np.zeros` of a huge shape may "work" lazily and crash later.

## When it matters
Image/audio pipelines (uint8 overflow), rolling-window features without Python loops, reading binary files bigger than RAM, debugging "why did my write not stick" bugs, and squeezing memory with float32/int8. Layout matters for speed on big arrays (iterate along the contiguous axis).

## One-line recap example
```python
import numpy as np
a = np.arange(6, dtype=np.int32).reshape(2, 3)
print(a.strides, a.T.strides, np.shares_memory(a, a.T))   # (12, 4) (4, 12) True
```
