# 01. Normalisation: Min-Max Scaling
# 02. Standardisation: Z-Scores
# 03. One-Hot Encoding
# 04. Pairwise Distance Matrix via Broadcasting
# 05. Moving Average
# 06. Running Max and Running Statistics
# 07. Image-Like 3D Arrays: Build and Crop
# 08. Image-Like 3D Arrays: Flip and Rotate
# 09. Image-Like 3D Arrays: Grayscale and Brightness
# 10. Simple Monte Carlo (Seeded default_rng)
# 11. K-Means-Lite
# 12. Batch Matrix Operations
# 13. datetime64 and timedelta64 Arithmetic
# 14. Business-Day Functions
# 15. Boolean-Mask Idioms
# 16. Avoiding Python Loops: Patterns
# 17. Mini Linear Regression with lstsq
# 18. Cheat Sheet: Loop vs Vectorized
# 19. Cross-References
#
# Related: 04 (broadcasting), 05 (stats), 06 (linalg), 07 (random), 08 (vectorization),
# 11 (dtype overflow), 12 (bincount, einsum, sorting).

import numpy as np

rng = np.random.default_rng(42)

# 01. Normalisation: Min-Max Scaling
# ----------------------------
# - Min-max: (x - min) / (max - min) maps data to [0, 1]. Per COLUMN uses axis=0.
# - keepdims=True keeps the reduced axis as size 1 so broadcasting just works.
# - Guard against max == min (division by zero).

X = np.array([[1.0, 200.0, 5.0],
              [2.0, 400.0, 5.0],
              [4.0, 800.0, 5.0]])
lo, hi = X.min(axis=0, keepdims=True), X.max(axis=0, keepdims=True)
span = hi - lo
scaled = (X - lo) / np.where(span == 0, 1.0, span)
print("X =\n", X)
print("min-max per column:\n", scaled)
print("global min-max (one scale for all):\n", np.round((X - X.min()) / (X.max() - X.min()), 3))
print("without the guard, the constant column gives:", end=" ")
with np.errstate(invalid="ignore"):
    print(((X - lo) / span)[:, 2])
print("# Gotcha: forgetting axis=0 scales by ONE global min/max - mixes features with different units.")
print("#   Compute lo/hi on TRAINING data only and reuse them on test data to avoid leakage.")
print()

# 02. Standardisation: Z-Scores
# ----------------------------
# - z = (x - mean) / std gives mean 0 and std 1 per column.
# - ddof=0 (population, NumPy default) vs ddof=1 (sample std).
# - Row-wise version uses axis=1 with keepdims=True.

mu = X.mean(axis=0, keepdims=True)
sigma = X.std(axis=0, keepdims=True)
z = (X - mu) / np.where(sigma == 0, 1.0, sigma)
print("z-scores:\n", np.round(z, 3))
print("column means after:", np.round(z.mean(axis=0), 6), ", stds after:", np.round(z.std(axis=0), 6))
print("sample std (ddof=1) of col 0:", round(X[:, 0].std(ddof=1), 4), "vs population:", round(X[:, 0].std(), 4))
rowz = (X - X.mean(axis=1, keepdims=True)) / X.std(axis=1, keepdims=True)
print("row-wise z shape:", rowz.shape)
print("outlier flag |z| > 1.1:", (np.abs(z) > 1.1).tolist())
print("# Gotcha: a constant column has std 0, giving nan/inf. Replace 0 with 1 (as here) or add a tiny eps.")
print()

# 03. One-Hot Encoding
# ----------------------------
# - Index trick: np.eye(K)[labels] picks identity rows.
# - Or compare against arange: labels[:, None] == np.arange(K).
# - For text labels, np.unique(return_inverse=True) first.

labels = np.array([2, 0, 1, 2])
print("np.eye(3)[labels] =\n", np.eye(3, dtype=int)[labels])
print("compare form:\n", (labels[:, None] == np.arange(3)).astype(int))
cats = np.array(["red", "blue", "red", "green"])
uniq, codes = np.unique(cats, return_inverse=True)
print("categories:", uniq.tolist(), ", codes:", codes)
print("one-hot from codes:\n", np.eye(len(uniq), dtype=int)[codes])
oh = np.eye(3, dtype=int)[labels]
print("back to labels with argmax:", oh.argmax(axis=1))
print("# Gotcha: labels must be integers 0..K-1; a label equal to K raises IndexError.")
print("#   One-hot of a million rows x 1000 classes is a billion cells - use bincount or sparse methods.")
print()

# 04. Pairwise Distance Matrix via Broadcasting
# ----------------------------
# - points (n, d): points[:, None, :] has shape (n, 1, d), points[None, :, :] has (1, n, d).
#   Subtracting broadcasts to (n, n, d); sum squares over last axis -> (n, n).
# - Memory is n*n*d in the broadcast form. The dot-product trick uses only n*n.

P = np.array([[0.0, 0.0], [3.0, 4.0], [6.0, 8.0], [0.0, 1.0]])
diff = P[:, None, :] - P[None, :, :]
D = np.sqrt((diff ** 2).sum(axis=-1))
print("diff shape:", diff.shape)
print("distance matrix:\n", np.round(D, 3))
sq = (P ** 2).sum(axis=1)
D2 = sq[:, None] + sq[None, :] - 2 * P @ P.T
print("dot-product trick matches:", np.allclose(np.sqrt(np.maximum(D2, 0)), D))
print("symmetric:", np.allclose(D, D.T), ", zero diagonal:", np.allclose(np.diag(D), 0))
D_inf = D + np.diag(np.full(len(P), np.inf))
print("nearest neighbour of each point:", D_inf.argmin(axis=1))
print("farthest pair (i, j):", np.unravel_index(np.argmax(D), D.shape))
print("# Gotcha: the dot-product trick can give tiny NEGATIVE squares from rounding - clip with")
print("#   np.maximum(..., 0) before sqrt. And n=100,000 points makes a 10^10-cell matrix: chunk it.")
print()

# 05. Moving Average
# ----------------------------
# - Convolve with a box kernel, or use cumsum differences (fastest for long data),
#   or sliding_window_view(...).mean(axis=1).
# - 'valid' keeps only full windows: length n - w + 1.

series = np.array([1.0, 2.0, 6.0, 4.0, 5.0, 9.0, 3.0])
w = 3
conv = np.convolve(series, np.ones(w) / w, mode="valid")
cs = np.cumsum(np.insert(series, 0, 0.0))
cum = (cs[w:] - cs[:-w]) / w
win = np.lib.stride_tricks.sliding_window_view(series, w).mean(axis=1)
print("convolve   :", np.round(conv, 3))
print("cumsum     :", np.round(cum, 3))
print("window view:", np.round(win, 3))
print("all agree:", np.allclose(conv, cum) and np.allclose(conv, win))
padded = np.concatenate((np.full(w - 1, np.nan), conv))
print("aligned to input length (nan-padded start):", np.round(padded, 2))
alpha = 0.5
ema = np.empty_like(series)
ema[0] = series[0]
for t in range(1, len(series)):      # recursion: each value needs the previous, so a loop is natural
    ema[t] = alpha * series[t] + (1 - alpha) * ema[t - 1]
print("exponential moving average (loop is fine here):", np.round(ema, 3))
print("# Gotcha: output is shorter than input by w-1. cumsum difference can lose precision on very")
print("#   long float32 series. EMA depends on its own previous value, so it cannot be a plain ufunc.")
print()

# 06. Running Max and Running Statistics
# ----------------------------
# - np.maximum.accumulate = running max; minimum.accumulate = running min.
# - Drawdown = running max - value. cumsum / arange gives a running mean.
# - New-record flags: value equals its running max.

prices = np.array([10, 12, 11, 15, 14, 13, 16, 12])
runmax = np.maximum.accumulate(prices)
print("prices      :", prices)
print("running max :", runmax)
print("drawdown    :", runmax - prices)
print("max drawdown:", (runmax - prices).max())
print("new highs at positions:", np.flatnonzero(prices == runmax))
print("running mean:", np.round(np.cumsum(prices) / np.arange(1, len(prices) + 1), 2))
print("day-over-day change:", np.diff(prices), ", percent:", np.round(np.diff(prices) / prices[:-1] * 100, 1))
print("# Gotcha: percent change divides by the PREVIOUS value, so use prices[:-1], not prices[1:].")
print("#   Running means on long float32 data drift slowly - accumulate in float64.")
print()

# 07. Image-Like 3D Arrays: Build and Crop
# ----------------------------
# - An RGB image is shape (height, width, 3), dtype uint8 (0..255).
# - Batch of images: (N, H, W, 3). Channels-first layout (3, H, W) is also common.
# - Crop = plain slicing (returns a VIEW).

H, W = 6, 8
img = np.zeros((H, W, 3), dtype=np.uint8)
img[..., 0] = np.linspace(0, 255, W).astype(np.uint8)            # red ramps left -> right
img[..., 1] = np.linspace(0, 255, H).astype(np.uint8)[:, None]   # green ramps top -> bottom
img[2:4, 3:5] = [255, 255, 255]                                  # white square in the middle
print("img shape:", img.shape, ", dtype:", img.dtype, ", nbytes:", img.nbytes)
print("red channel:\n", img[..., 0])
print("pixel (2, 3):", img[2, 3].tolist(), ", pixel (0, 7):", img[0, 7].tolist())
crop = img[1:5, 2:6]
print("crop shape:", crop.shape, ", is a view:", np.shares_memory(img, crop))
crop_copy = img[1:5, 2:6].copy()
crop_copy[:] = 0
print("img untouched after editing the copy:", int(img.sum()) > 0)
border = img.copy()
border[[0, -1], :] = 0
border[:, [0, -1]] = 0
print("border zeroed, interior kept:", int(border[1:-1, 1:-1].sum()) == int(img[1:-1, 1:-1].sum()))
chw = np.moveaxis(img, -1, 0)
print("channels-first view shape:", chw.shape, ", still shares memory:", np.shares_memory(img, chw))
print("# Gotcha: slice crops are views - writing to a crop edits the original image. Copy first when you need an")
print("#   independent patch. Axis order is (row=y, column=x), so img[y, x], NOT img[x, y].")
print()

# 08. Image-Like 3D Arrays: Flip and Rotate
# ----------------------------
# - Flips are reversed slices (views): img[::-1] vertical, img[:, ::-1] horizontal.
# - np.flip(img, axis), np.rot90(img, k, axes=(0, 1)) rotate the spatial axes only.
# - Reversing the last axis swaps RGB <-> BGR.

tiny = np.arange(2 * 3 * 3, dtype=np.uint8).reshape(2, 3, 3)
print("tiny red channel:\n", tiny[..., 0])
print("flip up/down red:\n", tiny[::-1][..., 0])
print("flip left/right red:\n", tiny[:, ::-1][..., 0])
print("np.flip(axis=1) equals [:, ::-1]:", np.array_equal(np.flip(tiny, axis=1), tiny[:, ::-1]))
rot = np.rot90(tiny, k=1, axes=(0, 1))
print("rot90 shape (2,3,3) -> ", rot.shape, ", red channel:\n", rot[..., 0])
print("transpose (swap y/x) shape:", tiny.transpose(1, 0, 2).shape)
print("RGB -> BGR via [..., ::-1] first pixel:", tiny[0, 0].tolist(), "->", tiny[0, 0, ::-1].tolist())
print("flip is a view:", np.shares_memory(tiny, tiny[::-1]))
print("# Gotcha: tiny.T reverses ALL axes (including channels) - not an image transpose. Use")
print("#   transpose(1, 0, 2) or np.swapaxes(img, 0, 1).")
print()

# 09. Image-Like 3D Arrays: Grayscale and Brightness
# ----------------------------
# - Grayscale = weighted sum of channels (human eye: 0.299 R + 0.587 G + 0.114 B).
#   Use @ with a weight vector or np.dot over the last axis.
# - Do math in float or a wide int, then clip and convert back to uint8 (see 11 for wraparound).

weights = np.array([0.299, 0.587, 0.114])
gray = img @ weights
print("gray dtype:", gray.dtype, ", shape:", gray.shape, "(channel axis gone)")
print("gray rounded:\n", np.round(gray).astype(np.uint8))
gray_u8 = np.clip(np.round(gray), 0, 255).astype(np.uint8)
bright_wrong = img + np.uint8(100)
bright_ok = np.clip(img.astype(np.int16) + 100, 0, 255).astype(np.uint8)
print("pixel (2,3) before:", img[2, 3].tolist(), "-> wrong (wraps):", bright_wrong[2, 3].tolist(), "-> clipped:", bright_ok[2, 3].tolist())
print("mean per channel:", np.round(img.mean(axis=(0, 1)), 2))
print("threshold mask (gray > 128) count:", int((gray_u8 > 128).sum()))
masked = img.copy()
masked[gray_u8 <= 128] = 0
print("pixels kept after masking:", int(np.any(masked != 0, axis=-1).sum()))
print("per-channel histogram of red (4 bins):", np.histogram(img[..., 0], bins=4, range=(0, 256))[0])
norm = img.astype(np.float32) / 255.0
print("float image range:", float(norm.min()), "to", float(norm.max()))
print("# Gotcha: img + 100 on uint8 wraps (see 11). Also img * 0.5 silently makes float64 - cast back.")
print()

# 10. Simple Monte Carlo (Seeded default_rng)
# ----------------------------
# - Always create ONE Generator with a seed: rng = np.random.default_rng(seed).
# - Estimate pi: fraction of random points in the unit square that fall inside the quarter circle.
# - Accuracy improves like 1 / sqrt(N) - 100x more samples for 10x more accuracy.
# - See 07-Random-Module for the Generator API in detail.

rng_mc = np.random.default_rng(2024)
n = 200_000
xy = rng_mc.random((n, 2))
inside = (xy ** 2).sum(axis=1) <= 1.0
pi_est = 4 * inside.mean()
print("pi estimate with n =", n, ":", round(float(pi_est), 4))
print("error shrinks with N: ", end="")
for m in (100, 10_000, 1_000_000):
    pts = np.random.default_rng(1).random((m, 2))
    print(f"N={m}: {abs(4 * ((pts ** 2).sum(axis=1) <= 1).mean() - np.pi):.4f}", end="  ")
print()
dice = rng_mc.integers(1, 7, size=(100_000, 2)).sum(axis=1)
print("P(two dice sum to 7) ~", round(float((dice == 7).mean()), 3), "(exact 0.1667)")
print("P(sum >= 10) ~", round(float((dice >= 10).mean()), 3), "(exact 0.1667)")
walk = rng_mc.choice([-1, 1], size=(2000, 100)).sum(axis=1)
print("random-walk end position: mean ~", round(float(walk.mean()), 2), ", std ~", round(float(walk.std()), 2), "(theory std 10)")
boot = rng_mc.choice(series, size=(1000, len(series)), replace=True).mean(axis=1)
print("bootstrap 95% interval of the mean:", np.round(np.percentile(boot, [2.5, 97.5]), 2))
print("same seed twice gives the same draws:", np.array_equal(np.random.default_rng(5).random(3), np.random.default_rng(5).random(3)))
print("# Gotcha: results are only reproducible if the seed is fixed AND you draw in the same order.")
print("#   Printing the Monte Carlo estimate with many digits implies precision it does not have.")
print()

# 11. K-Means-Lite
# ----------------------------
# - Two steps repeated: (1) assign every point to its nearest centre, (2) move each centre to the
#   mean of its points. Assignment is vectorised with broadcasting; the loop is over ITERATIONS only.
# - Handle empty clusters. Real use: sklearn.cluster.KMeans (more robust).

rng_k = np.random.default_rng(7)
blob_a = rng_k.normal(loc=[0.0, 0.0], scale=0.5, size=(30, 2))
blob_b = rng_k.normal(loc=[5.0, 5.0], scale=0.5, size=(30, 2))
pts = np.vstack([blob_a, blob_b])
k = 2
centres = np.vstack([pts[0], pts[-1]])           # simple deterministic start: first and last point
for it in range(10):
    dists = ((pts[:, None, :] - centres[None, :, :]) ** 2).sum(axis=2)    # (n, k)
    assign = dists.argmin(axis=1)
    new_centres = np.array([pts[assign == j].mean(axis=0) if np.any(assign == j) else centres[j]
                            for j in range(k)])
    if np.allclose(new_centres, centres):
        break
    centres = new_centres
print("iterations used:", it + 1)
print("centres:\n", np.round(centres, 2))
print("cluster sizes:", np.bincount(assign, minlength=k))
inertia = ((pts - centres[assign]) ** 2).sum()
print("inertia (sum of squared distances):", round(float(inertia), 2))
print("first 30 all in same cluster:", len(np.unique(assign[:30])) == 1)
print("# Gotcha: bad starting centres can give a bad result - real k-means uses several random starts / k-means++.")
print("#   A centre with no points would become nan from .mean() on an empty slice; we keep the old centre.")
print()

# 12. Batch Matrix Operations
# ----------------------------
# - matmul (@) broadcasts over leading axes: (B, n, m) @ (B, m, p) -> (B, n, p).
# - A single (m, p) matrix broadcasts against a whole batch.
# - np.linalg.solve / inv / det also accept stacks of matrices.
# - einsum names the axes explicitly (see 12).

rng_b = np.random.default_rng(3)
A = rng_b.integers(0, 4, size=(5, 2, 3))
B = rng_b.integers(0, 4, size=(5, 3, 2))
C = A @ B
print("A, B, C shapes:", A.shape, B.shape, C.shape)
print("first product equals single matmul:", np.array_equal(C[0], A[0] @ B[0]))
Wt = np.arange(6).reshape(3, 2)
print("(5,2,3) @ (3,2) shape:", (A @ Wt).shape, "(one weight matrix shared by the batch)")
print("batch traces:", np.trace(C, axis1=1, axis2=2))
print("batch transpose shape:", C.transpose(0, 2, 1).shape, ", or np.swapaxes(C, -1, -2)")
S = np.eye(2) * 2 + C[:, :, :].astype(float) * 0.1
print("batch determinants:", np.round(np.linalg.det(S), 3))
rhs = np.ones((5, 2, 1))
sol = np.linalg.solve(S, rhs)
print("batched solve residual small:", np.allclose(S @ sol, rhs), ", sol shape:", sol.shape)
print("einsum batch trace matches:", np.array_equal(np.einsum("bii->b", C), np.trace(C, axis1=1, axis2=2)))
print("batch of row-normalised vectors:", np.round(np.linalg.norm(A.astype(float), axis=-1)[0], 3))
print("# Gotcha: np.dot on two 3-D arrays does NOT batch - it returns a bigger (N,n,N,p) array of all combinations.")
print("#   Use @ / np.matmul / einsum for batches. solve needs the rhs shaped (..., n, k) or (..., n).")
print()

# 13. datetime64 and timedelta64 Arithmetic
# ----------------------------
# - datetime64[unit] stores a point in time as an integer count of units (D, h, m, s, ...).
# - timedelta64 is the difference between two datetimes. Units must be compatible.
# - np.arange with dates gives date ranges. Subtracting gives timedelta; divide by a unit for numbers.
# - NaT = 'not a time' (the nan of dates).

d = np.datetime64("2024-02-27")
print("date:", d, ", + 3 days:", d + np.timedelta64(3, "D"), "(2024 is a leap year)")
dates = np.arange("2024-02-26", "2024-03-02", dtype="datetime64[D]")
print("date range:", dates.astype(str).tolist())
print("differences:", np.diff(dates), ", as ints:", np.diff(dates).astype(int))
span_days = np.datetime64("2024-12-25") - np.datetime64("2024-01-01")
print("days between:", span_days, ", in weeks:", span_days / np.timedelta64(1, "W"))
print("months as datetime64[M]:", np.arange("2024-01", "2024-05", dtype="datetime64[M]").astype(str).tolist())
stamp = np.datetime64("2024-03-10T14:30:00")
print("timestamp:", stamp, ", unit:", np.datetime_data(stamp.dtype))
print("truncate to day:", stamp.astype("datetime64[D]"), ", to hour:", stamp.astype("datetime64[h]"))
print("+ 90 minutes:", stamp + np.timedelta64(90, "m"))
print("year array:", dates.astype("datetime64[Y]").astype(int) + 1970)
print("month number:", (dates.astype("datetime64[M]") - dates.astype("datetime64[Y]")).astype(int) + 1)
weekday = (dates.astype("datetime64[D]").astype(int) + 3) % 7        # 1970-01-01 was a Thursday
print("weekday (Mon=0):", weekday)
print("NaT compares:", np.datetime64("NaT") == np.datetime64("NaT"), ", isnat:", np.isnat(np.datetime64("NaT")))
print("mask dates after Feb 28:", dates[dates > np.datetime64("2024-02-28")].astype(str).tolist())
print("mixed units promote to the finer one:", (np.datetime64("2024-01-01") + np.timedelta64(1, "h")).dtype)
print("# Gotcha: a day-level date + timedelta64(1, 'M') raises UFuncTypeError (a month has no fixed number of days);")
print("#   month arithmetic works only on datetime64[M] values. For anything calendar-heavy (time zones, parsing), use datetime/pandas.")
print()

# 14. Business-Day Functions
# ----------------------------
# - np.is_busday, np.busday_count, np.busday_offset treat Mon-Fri as work days by default.
# - weekmask='1111100' and holidays=[...] customise the calendar.
# - busday_offset(roll=...) says what to do when the start is not a business day.

print("is_busday for Fri 2024-03-01, Sat, Sun:", np.is_busday(np.array(["2024-03-01", "2024-03-02", "2024-03-03"], dtype="datetime64[D]")).tolist())
print("busday_count Mar 1 -> Mar 15 (end exclusive):", np.busday_count("2024-03-01", "2024-03-15"))
hol = ["2024-03-08"]
print("with a holiday on Mar 8:", np.busday_count("2024-03-01", "2024-03-15", holidays=hol))
print("5 business days after Fri Mar 1:", np.busday_offset("2024-03-01", 5))
print("Saturday + 0 with roll='forward':", np.busday_offset("2024-03-02", 0, roll="forward"), ", roll='backward':", np.busday_offset("2024-03-02", 0, roll="backward"))
try:
    np.busday_offset("2024-03-02", 0)
except ValueError as e:
    print("Saturday + 0 with roll='raise' (default) -> ValueError:", str(e)[:48])
print("Sun-Thu work week:", np.busday_count("2024-03-01", "2024-03-08", weekmask="1111001"))
all_days = np.arange("2024-03-01", "2024-03-15", dtype="datetime64[D]")
print("business days only:", all_days[np.is_busday(all_days)].astype(str).tolist())
print("# Gotcha: busday_count excludes the END date. busday_offset raises on a non-business start unless roll= is set.")
print()

# 15. Boolean-Mask Idioms
# ----------------------------
# - Combine conditions with & | ~ (NOT and/or/not) and parenthesise each comparison.
# - mask.sum() counts, mask.mean() gives a fraction, np.flatnonzero(mask) gives indexes.
# - arr[mask] = value assigns in place; np.where(mask, a, b) builds a new array.
# - Use ~np.isnan to drop missing values.

v = np.array([4.0, np.nan, -2.0, 15.0, 8.0, 0.0, 23.0])
valid = ~np.isnan(v)
print("v =", v)
print("valid count:", valid.sum(), ", fraction valid:", round(float(valid.mean()), 3))
print("positive and below 20:", v[(v > 0) & (v < 20)])
print("outside [0, 10] (nan excluded):", v[valid & ((v < 0) | (v > 10))])
print("indexes of values above 5:", np.flatnonzero(v > 5))
filled = np.where(np.isnan(v), 0.0, v)
print("fill nan with 0:", filled)
clipped = v.copy()
clipped[valid & (clipped > 10)] = 10.0
print("cap above 10 in place:", clipped)
print("count per condition:", {"neg": int((v < 0).sum()), "zero": int((v == 0).sum()), "pos": int((v > 0).sum())})
print("any/all:", (filled >= 0).any(), (filled >= 0).all(), ", first index above 10:", int(np.argmax(filled > 10)))
print("rows where any cell is nan:", np.isnan(np.array([[1, 2], [np.nan, 3], [4, 5]])).any(axis=1))
m2 = np.arange(12).reshape(3, 4)
print("rows with sum > 10:", m2[m2.sum(axis=1) > 10].tolist(), ", columns even-sum:", m2[:, m2.sum(axis=0) % 2 == 0].tolist())
print("np.select for tiers:", np.select([filled < 5, filled < 15], ["low", "mid"], default="high").tolist())
print("# Gotcha: use & | ~ with parentheses. 'v > 0 and v < 20' raises ValueError. argmax of an all-False mask")
print("#   returns 0 (looks like 'found at 0') - check mask.any() first.")
print()

# 16. Avoiding Python Loops: Patterns
# ----------------------------
# - Replace if/else per element with np.where / np.select.
# - Replace running totals with cumsum; counting with bincount; lookup with fancy indexing.
# - Replace nested loops over pairs with broadcasting (section 04).
# - Keep a loop only when each step depends on the previous result (e.g. EMA, simulations).

prices2 = np.array([100.0, 102.0, 99.0, 105.0, 110.0])
returns_loop = [(prices2[i] - prices2[i - 1]) / prices2[i - 1] for i in range(1, len(prices2))]
returns_vec = np.diff(prices2) / prices2[:-1]
print("loop vs vector returns equal:", np.allclose(returns_loop, returns_vec))
table = np.array([0.0, 0.5, 1.0, 1.5])
codes_ = np.array([3, 0, 2, 2])
print("lookup table via fancy indexing:", table[codes_])
temps = np.array([12, 25, 31, 18, 40])
print("categorise (where):", np.where(temps > 30, "hot", np.where(temps > 20, "warm", "cool")).tolist())
print("count per bucket (bincount of digitize):", np.bincount(np.digitize(temps, [20, 30]), minlength=3))
xs = np.arange(1, 6)
print("sum of i*j for i,j in 1..5 (outer):", int(np.multiply.outer(xs, xs).sum()), "vs loop:",
      sum(i * j for i in range(1, 6) for j in range(1, 6)))
print("count adjacent equal pairs:", int((np.array([1, 1, 2, 2, 2, 3])[1:] == np.array([1, 1, 2, 2, 2, 3])[:-1]).sum()))
print("accumulate until a limit: first index where cumsum > 10:", int(np.argmax(np.cumsum([3, 4, 2, 5, 1]) > 10)))
print("group-by sum via bincount:", np.bincount([0, 1, 0, 2, 1], weights=[1.0, 2.0, 3.0, 4.0, 5.0]))
print("# Gotcha: vectorising is not always faster for tiny arrays (call overhead) and uses more memory for")
print("#   big temporaries. Measure with timeit before rewriting working code.")
print()

# 17. Mini Linear Regression with lstsq
# ----------------------------
# - Model y = b0 + b1*x1 + b2*x2. Build a design matrix with a column of ones for the intercept.
# - np.linalg.lstsq(X, y) solves the least-squares problem (more stable than inv(X.T @ X)).
# - Report R^2 = 1 - SS_res / SS_tot. Compare with np.polyfit for the 1-feature case (see 10).

rng_r = np.random.default_rng(11)
n_obs = 50
x1 = rng_r.uniform(0, 10, n_obs)
x2 = rng_r.uniform(-5, 5, n_obs)
noise = rng_r.normal(0, 0.5, n_obs)
y = 3.0 + 2.0 * x1 - 1.5 * x2 + noise
Xd = np.column_stack([np.ones(n_obs), x1, x2])
coef, resid, rank, sv = np.linalg.lstsq(Xd, y, rcond=None)
print("true coefficients: [3.0, 2.0, -1.5]")
print("fitted coefficients:", np.round(coef, 3))
pred = Xd @ coef
ss_res = ((y - pred) ** 2).sum()
ss_tot = ((y - y.mean()) ** 2).sum()
print("R^2:", round(float(1 - ss_res / ss_tot), 4), ", rank:", rank)
print("residual sum of squares (lstsq):", round(float(resid[0]), 3), "vs manual:", round(float(ss_res), 3))
print("RMSE:", round(float(np.sqrt(ss_res / n_obs)), 3), "(near noise std 0.5)")
print("normal equations agree:", np.allclose(np.linalg.solve(Xd.T @ Xd, Xd.T @ y), coef))
print("predict new point (x1=4, x2=1):", round(float(np.array([1.0, 4.0, 1.0]) @ coef), 3))
slope, intercept = np.polyfit(x1, y - coef[2] * x2, 1)
print("polyfit on adjusted y gives similar slope/intercept:", round(float(slope), 3), round(float(intercept), 3))
print("standard errors:", np.round(np.sqrt(np.diag(ss_res / (n_obs - 3) * np.linalg.inv(Xd.T @ Xd))), 3))
print("# Gotcha: forget the ones column and you force the line through the origin. Highly correlated features make")
print("#   X.T @ X nearly singular - lstsq (SVD-based) copes better than inv. Always keep a held-out set to judge a model.")
print()

# 18. Cheat Sheet: Loop vs Vectorized
# ----------------------------
# - A side-by-side reference; each pair is checked for equal results below.

pairs = [
    ("sum of squares",      "sum(v*v for v in a)",                 "(a * a).sum()  or  a @ a"),
    ("normalise",           "[(v-lo)/(hi-lo) for v in a]",         "(a - a.min()) / np.ptp(a)"),
    ("conditional value",   "[x if x>0 else 0 for x in a]",        "np.where(a > 0, a, 0)  or  np.maximum(a, 0)"),
    ("count matches",       "sum(1 for x in a if x>2)",            "(a > 2).sum()"),
    ("filter",              "[x for x in a if x>2]",               "a[a > 2]"),
    ("running total",       "loop with total += x",                "np.cumsum(a)"),
    ("pairwise differences","double for-loop",                     "a[:, None] - a[None, :]"),
    ("element lookup",      "[table[i] for i in idx]",             "table[idx]"),
    ("histogram counts",    "dict counting loop",                  "np.bincount(a_int)"),
    ("row-wise function",   "[f(row) for row in M]",               "M.sum(axis=1) / np.apply_along_axis (slow)"),
    ("max index",           "max(range(n), key=a.__getitem__)",    "a.argmax()"),
    ("moving window",       "nested index loop",                   "sliding_window_view(a, w)"),
    ("dedupe",              "seen-set loop",                       "np.unique(a)"),
    ("string concat of all","'-'.join(...)",                       "keep Python / np.char.add for small cases"),
]
print(f"{'task':<22}{'python loop':<36}vectorized")
for task, loop_form, vec_form in pairs:
    print(f"{task:<22}{loop_form:<36}{vec_form}")
a_chk = np.array([3.0, -1.0, 4.0, -1.5, 5.0])
checks = {
    "sum of squares": (sum(v * v for v in a_chk), (a_chk * a_chk).sum()),
    "conditional": ([x if x > 0 else 0 for x in a_chk], np.where(a_chk > 0, a_chk, 0)),
    "count matches": (sum(1 for x in a_chk if x > 2), (a_chk > 2).sum()),
    "filter": ([x for x in a_chk if x > 2], a_chk[a_chk > 2]),
    "pairwise differences": ([[x - y for y in a_chk] for x in a_chk], a_chk[:, None] - a_chk[None, :]),
}
print("each pair gives the same answer:", all(np.allclose(l, v_) for l, v_ in checks.values()))
print("# Gotcha: the vectorized column is not a free win everywhere - rows that depend on the previous row's result")
print("#   (recursions, state machines, early exits) still want a loop, numba, or a different algorithm.")
print()

# 19. Cross-References
# ----------------------------
# - 04-Operations-And-Broadcasting: the rule behind sections 01, 02, 04.
# - 05-Statistical-And-Math-Functions: mean/std/percentile used throughout.
# - 06-Linear-Algebra: lstsq, solve, det, norm (sections 12, 17).
# - 07-Random-Module: default_rng details (sections 10, 11).
# - 08-Performance-And-Vectorization: timing and why loops are slow (section 16, 18).
# - 10-Advanced-NumPy: polyfit, select, meshgrid.
# - 11-Strides-And-Memory-Layout: sliding_window_view, views vs copies, uint8 wraparound (sections 05, 07, 09).
# - 12-Advanced-Indexing-Ufuncs-And-Sorting: bincount, einsum, unique, searchsorted.

print("Recipe habit: (1) get the shape right, (2) use axis= with keepdims=True, (3) broadcast, (4) check against a")
print("tiny loop version before trusting the fast one.")
