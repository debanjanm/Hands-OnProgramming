# 01. np.save / np.load - Single Array (.npy binary format)
# 02. np.savez / np.savez_compressed - Multiple Named Arrays (.npz)
# 03. np.savetxt / np.loadtxt - Human-Readable Text Output
# 04. np.memmap - Memory-Mapped Arrays for Files Too Large for RAM
# 05. Cleanup

import numpy as np
import os

# 01. np.save / np.load - Single Array (.npy binary format)
# ------------------------------------
# - np.save() writes ONE array to a binary ".npy" file - preserves dtype,
#   shape, and exact values (no precision loss, unlike text formats).
# - np.load() reads it back as an identical array.
# - Fast and compact - the default choice for saving intermediate NumPy results.

print("# 01. np.save / np.load - Single Array (.npy binary format)")
print("# ------------------------------------")

original = np.array([[1.5, 2.5, 3.5], [4.5, 5.5, 6.5]])
np.save("temp_array.npy", original)
print("Saved original array to temp_array.npy:\n", original)

loaded = np.load("temp_array.npy")
print("Loaded back:\n", loaded)
print("Arrays equal:", np.array_equal(original, loaded))
print("dtype preserved:", loaded.dtype)

# 02. np.savez / np.savez_compressed - Multiple Named Arrays (.npz)
# ------------------------------------
# - np.savez() bundles SEVERAL arrays into one ".npz" file, each given a name
#   (like a dict). Load it back and access each array by that name.
# - np.savez_compressed() does the same but applies zip compression - smaller
#   file, slower save/load. Use for large arrays with lots of repeated values.

print("\n# 02. np.savez / np.savez_compressed - Multiple Named Arrays (.npz)")
print("# ------------------------------------")

weights = np.array([0.1, 0.2, 0.3])
biases = np.array([1.0, 2.0])
np.savez("temp_bundle.npz", weights=weights, biases=biases)
print("Saved weights + biases to temp_bundle.npz")

bundle = np.load("temp_bundle.npz")
print("Keys in bundle:", list(bundle.keys()))
print("bundle['weights'] =", bundle["weights"])
print("bundle['biases']  =", bundle["biases"])

np.savez_compressed("temp_bundle_compressed.npz", weights=weights, biases=biases)
uncompressed_size = os.path.getsize("temp_bundle.npz")
compressed_size = os.path.getsize("temp_bundle_compressed.npz")
print(f"\nUncompressed .npz size: {uncompressed_size} bytes")
print(f"Compressed .npz size:   {compressed_size} bytes")
print("# For small arrays like these, compression overhead can make the file LARGER -")
print("#   it pays off on big, repetitive arrays, not tiny demo ones.")

# 03. np.savetxt / np.loadtxt - Human-Readable Text Output
# ------------------------------------
# - np.savetxt() writes an array as plain text (CSV-like) - readable in any
#   text editor or spreadsheet, but loses exact float precision and dtype
#   info unless you're careful with format strings.
# - delimiter= controls the column separator; header= adds a comment line.
# - np.loadtxt() reads it back (always as floats, unless dtype specified).

print("\n# 03. np.savetxt / np.loadtxt - Human-Readable Text Output")
print("# ------------------------------------")

table = np.array([[1, 85.5, 90.0], [2, 72.3, 88.1], [3, 91.0, 76.4]])
np.savetxt("temp_scores.csv", table, delimiter=",", header="id,test1,test2", comments="")
print("Saved table to temp_scores.csv:\n", table)

with open("temp_scores.csv") as f:
    print("\nRaw file contents:")
    print(f.read())

reloaded_table = np.loadtxt("temp_scores.csv", delimiter=",", skiprows=1)
print("Reloaded from text (all floats now):\n", reloaded_table)
print("# Note: loadtxt has no concept of an int column - everything comes back as float64.")

# 04. np.memmap - Memory-Mapped Arrays for Files Too Large for RAM
# ------------------------------------
# - A memmap array is backed by a file on disk, not loaded fully into RAM -
#   NumPy reads/writes only the slices you actually touch, on demand.
# - Lets you work with arrays far bigger than available memory (e.g. a
#   100GB dataset on an 8GB-RAM machine), at the cost of disk I/O speed
#   for each access instead of RAM speed.
# - mode='w+' creates/overwrites; mode='r' opens read-only; dtype and shape
#   must be specified explicitly (the file has no header describing them).

print("\n# 04. np.memmap - Memory-Mapped Arrays for Files Too Large for RAM")
print("# ------------------------------------")

mm_shape = (1000, 1000)
mm = np.memmap("temp_bigarray.dat", dtype="float64", mode="w+", shape=mm_shape)
mm[0, 0] = 42.0
mm[999, 999] = -1.0
mm.flush()  # ensure writes are pushed to disk
print(f"Created memmap array, shape={mm_shape}, on-disk size ~ "
      f"{os.path.getsize('temp_bigarray.dat') / 1e6:.1f} MB")
print("mm[0, 0] =", mm[0, 0], ", mm[999, 999] =", mm[999, 999])
del mm  # close the memmap (flushes and releases the file handle)

mm_reopened = np.memmap("temp_bigarray.dat", dtype="float64", mode="r", shape=mm_shape)
print("Reopened read-only: mm_reopened[0, 0] =", mm_reopened[0, 0],
      ", mm_reopened[999, 999] =", mm_reopened[999, 999])
del mm_reopened

# 05. Cleanup
# ------------------------------------
print("\n# 05. Cleanup")
for fname in ("temp_array.npy", "temp_bundle.npz", "temp_bundle_compressed.npz",
              "temp_scores.csv", "temp_bigarray.dat"):
    os.remove(fname)
print("temp files removed")

print("\n# End of File I/O Explanation")
