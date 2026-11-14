# 01. reshape() and the -1 Auto-Dimension
# 02. ravel() vs flatten() - View vs Copy
# 03. transpose() / .T
# 04. concatenate / vstack / hstack
# 05. split / array_split
# 06. newaxis / expand_dims / squeeze

import numpy as np

# 01. reshape() and the -1 Auto-Dimension
# ------------------------------------
# - reshape() reinterprets the SAME data with a new shape - total element
#   count must stay the same (2x6 can become 3x4, 12x1, etc, but not 5x3).
# - Passing -1 for one dimension tells NumPy "figure this size out for me"
#   from the total element count and the other given dimensions.
# - reshape() returns a VIEW when possible (same memory), a copy only when
#   the requested shape can't be expressed as a view of the original layout.

print("# 01. reshape() and the -1 Auto-Dimension")
print("# ------------------------------------")

arr = np.arange(12)
print("arr = np.arange(12) =", arr)

reshaped = arr.reshape(3, 4)
print("arr.reshape(3, 4):\n", reshaped)

auto_dim = arr.reshape(4, -1)
print("arr.reshape(4, -1) (NumPy infers 3 columns):\n", auto_dim)

auto_dim2 = arr.reshape(-1, 6)
print("arr.reshape(-1, 6) (NumPy infers 2 rows):\n", auto_dim2)

try:
    arr.reshape(5, 3)
except ValueError as e:
    print("arr.reshape(5, 3) raises ValueError:", e)

reshaped[0, 0] = 999
print("reshaped[0,0] = 999 -> arr also changed:", arr[0], "(reshape is usually a VIEW)")

# 02. ravel() vs flatten() - View vs Copy
# ------------------------------------
# - Both collapse any array down to 1D.
# - ravel() returns a VIEW when possible (shares memory) - cheap.
# - flatten() ALWAYS returns a COPY - safe but costs memory for large arrays.

print("\n# 02. ravel() vs flatten() - View vs Copy")
print("# ------------------------------------")

matrix = np.array([[1, 2, 3], [4, 5, 6]])
raveled = matrix.ravel()
flattened = matrix.flatten()

print("matrix:\n", matrix)
print("matrix.ravel()   =", raveled)
print("matrix.flatten() =", flattened)

raveled[0] = -1
flattened[1] = -1
print("After raveled[0]=-1 and flattened[1]=-1:")
print("  raveled   =", raveled)
print("  flattened =", flattened)
print("  matrix:\n", matrix, "(only ravel's change shows - flatten was an independent copy)")
print("np.shares_memory(matrix, matrix.ravel())   =", np.shares_memory(matrix, matrix.ravel()))
print("np.shares_memory(matrix, matrix.flatten()) =", np.shares_memory(matrix, matrix.flatten()))

# 03. transpose() / .T
# ------------------------------------
# - Swaps axes - for a 2D matrix, rows become columns and vice versa.
# - .T is shorthand for .transpose() with no arguments (reverses all axes).
# - Like reshape, transpose returns a VIEW (same data, different strides).

print("\n# 03. transpose() / .T")
print("# ------------------------------------")

m = np.array([[1, 2, 3], [4, 5, 6]])
print("m (shape", m.shape, "):\n", m)
print("m.T (shape", m.T.shape, "):\n", m.T)
print("m.transpose() same as m.T:", np.array_equal(m.transpose(), m.T))

# 04. concatenate / vstack / hstack
# ------------------------------------
# - np.concatenate([a, b], axis=...) joins arrays along an existing axis -
#   the arrays must match on every OTHER axis.
# - np.vstack stacks arrays row-wise (like concatenate with axis=0).
# - np.hstack stacks arrays column-wise (like concatenate with axis=1 for 2D).

print("\n# 04. concatenate / vstack / hstack")
print("# ------------------------------------")

a = np.array([[1, 2], [3, 4]])
b = np.array([[5, 6], [7, 8]])

print("a:\n", a, "\nb:\n", b)
print("np.concatenate([a, b], axis=0) (stack rows):\n", np.concatenate([a, b], axis=0))
print("np.concatenate([a, b], axis=1) (stack cols):\n", np.concatenate([a, b], axis=1))
print("np.vstack([a, b]):\n", np.vstack([a, b]), "(equivalent to axis=0)")
print("np.hstack([a, b]):\n", np.hstack([a, b]), "(equivalent to axis=1)")

# 05. split / array_split
# ------------------------------------
# - np.split(arr, n) divides an array into n EQUAL parts - raises an error
#   if it doesn't divide evenly.
# - np.array_split(arr, n) also divides into n parts, but tolerates uneven
#   splits (some pieces get one extra element instead of erroring).

print("\n# 05. split / array_split")
print("# ------------------------------------")

to_split = np.arange(9)
print("to_split =", to_split)
print("np.split(to_split, 3) =", np.split(to_split, 3), "(9 elements / 3 = evenly divides)")

try:
    np.split(to_split, 4)
except ValueError as e:
    print("np.split(to_split, 4) raises ValueError:", e)

print("np.array_split(to_split, 4) =", np.array_split(to_split, 4), "(tolerates uneven split, no error)")

# 06. newaxis / expand_dims / squeeze
# ------------------------------------
# - np.newaxis (alias None) inserts a new length-1 axis at a given
#   position - commonly used to turn a 1D array into a row or column
#   vector for broadcasting.
# - np.expand_dims(arr, axis) does the same thing as a function call.
# - .squeeze() removes all length-1 axes, going back to the minimal shape.

print("\n# 06. newaxis / expand_dims / squeeze")
print("# ------------------------------------")

vec = np.array([1, 2, 3])
print("vec.shape =", vec.shape)

row_vec = vec[np.newaxis, :]
col_vec = vec[:, np.newaxis]
print("vec[np.newaxis, :].shape =", row_vec.shape, "-> row vector:", row_vec)
print("vec[:, np.newaxis].shape =", col_vec.shape, "-> column vector:\n", col_vec)

expanded = np.expand_dims(vec, axis=0)
print("np.expand_dims(vec, axis=0).shape =", expanded.shape, "(same as row_vec)")

squeezed = row_vec.squeeze()
print("row_vec.squeeze().shape =", squeezed.shape, "(back to 1D, all size-1 axes dropped)")

print("\n# End of Reshaping and Manipulation")
