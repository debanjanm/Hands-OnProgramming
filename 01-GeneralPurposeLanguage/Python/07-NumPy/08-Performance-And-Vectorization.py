# 01. Timed Comparison - Python Loop vs Vectorized NumPy
# 02. Why Vectorization Is Faster
# 03. Memory Layout - C-order vs Fortran-order
# 04. Strides - How an Array Is Actually Laid Out in Memory
# 05. Views vs Copies - Performance Implications

import time
import numpy as np

# 01. Timed Comparison - Python Loop vs Vectorized NumPy
# ------------------------------------
# - Same computation (squaring a million numbers) done two ways:
#   a plain Python for-loop, and a vectorized NumPy operation.
# - time.perf_counter() gives a high-resolution timer suitable for benchmarking.

print("# 01. Timed Comparison - Python Loop vs Vectorized NumPy")
print("# ------------------------------------")

N = 1_000_000
python_list = list(range(N))
numpy_array = np.arange(N)

start = time.perf_counter()
squared_loop = [x * x for x in python_list]
loop_time = time.perf_counter() - start

start = time.perf_counter()
squared_vectorized = numpy_array ** 2
vector_time = time.perf_counter() - start

print(f"Python for-loop (list comprehension): {loop_time:.4f} sec")
print(f"NumPy vectorized (array ** 2):        {vector_time:.4f} sec")
print(f"Speedup: {loop_time / vector_time:.1f}x faster with vectorization")
print("# Exact numbers vary by machine, but vectorized is reliably an order of magnitude faster.")

# 02. Why Vectorization Is Faster
# ------------------------------------
# - Python for-loop: each iteration goes through the Python interpreter -
#   bytecode dispatch, type checks, and a new Python int OBJECT allocated
#   for every single result (Python ints are full objects, not raw machine ints).
# - NumPy vectorized op: the loop runs in pre-compiled C code over a flat,
#   contiguous block of raw machine numbers (no per-element Python object
#   overhead) - and can use SIMD (Single Instruction, Multiple Data) CPU
#   instructions to process several elements per CPU cycle.

print("\n# 02. Why Vectorization Is Faster")
print("# ------------------------------------")
print("# - Python loop: interpreter overhead + a new Python object per element.")
print("# - NumPy op: single call into a C loop over raw contiguous memory.")
print("# - Modern CPUs use SIMD to operate on multiple array elements per instruction.")
print("# - Net effect: less interpreter overhead + hardware-level parallelism.")

# 03. Memory Layout - C-order vs Fortran-order
# ------------------------------------
# - order='C' (default): row-major - elements of the SAME ROW are contiguous
#   in memory (last axis varies fastest). Matches C language convention.
# - order='F': column-major - elements of the SAME COLUMN are contiguous
#   (first axis varies fastest). Matches Fortran/MATLAB convention.
# - Choice affects performance: iterating along the contiguous axis is faster
#   (better CPU cache usage) than iterating across it.

print("\n# 03. Memory Layout - C-order vs Fortran-order")
print("# ------------------------------------")

arr_c = np.array([[1, 2, 3], [4, 5, 6]], order='C')
arr_f = np.array([[1, 2, 3], [4, 5, 6]], order='F')

print("arr_c (order='C'):\n", arr_c)
print("arr_c.flags['C_CONTIGUOUS'] =", arr_c.flags['C_CONTIGUOUS'])
print("arr_c.flags['F_CONTIGUOUS'] =", arr_c.flags['F_CONTIGUOUS'])

print("\narr_f (order='F'):\n", arr_f)
print("arr_f.flags['C_CONTIGUOUS'] =", arr_f.flags['C_CONTIGUOUS'])
print("arr_f.flags['F_CONTIGUOUS'] =", arr_f.flags['F_CONTIGUOUS'])
print("# Same logical values/shape, different physical memory layout.")

# 04. Strides - How an Array Is Actually Laid Out in Memory
# ------------------------------------
# - .strides is a tuple: the number of BYTES to step in memory to move one
#   index along each axis. It reveals the real physical layout behind the
#   logical shape.

print("\n# 04. Strides - How an Array Is Actually Laid Out in Memory")
print("# ------------------------------------")

print("arr_c.shape =", arr_c.shape, ", arr_c.strides =", arr_c.strides,
      "(itemsize", arr_c.itemsize, "bytes)")
print("# C-order (2,3) int64 array: step 24 bytes (3 items) to next row, 8 bytes to next column")
print("#   -> row elements ARE adjacent in memory (row-major).")

print("\narr_f.shape =", arr_f.shape, ", arr_f.strides =", arr_f.strides)
print("# F-order: step 8 bytes to next row, 16 bytes (2 items) to next column")
print("#   -> column elements ARE adjacent in memory (column-major).")

# 05. Views vs Copies - Performance Implications
# ------------------------------------
# - Slicing a NumPy array returns a VIEW - shares the same underlying memory,
#   created instantly, costs (almost) nothing.
# - Operations that reshape non-contiguous data, use fancy/boolean indexing,
#   or explicit .copy() allocate NEW memory and copy every element - costs
#   time proportional to array size, plus doubles memory use temporarily.

print("\n# 05. Views vs Copies - Performance Implications")
print("# ------------------------------------")

big = np.arange(10_000_000)

start = time.perf_counter()
view = big[::2]           # view: no data copied, just a different stride
view_time = time.perf_counter() - start

start = time.perf_counter()
copy = big[::2].copy()    # forces an actual copy of the sliced data
copy_time = time.perf_counter() - start

print(f"Creating a view (big[::2]):        {view_time:.6f} sec (near-instant, no data moved)")
print(f"Creating a copy (big[::2].copy()): {copy_time:.6f} sec (allocates + copies data)")
print("view.base is big:", view.base is big, "(view shares memory with original)")
print("copy.base is None:", copy.base is None, "(copy owns independent memory)")
print("# Rule of thumb: basic slicing = view (free). Fancy indexing/boolean masks/.copy() = copy (costs).")

print("\n# End of Performance and Vectorization Explanation")
