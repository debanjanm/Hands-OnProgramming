# 01. Elementwise Arithmetic
# 02. Comparison Operators -> Boolean Arrays
# 03. Universal Functions (ufuncs)
# 04. Broadcasting Rules

import numpy as np

# 01. Elementwise Arithmetic
# ------------------------------------
# - +, -, *, / on two arrays operate ELEMENT BY ELEMENT - very different
#   from Python lists, where + concatenates and * repeats.
# - This works because both operands have the same shape (or broadcast to
#   a common shape - see section 04).

print("# 01. Elementwise Arithmetic")
print("# ------------------------------------")

a = np.array([1, 2, 3, 4])
b = np.array([10, 20, 30, 40])

print("a =", a, ", b =", b)
print("a + b =", a + b, "(elementwise addition)")
print("a - b =", a - b)
print("a * b =", a * b, "(elementwise multiply, NOT dot product)")
print("a / b =", a / b)
print("a ** 2 =", a ** 2)

python_list_a = [1, 2, 3, 4]
print("\nCompare to Python lists:")
print("[1,2,3,4] + [1,2,3,4] =", python_list_a + python_list_a, "(concatenation, not addition!)")
print("[1,2,3,4] * 2         =", python_list_a * 2, "(repetition, not multiplication!)")

# 02. Comparison Operators -> Boolean Arrays
# ------------------------------------
# - ==, !=, <, >, <=, >= applied to arrays return a boolean array of
#   elementwise results, not a single True/False.

print("\n# 02. Comparison Operators -> Boolean Arrays")
print("# ------------------------------------")

print("a =", a)
print("a > 2   =", a > 2)
print("a == 3  =", a == 3)
print("a != 3  =", a != 3)
print("# Gotcha: 'if a > 2:' raises ValueError (ambiguous truth value) unless a has exactly 1 element.")
print("#   Use .any() or .all() to collapse a boolean array to a single bool.")
print("(a > 2).any() =", (a > 2).any(), ", (a > 2).all() =", (a > 2).all())

# 03. Universal Functions (ufuncs)
# ------------------------------------
# - ufuncs are vectorized functions that apply to every element without an
#   explicit Python loop - compiled C under the hood, same speed benefit
#   as elementwise operators.
# - Examples: np.sqrt, np.exp, np.log, np.sin, np.cos, np.abs, np.round.

print("\n# 03. Universal Functions (ufuncs)")
print("# ------------------------------------")

values = np.array([1, 4, 9, 16])
print("values =", values)
print("np.sqrt(values) =", np.sqrt(values))
print("np.exp([0, 1])  =", np.exp([0, 1]), "(e^0, e^1)")
print("np.log([1, np.e, np.e**2]) =", np.log([1, np.e, np.e**2]), "(natural log)")

angles = np.array([0, np.pi / 2, np.pi])
print("np.sin([0, pi/2, pi]) =", np.sin(angles))
print("np.round([1.234, 5.678], 1) =", np.round([1.234, 5.678], 1))
print("# ufuncs beat manual loops the same way elementwise operators do: no per-element")
print("#   Python bytecode dispatch, everything runs in a compiled C loop.")

# 04. Broadcasting Rules
# ------------------------------------
# - Broadcasting lets NumPy operate on arrays of DIFFERENT shapes without
#   copying data, by virtually "stretching" the smaller one.
# - THE RULE: compare shapes element-wise starting from the TRAILING
#   (rightmost) dimension. Two dimensions are compatible if:
#     (a) they are equal, OR
#     (b) one of them is 1 (that axis gets stretched to match).
#   If neither holds for any dimension pair, broadcasting fails with a
#   ValueError. Missing leading dimensions are treated as size 1.

print("\n# 04. Broadcasting Rules")
print("# ------------------------------------")
print("# Rule: align shapes from the right; each dim pair must be equal OR one of them is 1.")

# Example 1: scalar + array - the scalar broadcasts to every element.
arr = np.array([1, 2, 3])
print("\nExample 1 - scalar + array:")
print("arr =", arr, "shape", arr.shape)
print("arr + 10 =", arr + 10, "(scalar treated as shape () -> stretched to match (3,))")

# Example 2: 1D + 2D - the 1D array broadcasts across every row.
matrix = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
row = np.array([10, 20, 30])
print("\nExample 2 - 1D + 2D:")
print("matrix shape", matrix.shape, ":\n", matrix)
print("row shape", row.shape, ":", row)
print("matrix + row (row shape (3,) matches trailing dim of matrix (3,3), broadcasts down each row):")
print(matrix + row)

# Example 3: column vector + row vector - both stretch to a common shape.
col = np.array([[1], [2], [3]])   # shape (3, 1)
row_vec = np.array([10, 20, 30])  # shape (3,) -> treated as (1, 3)
print("\nExample 3 - column (3,1) + row (3,) [treated as (1,3)]:")
print("col shape", col.shape, "-> broadcasts across columns")
print("row_vec shape", row_vec.shape, "-> broadcasts across rows")
print("col + row_vec (produces a (3,3) outer-sum result):\n", col + row_vec)

# Example 4: mismatched shapes that CANNOT broadcast.
print("\nExample 4 - incompatible shapes:")
bad_a = np.ones((3, 4))
bad_b = np.ones((3, 3))
print("bad_a shape", bad_a.shape, ", bad_b shape", bad_b.shape)
print("Trailing dims: 4 vs 3 - neither equal nor 1 -> broadcasting fails.")
try:
    bad_a + bad_b
except ValueError as e:
    print("bad_a + bad_b raises ValueError:", e)

print("\n# End of Operations and Broadcasting")
