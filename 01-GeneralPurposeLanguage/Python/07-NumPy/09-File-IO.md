# File I/O (NumPy) — Notes

## What this covers
Saving and loading NumPy arrays: binary `.npy`/`.npz` formats, human-readable
text/CSV output, and memory-mapped arrays for datasets too large to fit in RAM.

## Key points
- `np.save("file.npy", arr)` / `np.load("file.npy")` — single array, binary,
  exact dtype/shape/values preserved, fast and compact.
- `np.savez("file.npz", name1=arr1, name2=arr2)` — bundles multiple named
  arrays into one file; load and access via `bundle["name1"]`.
  `np.savez_compressed()` does the same with zip compression (smaller file,
  slower to read/write — worth it for large, repetitive arrays).
- `np.savetxt("file.csv", arr, delimiter=",", header="...")` /
  `np.loadtxt("file.csv", delimiter=",", skiprows=1)` — human-readable
  text, editable/viewable outside NumPy, but loses exact dtype (everything
  reloads as `float64`).
- `np.memmap("file.dat", dtype=..., mode=..., shape=...)` — array backed by
  a file on disk; NumPy reads/writes only the slices you touch instead of
  loading everything into RAM. Lets you work with arrays bigger than
  available memory, at the cost of disk-speed access instead of RAM-speed.

## Gotchas (the part worth revising twice)
- `savetxt`/`loadtxt` round-trips lose integer dtype — an int column comes
  back as `float64`. Use `.npy`/`.npz` when exact types matter.
- `savez_compressed` can produce a *larger* file than plain `savez` on tiny
  arrays — compression overhead only pays off at scale.
- `np.memmap` requires you to specify `dtype` and `shape` explicitly when
  reopening — the raw `.dat` file has no header describing its own contents.
  Get either wrong and you'll silently read garbage.
- Always `del` (or let go out of scope) a memmap, or call `.flush()`, before
  assuming writes have hit disk.

## When it matters
`.npy`/`.npz` for fast intermediate results between pipeline stages;
`savetxt`/CSV for sharing data with non-NumPy tools or humans; `memmap` for
out-of-core processing of datasets larger than RAM (common in scientific
computing and large-scale data analysis).

## One-line recap example
```python
import numpy as np
np.save("weights.npy", np.array([0.1, 0.2, 0.3]))
loaded = np.load("weights.npy")   # exact dtype/values preserved
```
