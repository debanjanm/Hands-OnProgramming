# 01. Elementwise Multiply vs Matrix Multiply
# 02. .T Transpose Recap
# 03. np.linalg.inv - Matrix Inverse
# 04. np.linalg.det - Determinant
# 05. np.linalg.eig - Eigenvalues / Eigenvectors
# 06. np.linalg.solve - Solving Ax = b Directly
# 07. np.linalg.norm - Vector / Matrix Norms

import numpy as np

# 01. Elementwise Multiply vs Matrix Multiply
# ------------------------------------
# - `*` on two arrays is ELEMENTWISE - each position multiplied independently.
# - `@` (or np.matmul, or np.dot for 2D) is TRUE matrix multiplication -
#   row-by-column dot products. This is the #1 beginner confusion in NumPy:
#   `*` on two (2,2) arrays does NOT give you linear-algebra matrix product.

print("# 01. Elementwise Multiply vs Matrix Multiply")
print("# ------------------------------------")

A = np.array([[1, 2],
              [3, 4]])
B = np.array([[5, 6],
              [7, 8]])

print("A =\n", A)
print("B =\n", B)

print("\nA * B (elementwise, same shape required):\n", A * B)
print("# Each cell = A[i,j] * B[i,j]. NOT a matrix product.")

print("\nA @ B (matrix multiplication):\n", A @ B)
print("np.matmul(A, B):\n", np.matmul(A, B))
print("np.dot(A, B) (same result for 2D arrays):\n", np.dot(A, B))
print("# @ / matmul / dot agree for plain 2D arrays. Prefer '@' for readability;")
print("# np.dot has slightly different broadcasting rules for >2D - use matmul/@ there.")

# Manual check of one cell to make the row-by-column rule concrete.
manual_00 = A[0, 0] * B[0, 0] + A[0, 1] * B[1, 0]
print("\nManual (A@B)[0,0] = A[0,0]*B[0,0] + A[0,1]*B[1,0] =", manual_00,
      "-> matches (A @ B)[0,0] =", (A @ B)[0, 0])

# 02. .T Transpose Recap
# ------------------------------------
# - .T flips rows/columns. For a 2D array, (i, j) becomes (j, i).
# - .T returns a VIEW (no data copied) - cheap, but mutating it mutates the original.

print("\n# 02. .T Transpose Recap")
print("# ------------------------------------")

M = np.array([[1, 2, 3],
              [4, 5, 6]])
print("M (shape", M.shape, ") =\n", M)
print("M.T (shape", M.T.shape, ") =\n", M.T)
print("M.T.base is M:", M.T.base is M, "(transpose is a view, not a copy)")

# 03. np.linalg.inv - Matrix Inverse
# ------------------------------------
# - The inverse A_inv satisfies A @ A_inv = I (identity matrix).
# - Only defined for SQUARE, non-singular (det != 0) matrices.
# - Computationally expensive and numerically unstable for large/ill-conditioned
#   matrices - avoid it as a stepping stone to solving Ax=b (see section 06).

print("\n# 03. np.linalg.inv - Matrix Inverse")
print("# ------------------------------------")

C = np.array([[4.0, 7.0],
              [2.0, 6.0]])
C_inv = np.linalg.inv(C)
print("C =\n", C)
print("C_inv =\n", C_inv)
print("C @ C_inv (should be ~identity):\n", np.round(C @ C_inv, 10))

singular = np.array([[1.0, 2.0], [2.0, 4.0]])  # second row is a multiple of first
try:
    np.linalg.inv(singular)
except np.linalg.LinAlgError as e:
    print("\nSingular matrix (rows linearly dependent) -> inv() raises:", e)

# 04. np.linalg.det - Determinant
# ------------------------------------
# - A scalar summarizing a square matrix: det == 0 means the matrix is singular
#   (no inverse exists, rows/columns are linearly dependent).
# - Geometrically, |det| is the scale factor a matrix applies to area/volume.

print("\n# 04. np.linalg.det - Determinant")
print("# ------------------------------------")

print("det(C) =", np.linalg.det(C), "(nonzero -> invertible, matches inv() success above)")
print("det(singular) =", np.linalg.det(singular), "(~0 -> confirms inv() failure above)")

# 05. np.linalg.eig - Eigenvalues / Eigenvectors
# ------------------------------------
# - For square matrix A, eigenvector v and eigenvalue lambda satisfy: A @ v = lambda * v
#   ("v only gets scaled, not rotated, by A").
# - Returns (eigenvalues array, eigenvectors as COLUMNS of a matrix).
# - Used in PCA, stability analysis, vibration modes, Google's PageRank, etc.

print("\n# 05. np.linalg.eig - Eigenvalues / Eigenvectors")
print("# ------------------------------------")

D = np.array([[2.0, 0.0],
              [0.0, 3.0]])
eigenvalues, eigenvectors = np.linalg.eig(D)
print("D =\n", D)
print("eigenvalues =", eigenvalues)
print("eigenvectors (as columns) =\n", eigenvectors)

# Verify: A @ v == lambda * v for the first eigenpair.
v0 = eigenvectors[:, 0]
lam0 = eigenvalues[0]
print("Check A @ v0 =", D @ v0, " vs lambda0 * v0 =", lam0 * v0, "(equal, within float error)")

# 06. np.linalg.solve - Solving Ax = b Directly
# ------------------------------------
# - To solve Ax = b for x, DON'T do x = inv(A) @ b. Use np.linalg.solve(A, b).
# - Why: computing an explicit inverse is slower (more FLOPs) AND less numerically
#   stable - it amplifies floating-point rounding error, especially for
#   ill-conditioned matrices. solve() uses LU decomposition internally and only
#   computes what's needed for THIS particular b, no wasted/error-prone work.

print("\n# 06. np.linalg.solve - Solving Ax = b Directly")
print("# ------------------------------------")

# System: 3x + y = 9, x + 2y = 8
A_sys = np.array([[3.0, 1.0],
                   [1.0, 2.0]])
b_sys = np.array([9.0, 8.0])

x_solve = np.linalg.solve(A_sys, b_sys)
x_inv = np.linalg.inv(A_sys) @ b_sys  # works, but discouraged
print("A_sys =\n", A_sys, "\nb_sys =", b_sys)
print("solve(A_sys, b_sys)      =", x_solve, "(preferred: faster + more stable)")
print("inv(A_sys) @ b_sys       =", x_inv, "(same answer here, but don't do this - see note above)")
print("Verify A_sys @ x_solve == b_sys:", np.allclose(A_sys @ x_solve, b_sys))

# 07. np.linalg.norm - Vector / Matrix Norms
# ------------------------------------
# - norm() measures "size"/"length" of a vector or matrix.
# - Default (ord=None) on a vector = Euclidean (L2) length: sqrt(sum(x**2)).
# - ord=1 -> sum of absolute values (L1, "taxicab" distance).
# - ord=np.inf -> max absolute value.
# - Works on matrices too (default is Frobenius norm - sqrt of sum of squares of all elements).

print("\n# 07. np.linalg.norm - Vector / Matrix Norms")
print("# ------------------------------------")

vec = np.array([3.0, 4.0])
print("vec =", vec)
print("norm(vec) (L2, Euclidean length) =", np.linalg.norm(vec), "(3-4-5 triangle -> 5.0)")
print("norm(vec, ord=1) (L1, sum of abs) =", np.linalg.norm(vec, ord=1))
print("norm(vec, ord=np.inf) (max abs)   =", np.linalg.norm(vec, ord=np.inf))

print("\nnorm(C) (matrix, default = Frobenius) =", np.linalg.norm(C))
print("# Common use: normalizing a vector to unit length -> vec / norm(vec)")
unit_vec = vec / np.linalg.norm(vec)
print("unit_vec =", unit_vec, ", norm(unit_vec) =", np.linalg.norm(unit_vec), "(1.0, as expected)")

print("\n# End of Linear Algebra Explanation")
