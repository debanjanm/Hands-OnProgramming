# 01. Creating Arrays
# 02. dtype - Explicit vs Inferred
# 03. Shape, Ndim, Size, Itemsize, Nbytes
# 04. 1D / 2D / 3D Arrays
# 05. Why NumPy Beats Python Lists

import numpy as np

# 01. Creating Arrays
# ------------------------------------
# - np.array() wraps an existing Python list/tuple into an ndarray.
# - np.arange(start, stop, step) is like range() but returns an array (and
#   accepts float steps, unlike range()).
# - np.linspace(start, stop, num) returns `num` evenly spaced points,
#   INCLUDING both endpoints by default - different from arange's "stop
#   is exclusive" behavior.
# - np.zeros/np.ones/np.full pre-allocate arrays filled with a constant.
# - np.eye(n) builds an n x n identity matrix.
# - np.empty(shape) allocates memory WITHOUT initializing it - faster than
#   zeros/ones but contains garbage values until you write to it.

print("# 01. Creating Arrays")
print("# ------------------------------------")

from_list = np.array([1, 2, 3, 4])
print("np.array([1,2,3,4])      =", from_list)

arange_arr = np.arange(0, 10, 2)
print("np.arange(0, 10, 2)      =", arange_arr, "(stop is EXCLUSIVE)")

linspace_arr = np.linspace(0, 1, 5)
print("np.linspace(0, 1, 5)     =", linspace_arr, "(stop is INCLUSIVE, 5 evenly spaced points)")

zeros_arr = np.zeros((2, 3))
print("np.zeros((2,3)):\n", zeros_arr)

ones_arr = np.ones((2, 3))
print("np.ones((2,3)):\n", ones_arr)

eye_arr = np.eye(3)
print("np.eye(3) (identity):\n", eye_arr)

full_arr = np.full((2, 2), 7)
print("np.full((2,2), 7):\n", full_arr)

empty_arr = np.empty((2, 2))
print("np.empty((2,2)) (uninitialized, garbage values):\n", empty_arr)
print("# Gotcha: np.empty is faster than zeros/ones because it skips")
print("#   initialization - only use it when you're about to overwrite every cell.")

# 02. dtype - Explicit vs Inferred
# ------------------------------------
# - Every ndarray has ONE dtype shared by all elements (unlike Python lists,
#   which can mix types freely). This uniformity is what makes NumPy fast.
# - If you don't specify dtype, NumPy infers it from the input data.
# - Mixing int and float in a literal upcasts the whole array to float.
# - .astype(dtype) returns a NEW array cast to the given dtype (does not
#   mutate the original).

print("\n# 02. dtype - Explicit vs Inferred")
print("# ------------------------------------")

inferred_int = np.array([1, 2, 3])
print("np.array([1,2,3]).dtype       =", inferred_int.dtype, "(inferred int64)")

inferred_float = np.array([1, 2.5, 3])
print("np.array([1,2.5,3]).dtype     =", inferred_float.dtype, "(one float upcasts ALL elements)")

explicit_float32 = np.array([1, 2, 3], dtype=np.float32)
print("np.array([1,2,3], dtype=np.float32).dtype =", explicit_float32.dtype)

explicit_uint8 = np.array([1, 2, 3], dtype=np.uint8)
print("np.array([1,2,3], dtype=np.uint8).dtype   =", explicit_uint8.dtype, "(0-255 range only)")

casted = inferred_float.astype(np.int32)
print("inferred_float.astype(np.int32) =", casted, "(truncates decimals, does NOT round)")
print("# Common dtypes: int8/16/32/64, uint8/16/32/64, float16/32/64, bool, complex64/128")
print("# Gotcha: casting float -> int TRUNCATES toward zero, it does not round.")

overflow_demo = np.array([250], dtype=np.uint8) + np.array([10], dtype=np.uint8)
print("uint8 250 + 10 =", overflow_demo, "(wraps around/overflows silently - no error!)")

# 03. Shape, Ndim, Size, Itemsize, Nbytes
# ------------------------------------
# - .shape: tuple giving the length along each dimension.
# - .ndim: number of dimensions (axes).
# - .size: total number of elements (product of shape).
# - .itemsize: bytes per single element (depends on dtype).
# - .nbytes: total bytes consumed by the data buffer (size * itemsize).

print("\n# 03. Shape, Ndim, Size, Itemsize, Nbytes")
print("# ------------------------------------")

matrix = np.array([[1, 2, 3], [4, 5, 6]], dtype=np.float64)
print("matrix:\n", matrix)
print("matrix.shape    =", matrix.shape, "(2 rows, 3 cols)")
print("matrix.ndim     =", matrix.ndim)
print("matrix.size     =", matrix.size, "(total elements = 2*3)")
print("matrix.itemsize =", matrix.itemsize, "bytes (float64 = 8 bytes each)")
print("matrix.nbytes   =", matrix.nbytes, "bytes (size * itemsize =", matrix.size, "*", matrix.itemsize, ")")

# 04. 1D / 2D / 3D Arrays
# ------------------------------------
# - Dimensionality is just nesting depth: 1D is a flat list, 2D is a list
#   of rows (matrix), 3D is a stack of matrices (e.g. a batch of images).

print("\n# 04. 1D / 2D / 3D Arrays")
print("# ------------------------------------")

arr_1d = np.array([1, 2, 3])
arr_2d = np.array([[1, 2, 3], [4, 5, 6]])
arr_3d = np.array([[[1, 2], [3, 4]], [[5, 6], [7, 8]]])

print("1D shape", arr_1d.shape, "ndim", arr_1d.ndim, "->", arr_1d)
print("2D shape", arr_2d.shape, "ndim", arr_2d.ndim, "->\n", arr_2d)
print("3D shape", arr_3d.shape, "ndim", arr_3d.ndim, "->\n", arr_3d)
print("# Common uses: 1D = single feature/timeseries, 2D = table/matrix/grayscale image,")
print("#   3D = batch of matrices, RGB image (H, W, channels), or a stack of 2D data.")

# 05. Why NumPy Beats Python Lists
# ------------------------------------
# - A Python list stores POINTERS to separately-allocated PyObject ints/floats
#   scattered around memory - lots of overhead per element and poor cache
#   locality.
# - A NumPy array stores raw bytes of a SINGLE dtype in one CONTIGUOUS block -
#   no per-element object overhead, and operations run in compiled C loops
#   (vectorization) instead of the Python bytecode interpreter looping
#   element by element.

print("\n# 05. Why NumPy Beats Python Lists")
print("# ------------------------------------")

import sys
import time

python_list = list(range(1000))
numpy_array = np.arange(1000)

# sys.getsizeof() on a list only counts the pointer array, not the ints
# themselves - so the REAL gap is even bigger than this number shows.
list_shallow_bytes = sys.getsizeof(python_list)
array_bytes = numpy_array.nbytes
print("sys.getsizeof(list of 1000 ints)     =", list_shallow_bytes, "bytes (pointers only, ints stored elsewhere)")
print("numpy_array.nbytes (1000 int64s)     =", array_bytes, "bytes (actual data, tightly packed)")

single_python_int = sys.getsizeof(10**6)
print("sys.getsizeof(a single Python int)   =", single_python_int, "bytes (vs 8 bytes for one int64 in NumPy)")

# Timing: elementwise square of 1,000,000 numbers.
n = 1_000_000
big_list = list(range(n))
big_array = np.arange(n)

start = time.perf_counter()
squared_list = [x * x for x in big_list]
list_time = time.perf_counter() - start

start = time.perf_counter()
squared_array = big_array ** 2
array_time = time.perf_counter() - start

print(f"\nSquaring {n:,} numbers:")
print(f"  Python list comprehension: {list_time:.5f} sec")
print(f"  NumPy vectorized (**2)   : {array_time:.5f} sec")
print(f"  NumPy speedup            : ~{list_time / array_time:.1f}x faster")
print("# Why: fixed dtype -> no per-element type checks; contiguous memory ->")
print("#   CPU cache friendly; vectorized C loops -> no Python interpreter overhead per element.")

print("\n# End of Array Basics")
