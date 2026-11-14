# 01. Structured Arrays - Arrays of Records
# 02. Masked Arrays - numpy.ma
# 03. np.meshgrid - Coordinate Grids
# 04. np.polyfit / np.poly1d - Fitting a Polynomial
# 05. np.select - Multi-Condition Vectorized Selection

import numpy as np
import numpy.ma as ma

# 01. Structured Arrays - Arrays of Records
# ------------------------------------
# - A structured array is a single NumPy array where each element is a
#   "record" with named, typed fields - like a lightweight table or an
#   array of C structs. dtype defines the fields: ('name', type_string).
# - 'U10' = unicode string up to 10 chars, 'i4' = 4-byte (32-bit) int.
# - Access a field across ALL rows at once with array['field_name'].

print("# 01. Structured Arrays - Arrays of Records")
print("# ------------------------------------")

person_dtype = np.dtype([('name', 'U10'), ('age', 'i4')])
people = np.array([('Alice', 30), ('Bob', 25), ('Carol', 35)], dtype=person_dtype)

print("people =\n", people)
print("people['name'] =", people['name'])
print("people['age']  =", people['age'])
print("people[1] (single record) =", people[1], ", people[1]['name'] =", people[1]['name'])
print("Average age:", people['age'].mean())

# Boolean filtering works just like a regular array, but on a field.
over_28 = people[people['age'] > 28]
print("People over 28:\n", over_28)

# 02. Masked Arrays - numpy.ma
# ------------------------------------
# - A masked array pairs data with a boolean mask marking some values as
#   INVALID/MISSING. Masked positions are excluded from computations
#   (mean, sum, etc.) automatically - no need to manually filter NaNs.
# - ma.masked_array(data, mask=...) or ma.masked_where(condition, data).

print("\n# 02. Masked Arrays - numpy.ma")
print("# ------------------------------------")

readings = np.array([23.5, -999.0, 25.1, -999.0, 22.8])  # -999 = sensor error sentinel
masked_readings = ma.masked_where(readings == -999.0, readings)

print("readings (raw, -999 = bad sensor value) =", readings)
print("masked_readings =", masked_readings)
print("Plain np.mean (WRONG - includes -999 sentinels):", readings.mean())
print("Masked mean (correct - skips masked values):", masked_readings.mean())
print("masked_readings.mask =", masked_readings.mask)
print("masked_readings.compressed() (just the valid values) =", masked_readings.compressed())

# 03. np.meshgrid - Coordinate Grids
# ------------------------------------
# - Given 1D arrays of x and y coordinates, meshgrid builds 2D grids (X, Y)
#   where every (X[i,j], Y[i,j]) pair covers every combination of x and y.
# - Classic use: evaluate a function f(x, y) over an entire 2D grid at once,
#   for plotting surfaces/contours or numerical simulations.

print("\n# 03. np.meshgrid - Coordinate Grids")
print("# ------------------------------------")

x = np.array([0, 1, 2])
y = np.array([0, 1])
X, Y = np.meshgrid(x, y)
print("x =", x, ", y =", y)
print("X (x-coords broadcast across grid) =\n", X)
print("Y (y-coords broadcast across grid) =\n", Y)

# Evaluate f(x, y) = x^2 + y^2 over the whole grid in one vectorized call.
Z = X**2 + Y**2
print("Z = X**2 + Y**2 (function evaluated over entire grid at once) =\n", Z)

# 04. np.polyfit / np.poly1d - Fitting a Polynomial
# ------------------------------------
# - polyfit(x, y, degree) finds the polynomial coefficients that best fit
#   (x, y) data points via least-squares - e.g. degree=1 is a straight-line
#   fit ("linear regression"), degree=2 is a parabola, etc.
# - poly1d(coeffs) wraps the coefficients into a callable polynomial function.

print("\n# 04. np.polyfit / np.poly1d - Fitting a Polynomial")
print("# ------------------------------------")

x_data = np.array([0, 1, 2, 3, 4, 5])
y_data = np.array([1.1, 2.9, 9.2, 18.1, 31.9, 50.2])  # roughly y = 2x^2 - x + 1, plus noise

coeffs = np.polyfit(x_data, y_data, deg=2)
poly = np.poly1d(coeffs)

print("x_data =", x_data)
print("y_data =", y_data)
print("Fitted coefficients (degree 2, highest power first) =", coeffs)
print("poly (as an equation):", poly)
print("Predicted y at x=2.5:", poly(2.5))
print("Predicted y at x_data (compare to actual y_data):", poly(x_data))

# 05. np.select - Multi-Condition Vectorized Selection
# ------------------------------------
# - np.where(cond, a, b) only handles TWO outcomes (if/else).
# - np.select(condlist, choicelist, default=) generalizes this to MANY
#   conditions, evaluated in order - first matching condition wins, like a
#   vectorized if/elif/elif/.../else chain, but applied to a whole array at once.

print("\n# 05. np.select - Multi-Condition Vectorized Selection")
print("# ------------------------------------")

scores = np.array([95, 82, 71, 60, 45])
conditions = [
    scores >= 90,
    scores >= 80,
    scores >= 70,
    scores >= 60,
]
grades = ['A', 'B', 'C', 'D']

letter_grades = np.select(conditions, grades, default='F')
print("scores =", scores)
print("letter_grades (np.select, if/elif chain over the array) =", letter_grades)
print("# Compare: np.where only supports ONE condition (binary choice) per call -")
print("#   chaining np.where calls for >2 outcomes gets unreadable fast; np.select scales cleanly.")

print("\n# End of Advanced NumPy Explanation")
