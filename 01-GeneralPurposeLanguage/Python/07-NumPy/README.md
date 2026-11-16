# 07 - NumPy

| File | Covers |
|---|---|
| [01-Array-Basics.py](01-Array-Basics.py) · [notes](01-Array-Basics.md) | `ndarray` creation, `dtype`, shape/ndim/size, array vs list performance |
| [02-Indexing-And-Slicing.py](02-Indexing-And-Slicing.py) · [notes](02-Indexing-And-Slicing.md) | Basic/boolean/fancy indexing, views vs copies |
| [03-Reshaping-And-Manipulation.py](03-Reshaping-And-Manipulation.py) · [notes](03-Reshaping-And-Manipulation.md) | `reshape`, `ravel`/`flatten`, `transpose`, `concatenate`/`stack`/`split` |
| [04-Operations-And-Broadcasting.py](04-Operations-And-Broadcasting.py) · [notes](04-Operations-And-Broadcasting.md) | Elementwise ops, ufuncs, broadcasting rules |
| [05-Statistical-And-Math-Functions.py](05-Statistical-And-Math-Functions.py) · [notes](05-Statistical-And-Math-Functions.md) | `sum`/`mean`/`std` with `axis`, `cumsum`, sorting, `argmax`, `np.where` |
| [06-Linear-Algebra.py](06-Linear-Algebra.py) · [notes](06-Linear-Algebra.md) | `dot`/`matmul`/`@`, `np.linalg` (inv, det, eig, solve), norm |
| [07-Random-Module.py](07-Random-Module.py) · [notes](07-Random-Module.md) | `np.random.default_rng` Generator API vs legacy `np.random` |
| [08-Performance-And-Vectorization.py](08-Performance-And-Vectorization.py) · [notes](08-Performance-And-Vectorization.md) | Vectorized vs loop timing, C/F memory order, strides |
| [09-File-IO.py](09-File-IO.py) · [notes](09-File-IO.md) | `.npy`/`.npz` save/load, `savetxt`/`loadtxt`, `memmap` |
| [10-Advanced-NumPy.py](10-Advanced-NumPy.py) · [notes](10-Advanced-NumPy.md) | Structured arrays, masked arrays, `meshgrid`, `polyfit`, `np.select` |
| [11-Strides-And-Memory-Layout.py](11-Strides-And-Memory-Layout.py) · [notes](11-Strides-And-Memory-Layout.md) | strides, C/F order, contiguity, views and `shares_memory`, `sliding_window_view`, dtype internals, overflow, float precision, `memmap` |
| [12-Advanced-Indexing-Ufuncs-And-Sorting.py](12-Advanced-Indexing-Ufuncs-And-Sorting.py) · [notes](12-Advanced-Indexing-Ufuncs-And-Sorting.md) | `take`/`put`, `ix_`, ufunc `reduce`/`accumulate`/`outer`/`at`, `einsum`, `searchsorted`, `unique`/`bincount`/`histogram`, set ops, partition, nan-aware functions, `diff`/`gradient`/`convolve` |
| [13-NumPy-Recipes-And-Real-Patterns.py](13-NumPy-Recipes-And-Real-Patterns.py) · [notes](13-NumPy-Recipes-And-Real-Patterns.md) | normalisation, one-hot, distance matrices, moving average, image-like arrays, Monte Carlo, `lstsq` regression, `datetime64`, loop vs vectorized cheat sheet |

Each `.py` file has a matching `.md` notes file — a plain-English cheat sheet
for revision.
