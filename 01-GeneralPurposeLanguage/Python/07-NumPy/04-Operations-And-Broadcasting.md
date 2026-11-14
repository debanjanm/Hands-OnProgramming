# NumPy Operations and Broadcasting — Notes

## What this covers
How arithmetic, comparisons, and universal functions (ufuncs) work elementwise on arrays, and the broadcasting rule that lets NumPy combine arrays of different shapes.

## Key points
- `+ - * /` on arrays are **elementwise** — unlike Python lists, where `+` concatenates and `*` repeats.
- Comparison operators (`== != < > <= >=`) return a boolean array of elementwise results, not a single bool.
- Use `.any()` / `.all()` to collapse a boolean array to one value — `if arr > 2:` raises `ValueError` for multi-element arrays (ambiguous truth value).
- ufuncs (`np.sqrt`, `np.exp`, `np.log`, `np.sin`, `np.round`, etc.) are vectorized C functions — no explicit Python loop needed, same speed benefit as elementwise operators.
- **Broadcasting rule**: compare shapes from the trailing (rightmost) dimension. Two dimensions are compatible if they're equal or one of them is 1; that axis then stretches to match. Missing leading dimensions count as size 1.

## Gotchas (the part worth revising twice)
- `a * b` between two arrays is elementwise multiplication, not a dot product / matrix multiply (that's `@` or `np.dot`).
- A boolean array in an `if` statement fails unless it has exactly one element — always reduce with `.any()`/`.all()` first.
- Broadcasting failures raise `ValueError: operands could not be broadcast together with shapes ...` — read the shapes in the error and check the trailing dimensions against the rule.
- A `(3,)` array combined with a `(3,1)` array broadcasts to `(3,3)` (an outer-sum-like result) — easy to get by accident when you meant elementwise addition of two same-shaped vectors.

## When it matters
Broadcasting is what makes NumPy code short and fast — normalizing every row of a matrix by a per-row mean, adding a bias vector to every sample in a batch — all without writing a loop. Misreading the rule is one of the most common NumPy bugs.

## One-line recap example
```python
import numpy as np
matrix = np.ones((3, 4))
row = np.array([1, 2, 3, 4])     # shape (4,) broadcasts against (3,4)
print(matrix + row)              # row added to every row of matrix
```
