# 01. sum / mean / std / var / min / max
# 02. The axis Parameter Explained
# 03. cumsum / cumprod
# 04. sort / argsort
# 05. argmax / argmin
# 06. np.where - Both Forms

import numpy as np

# 01. sum / mean / std / var / min / max
# ------------------------------------
# - Without axis=, these reduce the ENTIRE array to a single scalar.
# - std (standard deviation) and var (variance) measure spread around the mean.

print("# 01. sum / mean / std / var / min / max")
print("# ------------------------------------")

matrix = np.array([[1, 2, 3], [4, 5, 6]])
print("matrix:\n", matrix)
print("matrix.sum()  =", matrix.sum(), "(all 6 elements added)")
print("matrix.mean() =", matrix.mean())
print("matrix.std()  =", matrix.std(), "(spread around the mean)")
print("matrix.var()  =", matrix.var(), "(std squared)")
print("matrix.min()  =", matrix.min(), ", matrix.max() =", matrix.max())

# 02. The axis Parameter Explained
# ------------------------------------
# - axis=0 collapses DOWN the rows -> one result PER COLUMN.
# - axis=1 collapses ACROSS the columns -> one result PER ROW.
# - Mental model: "axis=N" means "this axis disappears from the output shape".
#   matrix.shape is (2, 3). sum(axis=0) removes axis 0 -> result shape (3,).
#   sum(axis=1) removes axis 1 -> result shape (2,).

print("\n# 02. The axis Parameter Explained")
print("# ------------------------------------")
print("matrix (shape", matrix.shape, "):\n", matrix)
print("# axis=0 -> collapses ROWS, one value per COLUMN (result shape (3,))")
print("matrix.sum(axis=0) =", matrix.sum(axis=0), "(col0: 1+4=5, col1: 2+5=7, col2: 3+6=9)")
print("# axis=1 -> collapses COLUMNS, one value per ROW (result shape (2,))")
print("matrix.sum(axis=1) =", matrix.sum(axis=1), "(row0: 1+2+3=6, row1: 4+5+6=15)")
print("matrix.mean(axis=0) =", matrix.mean(axis=0), "(per-column mean)")
print("matrix.mean(axis=1) =", matrix.mean(axis=1), "(per-row mean)")

# 03. cumsum / cumprod
# ------------------------------------
# - Cumulative sum/product: each output element is the running total up to
#   and including that position. Output has the SAME size as the input
#   (flattened, unless axis= is given).

print("\n# 03. cumsum / cumprod")
print("# ------------------------------------")

seq = np.array([1, 2, 3, 4])
print("seq =", seq)
print("np.cumsum(seq)  =", np.cumsum(seq), "(1, 1+2, 1+2+3, 1+2+3+4)")
print("np.cumprod(seq) =", np.cumprod(seq), "(1, 1*2, 1*2*3, 1*2*3*4)")
print("matrix.cumsum(axis=1):\n", matrix.cumsum(axis=1), "(running total along each row)")

# 04. sort / argsort
# ------------------------------------
# - np.sort(arr) returns a NEW sorted array (original untouched);
#   arr.sort() sorts IN PLACE and returns None.
# - np.argsort(arr) returns the INDICES that would sort the array - useful
#   when you need to sort one array based on the order of another.

print("\n# 04. sort / argsort")
print("# ------------------------------------")

unsorted = np.array([3, 1, 4, 1, 5, 9, 2])
print("unsorted =", unsorted)
print("np.sort(unsorted)     =", np.sort(unsorted), "(new array, original untouched)")
print("unsorted after sort() call =", unsorted, "(unchanged)")

sort_indices = np.argsort(unsorted)
print("np.argsort(unsorted)  =", sort_indices, "(indices that WOULD sort it)")
print("unsorted[sort_indices] =", unsorted[sort_indices], "(applying those indices sorts it)")

names = np.array(["c", "a", "d", "b"])
scores = np.array([70, 90, 60, 85])
order = np.argsort(scores)[::-1]  # descending by score
print("\nnames  =", names, ", scores =", scores)
print("Sort names by descending score using argsort(scores)[::-1] ->", names[order])

# 05. argmax / argmin
# ------------------------------------
# - Return the INDEX of the max/min value, not the value itself.
# - With axis=, return one index per row/column, following the same
#   collapse rule as sum/mean.

print("\n# 05. argmax / argmin")
print("# ------------------------------------")

print("unsorted =", unsorted)
print("np.argmax(unsorted) =", np.argmax(unsorted), "-> value", unsorted[np.argmax(unsorted)])
print("np.argmin(unsorted) =", np.argmin(unsorted), "-> value", unsorted[np.argmin(unsorted)])
print("matrix:\n", matrix)
print("matrix.argmax(axis=0) =", matrix.argmax(axis=0), "(row-index of max in each column)")
print("matrix.argmax(axis=1) =", matrix.argmax(axis=1), "(col-index of max in each row)")

# 06. np.where - Both Forms
# ------------------------------------
# - 1-arg form: np.where(condition) returns a TUPLE of index arrays where
#   condition is True (like np.nonzero) - NOT the values themselves.
# - 3-arg form: np.where(condition, if_true, if_false) returns an array
#   built elementwise: if_true's value where condition holds, if_false's
#   value elsewhere - this is the "vectorized ternary" form.
# - These two forms are commonly confused because they share a name but
#   return completely different things.

print("\n# 06. np.where - Both Forms")
print("# ------------------------------------")

data = np.array([3, 8, 1, 9, 4, 7])
print("data =", data)

indices = np.where(data > 5)
print("np.where(data > 5)             =", indices, "(1-arg form: TUPLE of index arrays, not values)")
print("data[np.where(data > 5)]       =", data[indices], "(use the indices to fetch actual values)")

selected = np.where(data > 5, data, 0)
print("np.where(data > 5, data, 0)    =", selected, "(3-arg form: keep value if True, else 0)")

labels = np.where(data > 5, "high", "low")
print("np.where(data > 5, 'high', 'low') =", labels, "(vectorized ternary, any dtype)")

print("\n# End of Statistical and Math Functions")
