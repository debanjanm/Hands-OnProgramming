# 01. category dtype Basics
# 02. Ordered Categoricals
# 03. The .cat Accessor
# 04. add / remove / rename / reorder Categories
# 05. Memory Saving With category
# 06. groupby With Categoricals - The observed Gotcha
# 07. Nullable Integers (Int64) vs NaN in int Columns
# 08. Float64, boolean and Other Nullable Types
# 09. string dtype vs object
# 10. pd.NA Semantics and Three-Valued Logic
# 11. convert_dtypes
# 12. pd.to_numeric and errors=
# 13. Downcasting to Save Memory
# 14. memory_usage(deep=True)
# 15. Sparse Data Basics
# 16. pyarrow-Backed Dtypes (Optional)
# 17. Dtype Pitfalls With NaN, Mixed Types and astype
# 18. Copy-on-Write and SettingWithCopy
#
# See also: 03-Data-Cleaning (missing values), 04-Data-Transformation (astype basics),
# 10-Performance-And-Best-Practices (memory tips), 09-Input-Output (dtype= when reading).

import warnings

import numpy as np
import pandas as pd

rng = np.random.default_rng(7)

# 01. category dtype Basics
# ----------------------------
# - category stores each unique value ONCE (.categories) and each row as a
#   small integer code (.codes). Great for columns with few repeated values.
# - Create with astype("category") or pd.Categorical(...).
# - Missing values get code -1 and show as NaN; they are never a category.
# - Comparison/sorting follows category ORDER, not alphabet (see section 2).

colors = pd.Series(["red", "blue", "red", "green", "blue", "red", None])
cat = colors.astype("category")
print("dtype:", cat.dtype)
print("categories (sorted by default):", list(cat.cat.categories))
print("codes:", cat.cat.codes.tolist(), " (-1 means missing)")
print("value_counts:\n", cat.value_counts(), sep="")
print("Setting a value not in categories:")
try:
    cat.iloc[0] = "purple"
except TypeError as e:
    print("  TypeError:", str(e)[:60])

# 02. Ordered Categoricals
# ----------------------------
# - Give a fixed order with CategoricalDtype(categories=[...], ordered=True).
# - Then <, >, min, max, sort_values all follow that order.
# - Unordered categoricals refuse < and > (TypeError), and min/max fail.
# - Values not in the list become NaN: a handy way to catch typos.

size_type = pd.CategoricalDtype(["small", "medium", "large"], ordered=True)
sizes = pd.Series(["medium", "small", "large", "small", "huge"], dtype=size_type)
print("Series ('huge' is not allowed -> NaN):", sizes.tolist())
print("sizes > 'small':", (sizes > "small").tolist())
print("max:", sizes.max(), " min:", sizes.min())
print("sort_values:", sizes.sort_values().tolist())
try:
    cat.max()
except TypeError as e:
    print("unordered max ->", type(e).__name__)

# 03. The .cat Accessor
# -------------------------
# - s.cat.categories, .codes, .ordered - read the structure.
# - s.cat.as_ordered() / as_unordered() flip the flag.
# - s.cat.set_categories(new_list) forces exactly this list (adds unused
#   ones, turns values not in the list into NaN).
# - Many string operations need .astype(str) or .cat.rename_categories.

print("ordered?", sizes.cat.ordered, "| as_unordered ->", sizes.cat.as_unordered().cat.ordered)
print("codes:", sizes.cat.codes.tolist())
print("set_categories(['small','large']):", sizes.cat.set_categories(["small", "large"]).tolist())
print("unused categories still count with value_counts():")
print(sizes.value_counts(), sep="")

# 04. add / remove / rename / reorder Categories
# ----------------------------------------------------
# - add_categories(["x"])   : allow new labels (no row changes).
# - remove_categories(["x"]): rows with x become NaN.
# - remove_unused_categories(): drop labels no row uses.
# - rename_categories(list or dict): change label text, order stays.
# - reorder_categories(new_order, ordered=True): same labels, new order.
# - These return new Series; use the .cat accessor, not assignment to .categories.

s = pd.Series(["b", "a", "c", "a"], dtype="category")
s2 = s.cat.add_categories(["d"])
print("add d -> categories:", list(s2.cat.categories))
print("remove 'a' ->", s.cat.remove_categories(["a"]).tolist())
print("remove_unused_categories on s2:", list(s2.cat.remove_unused_categories().cat.categories))
print("rename dict:", s.cat.rename_categories({"a": "A", "b": "B"}).tolist())
print("reorder ordered=True, max:", s.cat.reorder_categories(["c", "b", "a"], ordered=True).max())

# 05. Memory Saving With category
# ------------------------------------
# - A column with 100,000 rows but only 4 unique strings stores 100,000
#   small integers instead of 100,000 Python string objects.
# - Use memory_usage(deep=True): without deep=True object columns are
#   under-counted (it counts pointers, not the strings).
# - Worth it when unique values are far fewer than rows; with mostly
#   unique values category can be BIGGER than object.

n = 100_000
labels = np.array(["North", "South", "East", "West"])
big_obj = pd.Series(labels[rng.integers(0, 4, n)])
big_cat = big_obj.astype("category")
print("object  deep bytes:", big_obj.memory_usage(deep=True))
print("category deep bytes:", big_cat.memory_usage(deep=True))
print("saving factor > 10x:", big_obj.memory_usage(deep=True) / big_cat.memory_usage(deep=True) > 10)

uniq = pd.Series([f"id_{i}" for i in range(2000)])
print("All-unique column: category bigger than object?",
      uniq.astype("category").memory_usage(deep=True) > uniq.memory_usage(deep=True))

# 06. groupby With Categoricals - The observed Gotcha
# ---------------------------------------------------------
# - Grouping by a categorical column with observed=False (the old
#   default) returns a row for EVERY category, even unused ones (sum 0,
#   mean NaN). That can be surprising and slow with many categories.
# - observed=True returns only categories that appear in the data.
# - In pandas 2.2 not passing observed gives a FutureWarning, so always
#   write observed= explicitly. pandas 3 will default to True.
# - With several categorical keys, observed=False builds the FULL product.

lvl = pd.Categorical(["low", "high", "low"], categories=["low", "mid", "high"], ordered=True)
d = pd.DataFrame({"level": lvl, "x": [1, 2, 3]})
print("observed=False:\n", d.groupby("level", observed=False)["x"].sum(), sep="")
print("\nobserved=True:\n", d.groupby("level", observed=True)["x"].sum(), sep="")
print("\nmean with observed=False gives NaN for 'mid':", d.groupby("level", observed=False)["x"].mean().tolist())

# 07. Nullable Integers (Int64) vs NaN in int Columns
# --------------------------------------------------------
# - NumPy int64 has no missing value, so one NaN turns a column to float64.
# - Capital-I "Int64" (also Int8/16/32, UInt8...) is pandas' nullable int:
#   it keeps whole numbers and uses pd.NA for missing.
# - Good for IDs, counts, years: no "5.0" surprises, no precision loss
#   for big ints (float64 loses exactness above 2**53).

print("pd.Series([1, 2, None]).dtype ->", pd.Series([1, 2, None]).dtype)
ni = pd.Series([1, 2, None], dtype="Int64")
print("with dtype='Int64':", ni.tolist(), ni.dtype)
print("isna:", ni.isna().tolist(), " sum:", ni.sum(), " mean:", ni.mean())
print("arithmetic keeps NA:", (ni + 1).tolist())
big = 2**53 + 1
print("float64 keeps 2**53+1 exact?", int(np.float64(big)) == big, "| Int64 keeps it exact?", int(pd.Series([big], dtype="Int64")[0]) == big)

# 08. Float64, boolean and Other Nullable Types
# ---------------------------------------------------
# - "Float64", "boolean" (lowercase b), "string", "Int64", "UInt8" ... all
#   use pd.NA as the missing marker and keep their own type.
# - numpy bool has no missing value: [True, None] becomes object dtype.
# - "boolean" supports NA. Using it directly as a row filter raises if it
#   contains NA, so fillna(False) first (decide what unknown means).

nf = pd.Series([1.5, None, 3.0], dtype="Float64")
print("Float64:", nf.tolist(), "| NaN float vs NA:", pd.Series([1.5, np.nan]).isna().tolist())
nb = pd.Series([True, None, False], dtype="boolean")
print("boolean:", nb.tolist(), nb.dtype)
print("object when numpy bool meets None:", pd.Series([True, None, False]).dtype)
df = pd.DataFrame({"v": [1, 2, 3], "flag": nb})
try:
    df[df["flag"]]
except ValueError as e:
    print("mask with NA raises ->", type(e).__name__)
print("fillna(False) then filter:\n", df[df["flag"].fillna(False)], sep="")

# 09. string dtype vs object
# -------------------------------
# - dtype object holds ANY Python objects; strings in it are just one case.
#   Mixed content (str + int) hides in object columns silently.
# - dtype "string" holds ONLY strings (+ pd.NA). Safer: assigning a number
#   fails or converts, and .str methods work cleanly.
# - Results of comparisons on "string" are nullable "boolean", not object.
# - Both have .str; "string" is the clearer choice for text columns.

o = pd.Series(["a", "b", 3, None])
print("object column with mixed types:", [type(x).__name__ for x in o])
st = pd.Series(["apple", "kiwi", None], dtype="string")
print("string dtype:", st.dtype, "| str.len:", st.str.len().tolist(), st.str.len().dtype)
print("comparison result dtype:", (st == "kiwi").dtype, (st == "kiwi").tolist())
print("str.upper:", st.str.upper().tolist())
print("object vs string on missing:", pd.Series(["a", None]).isna().tolist(), pd.Series(["a", None], dtype="string").isna().tolist())

# 10. pd.NA Semantics and Three-Valued Logic
# -------------------------------------------------
# - pd.NA means "unknown value". Most operations with it give NA.
# - pd.NA == pd.NA is NA (not True!). Use pd.isna(x) to test.
# - bool(pd.NA) raises TypeError: you cannot use it in `if`.
# - Kleene logic: True | NA = True (answer known anyway),
#   False & NA = False, but True & NA = NA, False | NA = NA.
# - np.nan != np.nan (False) but NaN==NaN is plain False; NA is more honest.

print("pd.NA + 1:", pd.NA + 1, "| pd.NA == pd.NA:", pd.NA == pd.NA, "| pd.isna(pd.NA):", pd.isna(pd.NA))
print("np.nan == np.nan:", np.nan == np.nan)
try:
    bool(pd.NA)
except TypeError as e:
    print("bool(pd.NA) ->", type(e).__name__)
print("True  | NA :", True | pd.NA)
print("False & NA :", False & pd.NA)
print("True  & NA :", True & pd.NA)
print("False | NA :", False | pd.NA)
print("pd.NA ** 0 :", pd.NA ** 0, "(anything to power 0 is 1, so known)")
k = pd.Series([True, False, None], dtype="boolean")
print("Series | True:", (k | True).tolist(), "  Series & True:", (k & True).tolist())
print("sum skips NA by default:", pd.Series([1, None], dtype="Int64").sum(), "| skipna=False:", pd.Series([1, None], dtype="Int64").sum(skipna=False))

# 11. convert_dtypes
# ----------------------
# - df.convert_dtypes() guesses the best NULLABLE dtype per column:
#   float with all whole numbers -> Int64, object text -> string,
#   bool -> boolean.
# - Great after read_csv or after cleaning, when dtypes are loose.
# - Options: convert_integer=False, convert_string=False etc. to opt out.
# - Does not touch category or datetime columns.

raw = pd.DataFrame({
    "id": [1.0, 2.0, np.nan],
    "name": ["a", "b", None],
    "ok": [True, False, True],
    "score": [1.5, 2.5, 3.5],
})
print("before:", raw.dtypes.astype(str).to_dict())
conv = raw.convert_dtypes()
print("after: ", conv.dtypes.astype(str).to_dict())
print("id column now:", conv["id"].tolist())

# 12. pd.to_numeric and errors=
# ------------------------------------
# - pd.to_numeric(s) converts text to numbers.
# - errors="raise" (default): stop on first bad value.
# - errors="coerce": bad values become NaN. Best for cleaning dirty data.
# - errors="ignore" is deprecated in 2.2: it is NOT used here.
# - downcast="integer"/"float"/"unsigned" picks the smallest dtype that fits.
# - dtype_backend="numpy_nullable" returns Int64/Float64 instead.
# - Thousands commas or currency signs must be cleaned first (str.replace).

dirty = pd.Series(["10", "20", "x", "40", "1,000"])
try:
    pd.to_numeric(dirty)
except ValueError as e:
    print("errors='raise' ->", type(e).__name__)
print("coerce:", pd.to_numeric(dirty, errors="coerce").tolist())
clean = pd.to_numeric(dirty.str.replace(",", "", regex=False), errors="coerce")
print("clean commas first:", clean.tolist())
print("nullable backend:", pd.to_numeric(dirty.str.replace(",", "", regex=False), errors="coerce", dtype_backend="numpy_nullable").dtype)
print("downcast:", pd.to_numeric(pd.Series(["1", "2", "3"]), downcast="integer").dtype)

# 13. Downcasting to Save Memory
# -------------------------------------
# - int64 uses 8 bytes per value. int8 uses 1 (range -128..127), int16 2,
#   int32 4. float32 halves float64 but loses precision (~7 digits).
# - Use pd.to_numeric(..., downcast=...) or astype with a chosen type.
# - GOTCHA: astype("int8") on a too-big value silently WRAPS around in
#   NumPy. Check min/max first, or let to_numeric(downcast) pick safely.
# - Math on small ints can overflow too (int8 100 + 100 = -56).

nums = pd.Series(rng.integers(0, 100, 10_000))
small = pd.to_numeric(nums, downcast="unsigned")
print("dtype:", nums.dtype, "->", small.dtype)
print("bytes:", nums.memory_usage(index=False), "->", small.memory_usage(index=False))
wrapped = pd.Series([100, 200, 300]).astype("int8")
print("astype('int8') wraps silently:", wrapped.tolist())
print("int8 overflow in math:", (pd.Series([100], dtype="int8") + pd.Series([100], dtype="int8")).tolist())
f64 = pd.Series([0.1 + 0.2])
print("float32 loses digits:", f64.iloc[0], "->", float(f64.astype("float32").iloc[0]))

# 14. memory_usage(deep=True)
# ---------------------------------
# - df.memory_usage() counts only the array itself: object columns show
#   8 bytes per row (pointers), hiding the real size of the strings.
# - deep=True inspects every Python object. Slower, but the truth.
# - index=False skips the index cost. df.info(memory_usage="deep") prints
#   the total.

people = pd.DataFrame({
    "city": rng.choice(["Mumbai", "Delhi", "Chennai"], 5000),
    "age": rng.integers(18, 80, 5000),
})
print("shallow:", people.memory_usage(index=False).to_dict())
print("deep:   ", people.memory_usage(index=False, deep=True).to_dict())
optim = people.astype({"city": "category", "age": "uint8"})
print("optimised deep total:", optim.memory_usage(index=False, deep=True).sum(),
      "vs original:", people.memory_usage(index=False, deep=True).sum())

# 15. Sparse Data Basics
# ----------------------------
# - Sparse dtype stores only the NON-fill values (fill is 0 or NaN) plus
#   their positions. Useful for mostly-empty data: one-hot columns,
#   huge indicator matrices.
# - Create with dtype=pd.SparseDtype("float", 0) or pd.arrays.SparseArray.
# - .sparse.density tells the fraction actually stored.
# - Not worth it for dense data: overhead can make it larger and slower.

dense = pd.Series(np.zeros(10_000))
dense.iloc[[5, 500, 9000]] = 1.0
sp = dense.astype(pd.SparseDtype("float64", 0.0))
print("dtype:", sp.dtype, "| density:", round(sp.sparse.density, 4), "| stored points:", sp.sparse.npoints)
print("bytes dense -> sparse:", dense.memory_usage(index=False), "->", sp.memory_usage(index=False))
print("sum identical:", dense.sum() == sp.sum())
print("get_dummies sparse:", pd.get_dummies(pd.Series(list("abca")), sparse=True, dtype=int).dtypes.astype(str).tolist())

# 16. pyarrow-Backed Dtypes (Optional)
# ------------------------------------------
# - If the pyarrow library is installed, dtypes like "int64[pyarrow]",
#   "string[pyarrow]", "double[pyarrow]" are available. They have native
#   NA support, faster string ops and smaller memory for text.
# - read_csv(dtype_backend="pyarrow") builds a whole frame this way.
# - It is optional: guard the import so code works without it.

try:
    import pyarrow as pa  # noqa: F401
    HAVE_ARROW = True
except ImportError:
    HAVE_ARROW = False
print("pyarrow importable:", HAVE_ARROW)
if HAVE_ARROW:
    ai = pd.Series([1, 2, None], dtype="int64[pyarrow]")
    print("int64[pyarrow]:", ai.tolist(), ai.dtype)
    ast = pd.Series(["x", "yy", None], dtype="string[pyarrow]")
    print("string[pyarrow] str.len:", ast.str.len().tolist())
    conv_arrow = raw.convert_dtypes(dtype_backend="pyarrow")
    print("convert_dtypes(dtype_backend='pyarrow'):", conv_arrow.dtypes.astype(str).to_dict())
else:
    print("pyarrow not installed: skipped, nullable numpy dtypes above cover the same ideas.")

# 17. Dtype Pitfalls With NaN, Mixed Types and astype
# ---------------------------------------------------------
# - An int column plus one NaN becomes float64 (see section 7).
# - astype(int) on a column with NaN raises IntCastingNaNError (a
#   ValueError). Use "Int64" instead.
# - A bool column plus a missing value becomes object.
# - object columns can hide numbers stored as text ("5" + "5" = "55").
# - Reindexing/merge that introduces missing rows silently turns ints into
#   floats: check dtypes after merges.
# - astype(str) turns NaN into the text "nan" (a real string!); use the
#   "string" dtype to keep the missing value.

try:
    pd.Series([1.0, np.nan]).astype(int)
except ValueError as e:
    print("astype(int) with NaN ->", type(e).__name__)
print("astype('Int64') works:", pd.Series([1.0, np.nan]).astype("Int64").tolist())
txt = pd.Series(["5", "5"])
print("text + text:", (txt + txt).tolist(), "| after to_numeric:", (pd.to_numeric(txt) * 2).tolist())
print("astype(str) on NaN:", pd.Series([1.5, np.nan]).astype(str).tolist())
print("astype('string') on NaN:", pd.Series([1.5, np.nan]).astype("string").tolist())
left = pd.DataFrame({"k": [1, 2, 3]})
right = pd.DataFrame({"k": [1, 2], "v": [10, 20]})
merged = left.merge(right, on="k", how="left")
print("merge introduced NaN -> v dtype:", merged["v"].dtype)
print("select_dtypes(include='number'):", list(merged.select_dtypes(include="number").columns))

# 18. Copy-on-Write and SettingWithCopy
# -------------------------------------------
# - In pandas 2.2 default mode, slices can be views OR copies, and writing
#   to a slice may or may not change the original. pandas tries to warn
#   with SettingWithCopyWarning, but not always.
# - Chained assignment df[mask]["col"] = v writes into a temporary copy:
#   the original is NOT changed. Use df.loc[mask, "col"] = v instead.
# - Copy-on-Write (pd.options.mode.copy_on_write = True) makes the rules
#   simple: every derived object behaves like a copy, so writing to a
#   slice never changes the parent. It becomes the only mode in pandas 3.
# - If you want an independent frame, say so: df2 = df[...].copy().
# - Under CoW, chained assignment never works, and pandas warns.

def run_collect(fn):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        fn()
    return sorted({x.category.__name__ for x in w})

base = pd.DataFrame({"a": [1, 2, 3, 4], "b": [10, 20, 30, 40]})

def chained():
    x = base.copy()
    x[x["a"] > 2]["b"] = 0
    print("chained assignment changed original?", x["b"].tolist())

print("warnings from chained assignment:", run_collect(chained))

def slice_then_set():
    x = base.copy()
    part = x[x["a"] > 2]
    part["b"] = 0
    print("slice-then-set: original unchanged:", x["b"].tolist(), "| part:", part["b"].tolist())

print("warnings from slice-then-set:", run_collect(slice_then_set))

fixed = base.copy()
fixed.loc[fixed["a"] > 2, "b"] = 0
print("loc fix:", fixed["b"].tolist())

with pd.option_context("mode.copy_on_write", True):
    cow = base.copy()
    view = cow["b"]
    view.iloc[0] = 999
    print("CoW on: parent after writing to extracted column:", cow["b"].tolist())
print("CoW option now (restored):", pd.options.mode.copy_on_write)

print("\n# End of Dtypes, Categorical and Nullable")
