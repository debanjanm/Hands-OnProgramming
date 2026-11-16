# 01. take and put
# 02. take_along_axis and put_along_axis
# 03. np.ix_ and ravel_multi_index
# 04. ufunc Methods: reduce, accumulate, outer
# 05. ufunc Methods: at and reduceat
# 06. frompyfunc and np.vectorize (and Why They Are Slow)
# 07. apply_along_axis and apply_over_axes
# 08. einsum Step by Step
# 09. searchsorted
# 10. digitize
# 11. np.unique with return_*
# 12. bincount
# 13. histogram and histogram2d
# 14. Set Operations
# 15. Sorting and Sort Kinds
# 16. partition and argpartition
# 17. lexsort
# 18. NaN-Aware Functions
# 19. Cumulative Operations
# 20. diff, gradient, convolve, correlate
# 21. clip, round, floor Variants
# 22. Cross-References
#
# Related: 02 (basic/fancy indexing, boolean masks), 05 (stats), 08 (vectorization),
# 10 (structured/masked arrays, select), 11 (views vs copies).

import warnings

import numpy as np

# 01. take and put
# ----------------------------
# - np.take(a, indices, axis) = fancy indexing with an explicit axis and mode option.
# - mode='clip' / 'wrap' handle out-of-range indexes instead of raising IndexError.
# - np.put(a, indices, values) writes into the FLATTENED array in place.
# - np.putmask / np.place write wherever a mask is True.

a = np.array([[10, 11, 12], [20, 21, 22], [30, 31, 32]])
print("a =\n", a)
print("np.take(a, [0, 2], axis=0) =\n", np.take(a, [0, 2], axis=0))
print("np.take(a, [0, 2], axis=1) =\n", np.take(a, [0, 2], axis=1))
print("np.take(a, [1, 10]) flat, mode='wrap':", np.take(a, [1, 10], mode="wrap"), "(10 wraps to 10 % 9 = 1)")
print("np.take(a, [1, 99], mode='clip'):", np.take(a, [1, 99], mode="clip"), "(99 -> last element)")
try:
    np.take(a, [99])
except IndexError as e:
    print("mode='raise' (default) ->", type(e).__name__)
p = np.arange(6)
np.put(p, [0, 5], [-1, -5])
print("np.put(p, [0,5], [-1,-5]):", p)
np.put(p, [1, 2, 3], [100])
print("values repeat if too few:", p)
np.putmask(p, p > 50, 0)
print("putmask(p > 50 -> 0):", p)
print("# Gotcha: np.put indexes the FLATTENED array, even for 2-D input.")
print("#   Plain fancy indexing a[idx] is just as good; take mostly adds axis= and mode=.")
print()

# 02. take_along_axis and put_along_axis
# ----------------------------
# - Picks one (or several) element per row/column using an index array of matching shape.
# - Typical use: apply the result of argsort / argmax per row.
# - Index array must have the same ndim as the data; use keepdims=True.

scores = np.array([[0.2, 0.9, 0.4],
                   [0.7, 0.1, 0.6]])
order = np.argsort(scores, axis=1)
print("argsort per row:\n", order)
print("sorted rows via take_along_axis:\n", np.take_along_axis(scores, order, axis=1))
best = np.argmax(scores, axis=1, keepdims=True)
print("argmax(keepdims=True) shape:", best.shape)
print("best value per row:", np.take_along_axis(scores, best, axis=1).ravel())
top2 = order[:, ::-1][:, :2]
print("top-2 per row:\n", np.take_along_axis(scores, top2, axis=1))
z = np.zeros((2, 3), dtype=int)
np.put_along_axis(z, best, 1, axis=1)
print("one-hot per row via put_along_axis:\n", z)
print("# Gotcha: scores[order] would index ROWS, not elements within each row. For per-row")
print("#   reordering use take_along_axis (or scores[np.arange(n)[:, None], order]).")
print()

# 03. np.ix_ and ravel_multi_index
# ----------------------------
# - np.ix_(rows, cols) builds an "open mesh" so a[np.ix_(r, c)] selects a SUB-GRID.
# - Without ix_, a[[0,2],[0,2]] pairs indexes -> just 2 points (the diagonal).
# - ravel_multi_index converts (row, col) pairs to flat positions; unravel_index goes back.

print("a[[0, 2], [0, 2]] (paired points) =", a[[0, 2], [0, 2]])
print("a[np.ix_([0, 2], [0, 2])] (sub-grid) =\n", a[np.ix_([0, 2], [0, 2])])
print("np.ix_ with a boolean mask:", a[np.ix_(np.array([True, False, True]), [1])].ravel())
flat = np.ravel_multi_index(([0, 1, 2], [2, 1, 0]), a.shape)
print("ravel_multi_index of (0,2),(1,1),(2,0):", flat, "-> values", a.ravel()[flat])
print("unravel_index(5, (3,3)) =", np.unravel_index(5, (3, 3)))
print("unravel_index of argmax:", np.unravel_index(np.argmax(a), a.shape), "(2-D position of the max)")
print("ravel_multi_index mode='clip':", np.ravel_multi_index(([5], [5]), (3, 3), mode="clip"))
print("# Gotcha: argmax on a 2-D array returns a FLAT index. Use unravel_index for (row, col).")
print()

# 04. ufunc Methods: reduce, accumulate, outer
# ----------------------------
# - Every binary ufunc (add, multiply, maximum, logical_and, ...) has methods:
#     reduce      fold along an axis -> one value per remaining position
#     accumulate  running fold (keeps the intermediate results)
#     outer       apply to all pairs (a_i op b_j)
# - np.add.reduce(x) is what x.sum() calls.

x = np.array([1, 2, 3, 4])
print("np.add.reduce(x) =", np.add.reduce(x), ", np.multiply.reduce(x) =", np.multiply.reduce(x))
print("np.add.accumulate(x) =", np.add.accumulate(x), "(same as np.cumsum)")
print("np.maximum.accumulate([3,1,4,1,5,2]) =", np.maximum.accumulate([3, 1, 4, 1, 5, 2]), "(running max)")
print("np.logical_and.reduce([True, True, False]) =", np.logical_and.reduce([True, True, False]))
m = np.arange(6).reshape(2, 3)
print("np.add.reduce(m, axis=0) =", np.add.reduce(m, axis=0), ", axis=1 =", np.add.reduce(m, axis=1))
print("np.add.reduce(m, axis=None) =", np.add.reduce(m, axis=None))
print("np.add.reduce(m, axis=1, keepdims=True) shape:", np.add.reduce(m, axis=1, keepdims=True).shape)
print("np.add.reduce(x, initial=100) =", np.add.reduce(x, initial=100))
print("np.multiply.outer([1,2,3], [10,20]) =\n", np.multiply.outer([1, 2, 3], [10, 20]))
print("np.subtract.outer([5,6], [1,2,3]) =\n", np.subtract.outer([5, 6], [1, 2, 3]))
print("np.equal.outer(x, [2, 4]) =\n", np.equal.outer(x, [2, 4]))
print("np.power.outer([1,2,3], [1,2,3]) (a table of powers) =\n", np.power.outer([1, 2, 3], [1, 2, 3]))
print("# Gotcha: reduce on an EMPTY array needs an identity: np.add.reduce([]) is 0.0 but")
print("#   np.maximum.reduce([]) raises ValueError. Pass initial= for ufuncs without one.")
print()

# 05. ufunc Methods: at and reduceat
# ----------------------------
# - ufunc.at(a, idx, vals): UNBUFFERED in-place op. Repeated indexes all count.
# - Plain a[idx] += 1 with repeated indexes applies only once per position.
# - reduceat(a, starts): reduce over slices [starts[i] : starts[i+1]] in one call.

c1 = np.zeros(4, dtype=int)
c1[[0, 0, 1]] += 1
print("a[[0,0,1]] += 1 gives (repeat ignored):", c1)
c2 = np.zeros(4, dtype=int)
np.add.at(c2, [0, 0, 1], 1)
print("np.add.at(..., [0,0,1], 1) gives:", c2)
c3 = np.zeros(4, dtype=int)
np.add.at(c3, [0, 0, 1, 3], [5, 6, 7, 8])
print("add.at with per-index values:", c3)
mx = np.full(3, -np.inf)
np.maximum.at(mx, [0, 1, 0, 2, 1], [4.0, 1.0, 9.0, 2.0, 0.5])
print("maximum.at group maxima:", mx)
vals = np.arange(10)
print("np.add.reduceat(0..9, [0, 3, 7]) =", np.add.reduceat(vals, [0, 3, 7]), "(sums of 0:3, 3:7, 7:end)")
print("np.maximum.reduceat([1,5,2,8,3], [0, 2]) =", np.maximum.reduceat([1, 5, 2, 8, 3], [0, 2]))
print("# Gotcha: reduceat with a start index >= the next one returns just a[start], not an empty")
print("#   reduction. np.add.at is slower than bincount for plain counting, but more general.")
print()

# 06. frompyfunc and np.vectorize (and Why They Are Slow)
# ----------------------------
# - np.vectorize(f): wraps a scalar Python function so it accepts arrays and broadcasts.
#   It is a convenience for syntax, NOT a speed-up - it still calls f once per element.
# - np.frompyfunc(f, nin, nout): real ufunc-like object but always returns object arrays.
# - Real speed comes from rewriting with array ops (np.where, np.select, ufuncs).

def clamp_scale(v, lo):
    return v * 2 if v > lo else lo

vec = np.vectorize(clamp_scale)
data = np.array([1, 5, 3, 9])
print("np.vectorize result:", vec(data, 4), "(scalar lo broadcast)")
print("vectorize guesses output dtype from the FIRST result:", vec(data, 4).dtype.kind, "(i = integer)")
vec_f = np.vectorize(clamp_scale, otypes=[float])
print("with otypes=[float]:", vec_f(data, 4))
print("vectorized with np.where:", np.where(data > 4, data * 2, 4))
fp = np.frompyfunc(lambda s, n: s * n, 2, 1)
out = fp(np.array(["ab", "c"]), 2)
print("frompyfunc output dtype:", out.dtype, ", values:", out.tolist())
print("frompyfunc(...).astype(float) to get real numbers:", np.frompyfunc(lambda t: t + 0.5, 1, 1)(np.arange(3)).astype(float))
big = np.arange(20000)
print("same result both ways:", np.array_equal(np.vectorize(lambda t: t * 3 + 1)(big), big * 3 + 1))
print("# Gotcha: np.vectorize on an EMPTY input needs otypes= or it raises ValueError, and its")
print("#   first-result dtype guess can truncate: first output int -> later floats become ints.")
print("#   Rule: if you find yourself reaching for vectorize, look for where/select/ufuncs first.")
print()

# 07. apply_along_axis and apply_over_axes
# ----------------------------
# - apply_along_axis(f, axis, arr): call f on every 1-D slice along that axis.
#   Still a Python loop underneath - use only when no built-in axis= version exists.
# - apply_over_axes(f, a, axes): apply a reducing function over several axes in turn,
#   keeping dimensions (so the result broadcasts back).

def spread(v):
    return v.max() - v.min()

grid = np.array([[3, 9, 1], [4, 4, 8], [7, 2, 5]])
print("apply_along_axis(spread, axis=1):", np.apply_along_axis(spread, 1, grid), "(per row)")
print("apply_along_axis(spread, axis=0):", np.apply_along_axis(spread, 0, grid), "(per column)")
print("built-in equivalent np.ptp(axis=1):", np.ptp(grid, axis=1))
print("apply_along_axis returning vectors (sorted desc per row):\n",
      np.apply_along_axis(lambda r: np.sort(r)[::-1], 1, grid))
cube = np.arange(24).reshape(2, 3, 4)
print("apply_over_axes(np.sum, cube, [0, 2]).shape:", np.apply_over_axes(np.sum, cube, [0, 2]).shape, "(kept as 1)")
print("same as cube.sum(axis=(0,2), keepdims=True):", np.array_equal(np.apply_over_axes(np.sum, cube, [0, 2]), cube.sum(axis=(0, 2), keepdims=True)))
print("# Gotcha: apply_along_axis is NOT vectorized - roughly as slow as a Python for-loop.")
print("#   Prefer arr.max(axis=...) etc. when the function is a standard reduction.")
print()

# 08. einsum Step by Step
# ----------------------------
# - einsum('subscripts', *arrays): write each array's axes as letters; a letter that
#   appears in the inputs but NOT after '->' is summed over; letters after '->' stay.
# - Repeated letter in ONE operand = diagonal. Output order is up to you.
# - Read it as: for every combination of letters, multiply, then sum the dropped ones.

v1 = np.array([1, 2, 3])
v2 = np.array([4, 5, 6])
M = np.arange(6).reshape(2, 3)
N = np.arange(12).reshape(3, 4)
sq = np.array([[1, 2], [3, 4]])
print("1. sum of vector       'i->'     :", np.einsum("i->", v1))
print("2. elementwise product 'i,i->i'  :", np.einsum("i,i->i", v1, v2))
print("3. dot product         'i,i->'   :", np.einsum("i,i->", v1, v2), "(matches np.dot:", np.dot(v1, v2), ")")
print("4. outer product       'i,j->ij' :\n", np.einsum("i,j->ij", v1, v2))
print("5. transpose           'ij->ji'  :", np.einsum("ij->ji", M).shape)
print("6. column sums         'ij->j'   :", np.einsum("ij->j", M), ", row sums 'ij->i':", np.einsum("ij->i", M))
print("7. matrix product      'ij,jk->ik': equal to M @ N:", np.array_equal(np.einsum("ij,jk->ik", M, N), M @ N))
print("8. trace               'ii->'    :", np.einsum("ii->", sq), ", diagonal 'ii->i':", np.einsum("ii->i", sq))
print("9. matrix-vector       'ij,j->i' :", np.einsum("ij,j->i", M, v1), "(same as M @ v1:", M @ v1, ")")
print("10. row-wise dot       'ij,ij->i':", np.einsum("ij,ij->i", M, M), "(sum of squares per row)")
batch_a = np.arange(2 * 2 * 3).reshape(2, 2, 3)
batch_b = np.arange(2 * 3 * 2).reshape(2, 3, 2)
print("11. batched matmul 'bij,bjk->bik' matches np.matmul:", np.array_equal(np.einsum("bij,bjk->bik", batch_a, batch_b), np.matmul(batch_a, batch_b)))
print("12. all-pairs squared distance (3 pts, 2-D): 'id,jd->ij' on difference:")
pts = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0]])
dots = np.einsum("id,jd->ij", pts, pts)
sqn = np.einsum("id,id->i", pts, pts)
print(sqn[:, None] + sqn[None, :] - 2 * dots)
print("13. implicit mode 'ij,jk' (no ->) sorts output letters alphabetically:", np.einsum("ij,jk", M, N).shape)
print("14. ellipsis '...ij->...ji' transposes the last two axes of anything:", np.einsum("...ij->...ji", batch_a).shape)
print("# Gotcha: a letter in the output that is not in any input is an error; a letter missing from")
print("#   the output is SUMMED. optimize=True may reorder multi-operand contractions for speed.")
print()

# 09. searchsorted
# ----------------------------
# - np.searchsorted(sorted_arr, values, side='left'|'right'): binary search - returns the
#   insertion index that keeps the array sorted. O(log n) per query.
# - Also the tool for "which bin" / "nearest value" lookups.

s = np.array([10, 20, 20, 30, 40])
print("searchsorted(s, 20, 'left') =", np.searchsorted(s, 20, "left"), ", 'right' =", np.searchsorted(s, 20, "right"))
print("count of 20s =", np.searchsorted(s, 20, "right") - np.searchsorted(s, 20, "left"))
print("many queries at once:", np.searchsorted(s, [5, 25, 40, 99]))
print("exact membership test:", [bool(i < len(s) and s[i] == q) for i, q in zip(np.searchsorted(s, [20, 25]), [20, 25])])
q = np.array([12, 29, 38])
idx = np.clip(np.searchsorted(s, q), 1, len(s) - 1)
left, right = s[idx - 1], s[idx]
nearest = np.where(q - left <= right - q, left, right)
print("nearest value to [12,29,38]:", nearest)
print("with sorter= (unsorted data):", np.searchsorted(np.array([30, 10, 20]), 15, sorter=np.argsort([30, 10, 20])))
print("# Gotcha: input MUST be sorted ascending - otherwise results are silent garbage, no error.")
print()

# 10. digitize
# ----------------------------
# - np.digitize(x, bins, right=False): bin number for each x. bins must be monotonic.
# - Returns 0 for x below first edge and len(bins) for x above the last.
# - Basically searchsorted with a different side convention (side='right' default).

ages = np.array([3, 17, 18, 40, 65, 90])
edges = np.array([18, 65])
labels = np.array(["child", "adult", "senior"])
b = np.digitize(ages, edges)
print("digitize(ages, [18, 65]) =", b, "->", labels[b].tolist())
print("right=True moves the boundary:", np.digitize(ages, edges, right=True))
print("same as searchsorted(side='right'):", np.array_equal(b, np.searchsorted(edges, ages, side="right")))
print("decreasing bins also work:", np.digitize([5, 15], [20, 10, 0]))
print("# Gotcha: digitize result 0 means 'below first edge' - indexes labels[b] must have len(bins)+1 items.")
print()

# 11. np.unique with return_*
# ----------------------------
# - np.unique(a): sorted unique values (flattens the input unless axis= is given).
# - return_index: position of first occurrence. return_inverse: rebuilds the original
#   from unique values. return_counts: how many times each appears.
# - np.unique(rows, axis=0) finds unique ROWS.

items = np.array([3, 1, 2, 3, 1, 3])
u, first, inv, cnt = np.unique(items, return_index=True, return_inverse=True, return_counts=True)
print("unique:", u, ", first idx:", first, ", counts:", cnt)
print("inverse:", inv, "-> u[inv] rebuilds:", u[inv])
print("most common value:", u[np.argmax(cnt)])
rows = np.array([[1, 2], [3, 4], [1, 2], [5, 6]])
print("unique rows (axis=0):\n", np.unique(rows, axis=0))
print("words unique:", np.unique(np.array(["pear", "apple", "pear", "fig"])).tolist())
print("keep ORIGINAL order of first appearance:", items[np.sort(first)])
print("duplicate flags:", ~np.isin(np.arange(len(items)), first))
print("np.unique(2-D) flattens:", np.unique(np.array([[2, 1], [2, 3]])))
print("# Gotcha: output is SORTED, not in appearance order. Use return_index to recover first-seen order.")
print("#   For 2-D input without axis=, the result (and inverse) are flattened.")
print()

# 12. bincount
# ----------------------------
# - np.bincount(x): counts of each non-negative INT value 0..max. Very fast.
# - weights= turns counts into per-bin sums. minlength= pads the output.
# - Compare with np.unique counts: bincount is faster but only for small non-negative ints.

labels_arr = np.array([0, 2, 2, 1, 2, 0])
print("bincount:", np.bincount(labels_arr))
print("minlength=5:", np.bincount(labels_arr, minlength=5))
w = np.array([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
sums = np.bincount(labels_arr, weights=w)
print("group sums by label (weights):", sums)
print("group means:", sums / np.bincount(labels_arr))
print("confusion-style 2-D count via ravel_multi_index:",
      np.bincount(np.ravel_multi_index(([0, 1, 1, 1], [0, 1, 1, 0]), (2, 2)), minlength=4).reshape(2, 2).tolist())
try:
    np.bincount(np.array([-1, 2]))
except ValueError as e:
    print("negative value ->", type(e).__name__)
print("# Gotcha: bincount output length is max+1 - a single huge value like 10**9 allocates a")
print("#   giant array. Use np.unique(return_inverse=True) first to compress sparse labels.")
print()

# 13. histogram and histogram2d
# ----------------------------
# - np.histogram(x, bins, range) -> (counts, edges). bins can be an int or explicit edges.
# - All bins are half-open [a, b) EXCEPT the last, which is closed [a, b].
# - density=True makes the area (not the height) sum to 1.
# - histogram2d(x, y, bins) -> counts grid, x edges, y edges.

h_data = np.array([1, 2, 2, 3, 3, 3, 4, 4, 4, 4, 10])
counts, edges = np.histogram(h_data, bins=[0, 2, 4, 6, 10])
print("counts:", counts, ", edges:", edges)
print("value 10 (== last edge) is included in the last bin:", counts[-1])
print("bins=3 auto edges:", np.histogram(h_data, bins=3)[1])
dens, e2 = np.histogram(h_data, bins=[0, 2, 4, 6, 10], density=True)
print("density sums with widths to 1:", np.sum(dens * np.diff(e2)))
print("histogram with range=(0, 5):", np.histogram(h_data, bins=5, range=(0, 5))[0], "(10 is outside, dropped)")
hx = np.array([0.5, 1.5, 1.5, 2.5])
hy = np.array([0.5, 0.5, 1.5, 1.5])
H, xe, ye = np.histogram2d(hx, hy, bins=[[0, 1, 2, 3], [0, 1, 2]])
print("histogram2d counts (rows=x bins, cols=y bins):\n", H)
print("np.histogram_bin_edges(h_data, bins='auto') length:", len(np.histogram_bin_edges(h_data, bins="auto")))
print("# Gotcha: histogram2d rows are the X bins and columns are the Y bins - the opposite of how")
print("#   an image/plot is drawn, so transpose before imshow.")
print()

# 14. Set Operations
# ----------------------------
# - union1d, intersect1d, setdiff1d, setxor1d: return SORTED unique results.
# - np.isin(a, b): boolean mask of "is each element of a in b" - keeps a's shape.
#   (in1d is the older flat version; isin replaces it.)
# - intersect1d(return_indices=True) gives where the common values sit.

p1 = np.array([5, 1, 3, 3, 7])
p2 = np.array([3, 7, 9, 9])
print("union1d:", np.union1d(p1, p2))
print("intersect1d:", np.intersect1d(p1, p2))
print("setdiff1d(p1, p2):", np.setdiff1d(p1, p2))
print("setxor1d:", np.setxor1d(p1, p2))
print("isin(p1, p2):", np.isin(p1, p2), ", invert=True:", np.isin(p1, p2, invert=True))
print("filter p1 by membership:", p1[np.isin(p1, p2)])
common, i1, i2 = np.intersect1d(p1, p2, return_indices=True)
print("intersect indices:", common, i1, i2)
print("isin keeps 2-D shape:", np.isin(np.array([[1, 5], [9, 3]]), p1).tolist())
print("# Gotcha: results are sorted and de-duplicated - not the order of the input. isin is the")
print("#   one that preserves order and duplicates in the first argument.")
print()

# 15. Sorting and Sort Kinds
# ----------------------------
# - np.sort(a) returns a sorted COPY; a.sort() sorts in place and returns None.
# - np.argsort gives the indexes that would sort. axis=-1 by default (sorts each row).
# - kind: 'quicksort' (default, introsort, not stable), 'mergesort'/'stable' (stable),
#   'heapsort'. Use 'stable' when ties must keep input order or for multi-pass sorting.
# - Descending: sort then [::-1], or negate numbers. a[::-1] is a view.

raw = np.array([3, 1, 2, 1, 3])
print("np.sort:", np.sort(raw), ", original untouched:", raw)
tmp = raw.copy()
print("in-place tmp.sort() returns:", tmp.sort(), ", tmp is now", tmp)
print("argsort kind='stable' (ties keep original order):", np.argsort(raw, kind="stable"))
print("descending stable by negation:", np.argsort(-raw, kind="stable"))
two = np.array([[3, 1, 2], [9, 8, 7]])
print("sort axis=1 (default):", np.sort(two, axis=1).tolist(), ", axis=0:", np.sort(two, axis=0).tolist())
print("sort axis=None flattens:", np.sort(two, axis=None))
recs = np.array([("b", 2), ("a", 2), ("c", 1)], dtype=[("name", "U1"), ("n", "i4")])
print("sort structured by field 'n' then name:", np.sort(recs, order=["n", "name"]).tolist())
print("sorted check:", bool(np.all(np.diff(np.sort(raw)) >= 0)))
print("strings sort lexicographically:", np.sort(np.array(["b10", "b2", "a"])).tolist())
print("# Gotcha: the default sort is NOT stable. Two-pass sorts (secondary key first, then primary)")
print("#   only work with kind='stable'. Also, NaNs sort to the END.")
print("nan sort:", np.sort(np.array([2.0, np.nan, 1.0])))
print()

# 16. partition and argpartition
# ----------------------------
# - np.partition(a, k): puts the k-th smallest in sorted position; smaller values before,
#   larger after, but neither side is sorted. O(n) instead of O(n log n).
# - Perfect for "top-k" and median-like questions on large arrays.

pa = np.array([9, 4, 7, 1, 8, 3, 6])
print("sorted for reference:", np.sort(pa))
part = np.partition(pa, 2)
print("partition(k=2):", part, "-> element [2] =", part[2], "(3rd smallest, in its final place)")
print("3 smallest (any order):", np.sort(np.partition(pa, 2)[:3]))
k = 3
topk_idx = np.argpartition(pa, -k)[-k:]
print("indexes of top-3:", np.sort(topk_idx), "values:", np.sort(pa[topk_idx])[::-1])
print("median via partition:", np.partition(pa, len(pa) // 2)[len(pa) // 2], "vs np.median:", np.median(pa))
print("multiple kth: partition(pa, [1, 4])[[1, 4]] =", np.partition(pa, [1, 4])[[1, 4]])
mat = np.array([[5, 2, 9], [1, 8, 3]])
print("argpartition per row (smallest 1):", np.argpartition(mat, 0, axis=1)[:, 0])
print("# Gotcha: only position k is guaranteed. The rest of the 'small half' is in arbitrary")
print("#   order - sort that slice yourself if you need top-k ordered.")
print()

# 17. lexsort
# ----------------------------
# - np.lexsort((secondary, primary)): sort by several keys. The LAST key is the PRIMARY one.
# - Returns indexes (like argsort). Stable. Works on columns of separate arrays.

last = np.array(["Lee", "Kim", "Lee", "Kim"])
first_n = np.array(["Ann", "Zed", "Bob", "Amy"])
order = np.lexsort((first_n, last))
print("lexsort by last name then first name:", list(zip(last[order], first_n[order])))
score = np.array([90, 85, 90, 85])
order2 = np.lexsort((first_n, -score))
print("score desc then first name:", list(zip(score[order2].tolist(), first_n[order2])))
table = np.array([[2, 1], [1, 9], [2, 0], [1, 3]])
print("sort rows by col0 then col1:\n", table[np.lexsort((table[:, 1], table[:, 0]))])
print("# Gotcha: key order is REVERSED from what people expect (last key sorts first).")
print("#   Negate numeric keys for descending; strings cannot be negated.")
print()

# 18. NaN-Aware Functions
# ----------------------------
# - nansum, nanmean, nanstd, nanvar, nanmin, nanmax, nanargmin, nanargmax, nanmedian,
#   nanpercentile, nanprod, nancumsum, nancumprod ignore nans.
# - They treat all-nan slices differently (warn, return nan) - decide how to handle.

nv = np.array([[1.0, np.nan, 3.0], [np.nan, np.nan, np.nan]])
print("sum:", nv.sum(axis=1), "| nansum:", np.nansum(nv, axis=1), "(all-nan row sums to 0.0)")
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    print("nanmean per row:", np.nanmean(nv, axis=1), "(all-nan -> nan, with a RuntimeWarning)")
print("nanmax:", np.nanmax(nv[0]), ", nanargmax:", np.nanargmax(nv[0]))
print("nanstd of [1,nan,3]:", np.nanstd(nv[0]))
print("nanmedian:", np.nanmedian(np.array([1.0, np.nan, 5.0, 9.0])))
print("nancumsum:", np.nancumsum(np.array([1.0, np.nan, 2.0])))
print("count valid per column:", np.count_nonzero(~np.isnan(nv), axis=0))
print("mean with fill:", np.where(np.isnan(nv), np.nanmean(nv[0]), nv)[0])
print("# Gotcha: np.max / np.mean propagate nan, np.nanmax / np.nanmean skip it. nanargmax raises on an")
print("#   all-nan slice. Integer arrays cannot hold nan, so nan-functions are for floats.")
print()

# 19. Cumulative Operations
# ----------------------------
# - cumsum, cumprod, np.maximum.accumulate (running max), np.minimum.accumulate.
# - axis= picks direction. The output has the same shape as the input.
# - cumsum - shifted = windowed sums (see section 20 for diff).

cv = np.array([2, 1, 4, 3])
print("cumsum:", np.cumsum(cv), ", cumprod:", np.cumprod(cv))
cm = np.arange(6).reshape(2, 3)
print("cumsum axis=0:", np.cumsum(cm, axis=0).tolist(), ", axis=1:", np.cumsum(cm, axis=1).tolist())
print("cumsum of 2-D with axis=None flattens:", np.cumsum(cm))
print("running max:", np.maximum.accumulate(cv), ", running min:", np.minimum.accumulate(cv))
print("fraction of total so far:", np.cumsum(cv) / cv.sum())
cs = np.concatenate(([0], np.cumsum(cv)))
print("sum of cv[1:3] via prefix sums:", cs[3] - cs[1], "(same as", cv[1:3].sum(), ")")
print("cumsum on a bool counts Trues so far:", np.cumsum(np.array([True, False, True, True])))
print("cumsum of int8 widens the accumulator:", np.cumsum(np.array([100, 100], dtype=np.int8)).tolist(), "(no int8 wrap)")
print("cumprod 1..25 last value in int64:", int(np.cumprod(np.arange(1, 26, dtype=np.int64))[-1]), "(wrong; true 25! is much larger)")
print("# Gotcha: cumprod grows fast - int64 overflow wraps silently, as the line above shows.")
print()

# 20. diff, gradient, convolve, correlate
# ----------------------------
# - np.diff(a, n, axis): differences of neighbours (length shrinks by 1 per pass).
# - np.gradient(a): numeric derivative; same length as input (central differences).
# - np.convolve(a, v, mode): sliding weighted sum with the kernel FLIPPED.
# - np.correlate(a, v, mode): same without flipping. 'valid', 'same', 'full' modes.

sq_t = np.array([0, 1, 4, 9, 16, 25])
print("diff:", np.diff(sq_t), ", second diff (n=2):", np.diff(sq_t, n=2))
print("diff on 2-D axis=1:", np.diff(np.array([[1, 4, 9], [2, 2, 2]]), axis=1).tolist())
print("diff with prepend to keep length:", np.diff(sq_t, prepend=0))
print("gradient (unit spacing):", np.gradient(sq_t.astype(float)))
print("gradient with x coords:", np.gradient(sq_t.astype(float), np.array([0, 2, 4, 6, 8, 10.0])))
sig = np.array([1, 2, 3, 4, 5], dtype=float)
box = np.ones(3) / 3
print("convolve 'valid' (moving avg):", np.convolve(sig, box, mode="valid"))
print("convolve 'same':", np.convolve(sig, box, mode="same"))
print("convolve 'full' length:", len(np.convolve(sig, box, mode="full")))
print("kernel flip matters: convolve with [1,0,-1]:", np.convolve(sig, [1, 0, -1], "valid"),
      "| correlate:", np.correlate(sig, [1, 0, -1], "valid"))
print("polynomial multiply via convolve (1+x)(1+x):", np.convolve([1, 1], [1, 1]))
sig2 = np.array([0, 1, 0.5])
print("correlate full (signal vs itself):", np.correlate(sig2, sig2, "full"))
print("# Gotcha: convolve is 1-D only (use scipy.signal for 2-D). Edges in 'same' mode are")
print("#   zero-padded, so the first/last averages are pulled toward 0.")
print()

# 21. clip, round, floor Variants
# ----------------------------
# - np.clip(a, lo, hi): limit values. Either bound may be None.
# - np.round / around: round half to EVEN. decimals=-1 rounds to tens.
# - floor (toward -inf), ceil (toward +inf), trunc (toward 0), rint (nearest, half-even).
# - floor_divide (//) and mod (%) use floor semantics; np.fmod / np.remainder differ for negatives.

r = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5, 2.7, -2.7])
print("values   :", r)
print("round    :", np.round(r))
print("rint     :", np.rint(r), "(same as round)")
print("floor    :", np.floor(r))
print("ceil     :", np.ceil(r))
print("trunc    :", np.trunc(r))
print("astype(int) truncates too:", r.astype(int))
print("round decimals=1:", np.round(np.array([1.25, 1.35, 2.675]), 1), "(float storage error + half-even)")
print("round decimals=-1:", np.round(np.array([14, 15, 25, 36]), -1))
print("clip(0, 1):", np.clip(np.array([-0.5, 0.3, 1.7]), 0, 1), ", lower only:", np.clip(np.array([-3, 2, 9]), 0, None))
print("-7 // 2 =", np.floor_divide(-7, 2), ", -7 % 2 =", np.mod(-7, 2), "(floor-based)")
print("np.fmod(-7, 2) =", np.fmod(-7, 2), "(sign follows dividend, like C)")
print("np.divmod(-7, 2):", tuple(int(t) for t in np.divmod(-7, 2)))
print("np.sign:", np.sign(np.array([-3, 0, 5])), ", np.abs:", np.abs(np.array([-3, 0, 5])))
print("# Gotcha: np.round(2.5) is 2.0 and round(3.5) is 4.0 (half to even), not school rounding.")
print("#   For half-up use np.floor(x + 0.5). Also astype(int) truncates toward zero, not floor.")
print()

# 22. Cross-References
# ----------------------------
# - 02-Indexing-And-Slicing: fancy and boolean indexing (take/put build on it).
# - 05-Statistical-And-Math-Functions: sum/mean/percentile (here: nan-aware, cumulative).
# - 06-Linear-Algebra: matmul/dot (here: einsum as the general form).
# - 08-Performance-And-Vectorization: why loops lose (here: vectorize/apply_along_axis are loops).
# - 10-Advanced-NumPy: structured arrays, np.select, meshgrid.
# - 11-Strides-And-Memory-Layout: views vs copies, which explains put/take behaviour.
# - 13-NumPy-Recipes-And-Real-Patterns: these tools combined in real tasks.

print("Rule of thumb: pick the narrowest tool - take/put for axis picks, bincount/unique for counting,")
print("partition for top-k, searchsorted for lookups, einsum when axes need names.")
