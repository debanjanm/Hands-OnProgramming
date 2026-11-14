# Linear Algebra (NumPy) — Notes

## What this covers
The `numpy.linalg` toolbox: matrix multiplication vs elementwise multiply, transpose,
inverse, determinant, eigenvalues/eigenvectors, solving linear systems, and norms.

## Key points
- `*` between two arrays is **elementwise** (position-by-position). `@` / `np.matmul` /
  `np.dot` (for 2D) is **true matrix multiplication** (row · column dot products).
  These give different results on the same shapes — don't mix them up.
- `.T` transposes an array and returns a **view** (no copy) — mutating `.T` mutates the original.
- `np.linalg.inv(A)` gives the matrix inverse; only works for square, non-singular matrices
  (raises `LinAlgError: Singular matrix` otherwise).
- `np.linalg.det(A)` — a scalar; `det == 0` means the matrix is singular (no inverse exists).
- `np.linalg.eig(A)` returns `(eigenvalues, eigenvectors)` where eigenvectors are the
  **columns** of the returned matrix, satisfying `A @ v = lambda * v`.
- `np.linalg.solve(A, b)` solves `Ax = b` directly — the preferred way, over
  `inv(A) @ b`, to find `x`.
- `np.linalg.norm(v)` measures vector "length" — default is Euclidean (L2); `ord=1` is
  sum of absolute values; `ord=np.inf` is the max absolute value. Works on matrices too
  (default = Frobenius norm).

## Gotchas (the part worth revising twice)
- `A * B` vs `A @ B` on two square matrices of the same shape are BOTH valid and BOTH
  run without error — but they compute different things. This is the classic silent bug.
- `np.linalg.inv` is slower and numerically less stable than `np.linalg.solve` for
  solving `Ax = b` — inverting amplifies floating-point rounding error, especially for
  ill-conditioned matrices. Always prefer `solve()` when the goal is solving a system,
  not the inverse itself.
- A matrix with `det ≈ 0` isn't necessarily exactly zero due to floating-point error —
  check with `np.isclose(det, 0)` rather than `det == 0`.

## When it matters
Linear algebra underlies machine learning (weight matrices, gradients), computer
graphics (transformations), physics simulations, and statistics (PCA uses
eigenvectors). Any time you see "solve a system of equations" or "transform a set of
points," this is the toolbox.

## One-line recap example
```python
import numpy as np
A = np.array([[3.0, 1.0], [1.0, 2.0]])
b = np.array([9.0, 8.0])
x = np.linalg.solve(A, b)   # preferred over np.linalg.inv(A) @ b
```
