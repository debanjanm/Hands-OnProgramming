# 01. Basic Indexing
# 02. Slicing
# 03. Boolean / Mask Indexing
# 04. Fancy Indexing
# 05. Views vs Copies - The Critical Gotcha

import numpy as np

# 01. Basic Indexing
# ------------------------------------
# - 1D indexing works like Python lists: arr[0], arr[-1].
# - 2D+ indexing uses a single comma-separated tuple: arr[row, col] instead
#   of the nested arr[row][col] (both work, but arr[row, col] avoids
#   building an intermediate array and is the idiomatic NumPy form).

print("# 01. Basic Indexing")
print("# ------------------------------------")

arr_1d = np.array([10, 20, 30, 40, 50])
print("arr_1d =", arr_1d)
print("arr_1d[0]  =", arr_1d[0], "(first element)")
print("arr_1d[-1] =", arr_1d[-1], "(last element)")

matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
print("\nmatrix:\n", matrix)
print("matrix[1, 2]    =", matrix[1, 2], "(row 1, col 2 - preferred form)")
print("matrix[1][2]    =", matrix[1][2], "(same result, but builds a temp row array first)")
print("matrix[-1, -1]  =", matrix[-1, -1], "(last row, last col)")

# 02. Slicing
# ------------------------------------
# - arr[start:stop:step] works like list slicing, but extends to any axis.
# - arr[:, 0] means "all rows, column 0" - the colon alone means "everything
#   along this axis".
# - Negative step reverses direction, same as Python lists.

print("\n# 02. Slicing")
print("# ------------------------------------")

print("arr_1d[1:3]     =", arr_1d[1:3], "(indices 1,2 - stop exclusive)")
print("arr_1d[::2]     =", arr_1d[::2], "(every other element)")
print("arr_1d[::-1]    =", arr_1d[::-1], "(reversed)")

print("\nmatrix[:, 0]    =", matrix[:, 0], "(all rows, column 0)")
print("matrix[0, :]    =", matrix[0, :], "(row 0, all columns)")
print("matrix[0:2, 1:3]:\n", matrix[0:2, 1:3], "(rows 0-1, cols 1-2)")
print("matrix[::-1]:\n", matrix[::-1], "(rows reversed, cols untouched)")

# 03. Boolean / Mask Indexing
# ------------------------------------
# - Comparing an array to a value produces a boolean array of the same
#   shape (the "mask").
# - Indexing with that mask selects only the True positions, always
#   flattened into a 1D result regardless of the original shape.

print("\n# 03. Boolean / Mask Indexing")
print("# ------------------------------------")

data = np.array([3, 8, 1, 9, 4, 7])
mask = data > 5
print("data       =", data)
print("mask (data > 5) =", mask)
print("data[mask]      =", data[mask], "(only elements where mask is True)")
print("data[data > 5]  =", data[data > 5], "(same thing, written inline)")

matrix_mask = matrix[matrix % 2 == 0]
print("matrix[matrix % 2 == 0] =", matrix_mask, "(even elements, always returned FLATTENED)")

# Combining conditions needs & / | (not `and`/`or`) plus parentheses -
# Python's and/or don't work elementwise on arrays.
combo_mask = data[(data > 2) & (data < 9)]
print("data[(data > 2) & (data < 9)] =", combo_mask, "(use & | ~, not and/or/not)")

# 04. Fancy Indexing
# ------------------------------------
# - Indexing with a LIST or ARRAY of integer indices picks out those
#   positions explicitly, in the order given (can repeat indices too).

print("\n# 04. Fancy Indexing")
print("# ------------------------------------")

print("data            =", data)
print("data[[0, 2, 4]] =", data[[0, 2, 4]], "(elements at positions 0, 2, 4)")
print("data[[4, 4, 0]] =", data[[4, 4, 0]], "(repeats allowed, order follows the index list)")
print("matrix[[0, 2]]:\n", matrix[[0, 2]], "(rows 0 and 2)")

# 05. Views vs Copies - The Critical Gotcha
# ------------------------------------
# - Basic slicing (arr[1:3], arr[:, 0], etc.) returns a VIEW: a new ndarray
#   object that shares the SAME underlying memory buffer as the original.
#   Mutating the view mutates the original, and vice versa.
# - Boolean indexing and fancy indexing always return a COPY: an
#   independent memory buffer. Mutating the result leaves the original
#   untouched.
# - Use .copy() whenever you need an independent slice.

print("\n# 05. Views vs Copies - The Critical Gotcha")
print("# ------------------------------------")

original = np.array([1, 2, 3, 4, 5])
view = original[1:4]          # slice -> VIEW
print("original        =", original)
print("view = original[1:4] =", view)

view[0] = 999
print("After view[0] = 999:")
print("  view     =", view)
print("  original =", original, "(CHANGED! view shares memory with original)")

original2 = np.array([1, 2, 3, 4, 5])
fancy_copy = original2[[1, 2, 3]]   # fancy indexing -> COPY
fancy_copy[0] = 999
print("\noriginal2 =", original2)
print("fancy_copy = original2[[1,2,3]]; fancy_copy[0] = 999")
print("  fancy_copy =", fancy_copy)
print("  original2  =", original2, "(UNCHANGED - fancy indexing made a copy)")

bool_copy = original2[original2 > 2]
bool_copy[0] = -1
print("\nbool_copy = original2[original2 > 2]; bool_copy[0] = -1")
print("  bool_copy =", bool_copy)
print("  original2 =", original2, "(also UNCHANGED - boolean indexing copies too)")

print("\n# np.shares_memory() confirms it directly:")
print("shares_memory(original, view)        =", np.shares_memory(original, view), "(slice = view)")
print("shares_memory(original2, fancy_copy)  =", np.shares_memory(original2, fancy_copy), "(fancy = copy)")

safe_slice = original[1:4].copy()   # force an independent copy
safe_slice[0] = -1
print("\nsafe_slice = original[1:4].copy(); safe_slice[0] = -1")
print("  safe_slice =", safe_slice)
print("  original   =", original, "(untouched - .copy() breaks the memory link)")

print("\n# End of Indexing and Slicing")
