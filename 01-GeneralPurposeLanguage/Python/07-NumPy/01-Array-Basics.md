# NumPy Array Basics — Notes

## What this covers
How to create NumPy arrays (`array`, `arange`, `linspace`, `zeros`, `ones`, `eye`, `full`, `empty`), how `dtype` works, the core shape attributes, and why arrays beat Python lists for numeric work.

## Key points
- `np.array(list)` converts a Python list/tuple into an ndarray; `np.arange(start, stop, step)` is `range()` with array output and float-step support.
- `np.linspace(start, stop, num)` gives `num` evenly spaced points and **includes both endpoints** — different from `arange`, where `stop` is exclusive.
- `np.zeros`, `np.ones`, `np.full` pre-fill; `np.eye(n)` makes an identity matrix; `np.empty` allocates fast but leaves garbage values until you write to it.
- Every array has ONE shared `dtype`. Mixing `int` and `float` literals upcasts the whole array to float. Use `.astype(dtype)` to convert (returns a new array, doesn't mutate).
- `.shape` (dims tuple), `.ndim` (number of axes), `.size` (total elements), `.itemsize` (bytes/element), `.nbytes` (`size * itemsize`).
- 1D = flat vector, 2D = matrix/table, 3D = stack of matrices (e.g. RGB image or batch of matrices).
- Arrays beat lists because they store one fixed dtype in one contiguous memory block, so operations run as vectorized C loops instead of per-element Python bytecode.

## Gotchas (the part worth revising twice)
- `astype(int)` **truncates** toward zero, it does not round — `2.9` becomes `2`.
- Small unsigned dtypes overflow silently with no error: `uint8(250) + uint8(10)` wraps around instead of raising.
- `np.empty` is uninitialized memory, not zeros — never read from it before writing every cell.
- `sys.getsizeof()` on a Python list only counts the pointer array, not the actual int objects it points to — the true memory gap vs. a NumPy array is bigger than that number alone suggests.

## When it matters
Any numeric workload — data analysis, ML preprocessing, image arrays, scientific computing — starts with picking the right array shape and dtype; getting dtype wrong silently corrupts results (overflow) or wastes memory.

## One-line recap example
```python
import numpy as np
arr = np.linspace(0, 1, 5)   # [0. 0.25 0.5 0.75 1.] - endpoints included
print(arr.dtype, arr.shape)  # float64 (5,)
```
