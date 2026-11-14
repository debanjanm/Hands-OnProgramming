import math
import cmath
import sys
import numbers
import statistics
from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP, ROUND_CEILING, ROUND_FLOOR
from decimal import getcontext, localcontext, InvalidOperation
from fractions import Fraction

# 01. Math and Numeric Modules - Introduction
# ------------------------------------
# - Python ships several numeric toolboxes, each for a different job:
#     math        -> fast float functions (sqrt, sin, log, gcd, ...)
#     cmath       -> the same idea for complex numbers
#     decimal     -> exact base-10 arithmetic (money!) with controllable rounding
#     fractions   -> exact rational numbers (1/3 stays 1/3)
#     statistics  -> mean, median, stdev... for small/medium datasets
#     numbers     -> abstract "family tree" of number types (int, float, ...)
# - WHY so many? Computers store floats in binary, and most decimal fractions
#   (like 0.1) cannot be written exactly in binary. Different problems need
#   different trade-offs between speed, exactness, and convenience.

print("# 01. Math and Numeric Modules - Introduction")
print("# ------------------------------------")

# 02. math - Constants
# ------------------------------------
print("\n# 02. math - Constants")
print("pi  =", math.pi)
print("e   =", math.e)
print("tau =", math.tau, "(= 2*pi, one full circle in radians)")
print("inf =", math.inf, "| nan =", math.nan)

# 03. floor, ceil, trunc vs round
# ------------------------------------
# - floor: toward -infinity   ceil: toward +infinity   trunc: toward zero
# - They only differ for NEGATIVE numbers - this trips people up.
print("\n# 03. floor / ceil / trunc / round")
for x in (2.7, -2.7):
    print(f"x={x:5}: floor={math.floor(x):3} ceil={math.ceil(x):3} trunc={math.trunc(x):3} round={round(x):3}")

# - round() uses "banker's rounding" (round half to even), not school rounding!
print("round(0.5), round(1.5), round(2.5), round(3.5) ->", [round(v) for v in (0.5, 1.5, 2.5, 3.5)])
print("round(2.675, 2) ->", round(2.675, 2), "(NOT 2.68: 2.675 is stored as 2.67499999...)")
print("round(1234, -2) ->", round(1234, -2), "(negative digits round to hundreds)")
print("int(-2.7) ->", int(-2.7), "(int() truncates, same as math.trunc)")
print("-7 // 2 ->", -7 // 2, "(// floors, does NOT truncate)")

# 04. isclose - Comparing Floats Safely
# ------------------------------------
# - Never compare floats with ==. Use isclose with a tolerance.
# - rel_tol: relative to the size of the numbers (default 1e-09)
# - abs_tol: absolute; REQUIRED when comparing to 0 (relative to 0 is meaningless)
print("\n# 04. isclose - rel_tol and abs_tol")
print("0.1 + 0.2 == 0.3          ->", 0.1 + 0.2 == 0.3)
print("isclose(0.1 + 0.2, 0.3)   ->", math.isclose(0.1 + 0.2, 0.3))
print("isclose(1e-10, 0.0)       ->", math.isclose(1e-10, 0.0), "(rel_tol alone fails near zero)")
print("isclose(1e-10, 0.0, abs_tol=1e-9) ->", math.isclose(1e-10, 0.0, abs_tol=1e-9))
print("isclose(100, 101, rel_tol=0.02)   ->", math.isclose(100, 101, rel_tol=0.02), "(within 2%)")
print("isclose(100, 103, rel_tol=0.02)   ->", math.isclose(100, 103, rel_tol=0.02))

# 05. fsum vs sum - Accurate Float Summing
# ------------------------------------
# - Adding floats one by one (what a plain loop does) accumulates tiny errors.
# - math.fsum() tracks the lost low-order bits and returns the correctly rounded total.
# - NOTE: Python 3.12 made the built-in sum() smarter for floats (it now uses
#   compensated summation), so we use an explicit loop to show the classic problem.
print("\n# 05. fsum vs a plain running total")


def naive_sum(items):
    total = 0.0
    for item in items:
        total += item
    return total


values = [0.1] * 10
print("loop total of [0.1]*10  =", naive_sum(values))
print("math.fsum([0.1]*10)     =", math.fsum(values))
tricky = [1e100, 1.0, -1e100]
print("loop total of [1e100, 1.0, -1e100]  =", naive_sum(tricky), "(the 1.0 got swallowed)")
print("fsum([1e100, 1.0, -1e100])          =", math.fsum(tricky))
print("builtin sum on 3.12+ =", sum(values), "(version-dependent; use fsum when you NEED accuracy)")

# 06. prod, gcd, lcm
# ------------------------------------
print("\n# 06. prod / gcd / lcm")
print("math.prod([1, 2, 3, 4, 5]) =", math.prod([1, 2, 3, 4, 5]))
print("math.prod([]) =", math.prod([]), "(empty product is 1, like sum([]) is 0)")
print("math.gcd(48, 18)    =", math.gcd(48, 18), "(greatest common divisor)")
print("math.lcm(4, 6)      =", math.lcm(4, 6), "(least common multiple)")
print("math.gcd(12, 18, 24) =", math.gcd(12, 18, 24), "(many args OK in 3.9+)")
print("simplify 48/18 ->", 48 // math.gcd(48, 18), "/", 18 // math.gcd(48, 18))

# 07. factorial, comb, perm - Counting
# ------------------------------------
# - factorial(n) = n!      comb(n, k) = n choose k (order does NOT matter)
# - perm(n, k) = ordered arrangements (order DOES matter)
print("\n# 07. factorial / comb / perm")
print("factorial(5)  =", math.factorial(5))
print("factorial(20) =", math.factorial(20), "(ints never overflow in Python)")
print("comb(5, 2)    =", math.comb(5, 2), "-> pick 2 people from 5 for a pair")
print("perm(5, 2)    =", math.perm(5, 2), "-> 2 ranked positions (gold, silver) from 5")
print("comb(52, 5)   =", math.comb(52, 5), "-> possible poker hands")
try:
    math.factorial(-1)
except ValueError as err:
    print("factorial(-1) ->", type(err).__name__ + ":", err)
try:
    math.factorial(2.5)
except (ValueError, TypeError) as err:
    print("factorial(2.5) ->", type(err).__name__ + ":", err)

# 08. isqrt, sqrt, pow, exp, log family
# ------------------------------------
print("\n# 08. isqrt / sqrt / pow / exp / log")
print("math.sqrt(16)    =", math.sqrt(16), "(always a float)")
print("math.isqrt(17)   =", math.isqrt(17), "(integer floor of sqrt, exact even for huge ints)")
big = 10**40
print("isqrt(10**40)    =", math.isqrt(big), "| sqrt(10**40) =", math.sqrt(big))
print("math.pow(2, 10)  =", math.pow(2, 10), "(float) vs 2 ** 10 =", 2 ** 10, "(int)")
print("math.exp(1)      =", math.exp(1), "(= e)")
print("math.log(math.e) =", math.log(math.e), "(natural log)")
print("math.log(8, 2)   =", math.log(8, 2), "| log2(8) =", math.log2(8), "| log10(1000) =", math.log10(1000))
print("math.log(1000, 10) =", math.log(1000, 10), "(base arg can be slightly off; prefer log10/log2)")
for bad in (lambda: math.sqrt(-1), lambda: math.log(0)):
    try:
        bad()
    except ValueError as err:
        print("domain error ->", err)

# 09. Trigonometry - degrees vs radians
# ------------------------------------
# - math trig functions take RADIANS, not degrees. Convert first.
print("\n# 09. Trigonometry")
print("sin(90) (wrong, 90 radians!) =", round(math.sin(90), 4))
print("sin(radians(90))             =", math.sin(math.radians(90)))
print("cos(pi)   =", math.cos(math.pi))
print("tan(pi/4) =", round(math.tan(math.pi / 4), 10))
print("degrees(pi) =", math.degrees(math.pi))
print("sin(pi) =", math.sin(math.pi), "(not exactly 0 - float pi is approximate)")
print("atan2(1, 1) in degrees =", math.degrees(math.atan2(1, 1)), "(atan2 handles all quadrants)")

# 10. hypot and dist - Distances
# ------------------------------------
print("\n# 10. hypot / dist")
print("hypot(3, 4)             =", math.hypot(3, 4), "(sqrt(3**2 + 4**2), safe against overflow)")
print("hypot(1, 2, 2)          =", math.hypot(1, 2, 2), "(n dimensions in 3.8+)")
print("dist((0, 0), (3, 4))    =", math.dist((0, 0), (3, 4)), "(distance between two points)")
print("dist((1, 1, 1), (4, 5, 13)) =", math.dist((1, 1, 1), (4, 5, 13)))

# 11. inf and nan - Special Float Values
# ------------------------------------
# - inf: "bigger than any number"; nan: "not a number" (undefined result)
print("\n# 11. inf and nan")
inf, nan = math.inf, math.nan
print("inf > 10**100        ->", inf > 10**100)
print("-inf < 0             ->", -inf < 0)
print("inf + 1              ->", inf + 1)
print("inf - inf            ->", inf - inf, "(undefined -> nan)")
print("nan == nan           ->", nan == nan, "(nan is not equal to ANYTHING, even itself)")
print("nan != nan           ->", nan != nan)
print("math.isnan(nan)      ->", math.isnan(nan), "(the correct test)")
print("math.isinf(-inf)     ->", math.isinf(-inf))
print("math.isfinite(1.5)   ->", math.isfinite(1.5))
print("float('inf'), float('nan') ->", float("inf"), float("nan"), "(parsing from strings works)")
print("max(1, nan, 2) ->", max(1, nan, 2), "| max(nan, 1, 2) ->", max(nan, 1, 2), "(order-dependent: nan breaks comparisons!)")
clean = [x for x in [1.0, nan, 3.0] if not math.isnan(x)]
print("filtered nan out:", clean)
print("1.0 / 0 -> ZeroDivisionError in Python (it does NOT return inf)")
try:
    1.0 / 0
except ZeroDivisionError as err:
    print("   caught:", err)
print("1e308 * 10 ->", 1e308 * 10, "(float overflow silently becomes inf)")
try:
    math.exp(1000)
except OverflowError as err:
    print("math.exp(1000) -> OverflowError:", err)

# 12. cmath - Complex Numbers
# ------------------------------------
# - math.sqrt(-1) raises ValueError; cmath.sqrt(-1) gives the imaginary unit.
# - Python writes the imaginary part with j (engineering convention), not i.
print("\n# 12. cmath - Complex Numbers")
z = 3 + 4j
print("z =", z, "| real:", z.real, "imag:", z.imag, "| conjugate:", z.conjugate())
print("abs(z) =", abs(z), "(magnitude, same as hypot(3, 4))")
print("cmath.sqrt(-1) =", cmath.sqrt(-1))
# Roots of x^2 + 2x + 5 = 0 via the quadratic formula (negative discriminant!)
a, b, c = 1, 2, 5
disc = b * b - 4 * a * c
root1 = (-b + cmath.sqrt(disc)) / (2 * a)
root2 = (-b - cmath.sqrt(disc)) / (2 * a)
print(f"roots of x^2+2x+5: {root1} and {root2}")
# polar <-> rectangular
r, phi = cmath.polar(z)
print(f"polar(3+4j) -> r={r}, phi={phi:.4f} rad ({math.degrees(phi):.2f} deg)")
print("rect(r, phi)    ->", cmath.rect(r, phi))
print("Euler: exp(1j*pi) =", cmath.exp(1j * math.pi), "(approx -1 + 0j)")
# 3 cube roots of 8: they sit on a circle
cube_roots = [cmath.rect(2, 2 * math.pi * k / 3) for k in range(3)]
print("cube roots of 8:", [f"{x.real:.3f}{x.imag:+.3f}j" for x in cube_roots])

# 13. decimal - The Float Gotcha
# ------------------------------------
# - Decimal does base-10 arithmetic, exactly like on paper. Perfect for money.
# - GOTCHA: build Decimals from STRINGS (or ints). Decimal(0.1) faithfully
#   copies the already-wrong binary float, digits and all.
print("\n# 13. decimal - Decimal('0.1') vs Decimal(0.1)")
print("Decimal('0.1')  =", Decimal("0.1"))
print("Decimal(0.1)    =", Decimal(0.1))
print("0.1 + 0.2 (float)             =", 0.1 + 0.2)
print("Decimal('0.1') + Decimal('0.2') =", Decimal("0.1") + Decimal("0.2"))
print("== 0.3 ?", Decimal("0.1") + Decimal("0.2") == Decimal("0.3"))
try:
    Decimal("0.1") + 0.2
except TypeError as err:
    print("Decimal + float ->", type(err).__name__ + ":", err)
print("Decimal('0.1') + 2 ->", Decimal("0.1") + 2, "(ints mix fine)")
print("Decimal('1.10') =", Decimal("1.10"), "| Decimal('1.1') == Decimal('1.10') ->", Decimal("1.1") == Decimal("1.10"),
      "(trailing zeros kept for display, equal in value)")
try:
    Decimal("abc")
except InvalidOperation:
    print("Decimal('abc') -> InvalidOperation (bad string)")

# 14. decimal - Precision and Context
# ------------------------------------
# - The context holds settings: prec = significant digits (default 28), rounding mode.
# - Precision counts SIGNIFICANT digits, not decimals after the point.
print("\n# 14. decimal - Context / Precision")
print("default prec:", getcontext().prec)
print("Decimal(1) / Decimal(3) =", Decimal(1) / Decimal(3))
with localcontext() as ctx:  # change settings temporarily, restored automatically
    ctx.prec = 6
    print("prec=6  ->", Decimal(1) / Decimal(3), "| sqrt(2) =", Decimal(2).sqrt())
with localcontext() as ctx:
    ctx.prec = 50
    print("prec=50 ->", Decimal(2).sqrt())
print("after the block, prec is back to:", getcontext().prec)
print("NOTE: precision applies to RESULTS of operations, not to the numbers you type in:")
print("      Decimal('1.123456789123456789123456789123') + 0 ->", Decimal("1.123456789123456789123456789123") + 0)

# 15. decimal - Rounding Modes and quantize
# ------------------------------------
# - quantize(exp) rounds a Decimal to the same number of decimals as `exp`.
#   This is THE way to round money to cents.
print("\n# 15. decimal - Rounding modes and quantize")
cent = Decimal("0.01")
price = Decimal("2.665")
print("price =", price)
print("quantize to cents (default ROUND_HALF_EVEN):", price.quantize(cent))
print("ROUND_HALF_UP   (school rounding):", price.quantize(cent, rounding=ROUND_HALF_UP))
print("ROUND_HALF_EVEN (banker's)       :", price.quantize(cent, rounding=ROUND_HALF_EVEN))
print("HALF_EVEN sends ties to the even neighbour: 2.665 -> 2.66, 2.675 -> 2.68; HALF_UP always rounds ties up.")
print("float round(2.675, 2) =", round(2.675, 2), "<- not even a tie in binary; Decimal('2.675') is exact:", Decimal("2.675").quantize(cent, ROUND_HALF_UP))
print("\nmode comparison on 2.5 and -2.5 (round to whole number):")
one = Decimal("1")
for mode in (ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN, ROUND_UP, ROUND_CEILING, ROUND_FLOOR):
    print(f"  {mode:15} 2.5 -> {Decimal('2.5').quantize(one, mode)}   -2.5 -> {Decimal('-2.5').quantize(one, mode)}")

# - Typical invoice: line totals, tax, and a rounded total
unit_price, qty, tax_rate = Decimal("19.99"), 3, Decimal("0.0825")
subtotal = unit_price * qty
tax = (subtotal * tax_rate).quantize(cent, ROUND_HALF_UP)
print(f"\ninvoice: subtotal={subtotal} tax={tax} total={subtotal + tax}")
print("normalize() strips trailing zeros:", Decimal("3.1400").normalize())
print("as_tuple():", Decimal("-12.50").as_tuple())

# 16. fractions.Fraction - Exact Rationals
# ------------------------------------
print("\n# 16. fractions.Fraction")
third = Fraction(1, 3)
print("Fraction(1, 3) =", third, "| float:", float(third))
print("1/3 + 1/6 =", Fraction(1, 3) + Fraction(1, 6), "(auto-simplified, exact)")
print("Fraction(6, 8) =", Fraction(6, 8), "| numerator/denominator:", Fraction(6, 8).numerator, Fraction(6, 8).denominator)
print("Fraction('0.75') =", Fraction("0.75"), "| Fraction('3/9') =", Fraction("3/9"))
print("Fraction(0.1) =", Fraction(0.1), "(same float gotcha as Decimal(0.1)!)")
print("Fraction('0.1') =", Fraction("0.1"))
print("sum of ten 1/10:", sum([Fraction(1, 10)] * 10), "== 1 ->", sum([Fraction(1, 10)] * 10) == 1)
print("Fraction(1,3) * 3 == 1 ->", Fraction(1, 3) * 3 == 1)
# limit_denominator: find the nearest simple fraction (great for "what fraction is this float?")
print("Fraction(math.pi).limit_denominator(100)    =", Fraction(math.pi).limit_denominator(100), "(close to pi)")
print("Fraction(math.pi).limit_denominator(1000)   =", Fraction(math.pi).limit_denominator(1000))
print("Fraction(0.333).limit_denominator(10)       =", Fraction(0.333).limit_denominator(10))
print("Fraction(2, 3) ** 2 =", Fraction(2, 3) ** 2, "| round(Fraction(7, 2)) =", round(Fraction(7, 2)))

# 17. statistics - Describing Data
# ------------------------------------
data = [2, 4, 4, 4, 5, 5, 7, 9]
print("\n# 17. statistics - Central tendency and spread")
print("data:", data)
print("mean        =", statistics.mean(data), "(exact-ish average)")
print("fmean       =", statistics.fmean(data), "(faster, always float)")
print("median      =", statistics.median(data), "(middle; average of 2 middles for even length)")
print("median_low  =", statistics.median_low(data), "| median_high =", statistics.median_high(data), "(always an actual data point)")
print("mode        =", statistics.mode(data), "(most common value)")
print("multimode   =", statistics.multimode([1, 1, 2, 2, 3]), "(all ties returned as a list)")
print("pstdev      =", statistics.pstdev(data), "(population: data IS everything)")
print("stdev       =", round(statistics.stdev(data), 4), "(sample: data is a SAMPLE of a bigger group, divides by n-1)")
print("pvariance   =", statistics.pvariance(data), "| variance =", round(statistics.variance(data), 4))
print("outlier effect: mean([1,2,3,4,100]) =", statistics.mean([1, 2, 3, 4, 100]),
      "but median =", statistics.median([1, 2, 3, 4, 100]), "(median resists outliers)")

# - Errors: empty data
for func in (statistics.mean, statistics.median, statistics.mode):
    try:
        func([])
    except statistics.StatisticsError as err:
        print(f"{func.__name__}([]) -> StatisticsError: {err}")
try:
    statistics.stdev([5])
except statistics.StatisticsError as err:
    print("stdev([5]) -> StatisticsError:", err, "(sample stdev needs 2+ points)")

# - quantiles (3.8+): cut points splitting data into n equal groups
q = statistics.quantiles(data, n=4)
print("quartiles (n=4):", q)
print("IQR = Q3 - Q1 =", q[2] - q[0])

# - correlation / linear_regression need Python 3.10+
if sys.version_info >= (3, 10):
    hours = [1, 2, 3, 4, 5]
    score = [52, 58, 65, 70, 78]
    print("\ncorrelation(hours, score) =", round(statistics.correlation(hours, score), 4), "(1.0 = perfect straight line)")
    slope, intercept = statistics.linear_regression(hours, score)
    print(f"linear_regression: score = {slope:.2f} * hours + {intercept:.2f}")
    print(f"predicted score for 6 hours: {slope * 6 + intercept:.1f}")
else:
    print("\n[skip] correlation / linear_regression need Python 3.10+")

# 18. numbers - The Numeric Tower
# ------------------------------------
# - numbers.Number > Complex > Real > Rational > Integral
# - Use isinstance(x, numbers.Real) to accept ANY real number type
#   (int, float, Fraction, numpy floats...) instead of listing types by hand.
print("\n# 18. numbers - Numeric tower")
samples = [("1 (int)", 1), ("1.5 (float)", 1.5), ("Fraction(1,2)", Fraction(1, 2)), ("3+4j (complex)", 3 + 4j), ("Decimal('1.5')", Decimal("1.5")), ("True (bool)", True)]
print(f"{'value':16}{'Integral':10}{'Rational':10}{'Real':8}{'Complex':9}{'Number':8}")
for label, v in samples:
    flags = [isinstance(v, t) for t in (numbers.Integral, numbers.Rational, numbers.Real, numbers.Complex, numbers.Number)]
    print(f"{label:16}" + "".join(f"{str(f):{w}}" for f, w in zip(flags, (10, 10, 8, 9, 8))))
print("NOTE: Decimal is a Number but NOT a Real - it deliberately refuses to mix with float.")
print("NOTE: bool is a subclass of int, so isinstance(True, int) is True - a classic surprise.")


def add_all(*items):
    """Accept any real number type; reject strings early with a clear error."""
    for v in items:
        if not isinstance(v, numbers.Real):
            raise TypeError(f"not a real number: {v!r}")
    return sum(items)


print("add_all(1, 2.5, Fraction(1, 2)) =", add_all(1, 2.5, Fraction(1, 2)))
try:
    add_all(1, "2")
except TypeError as err:
    print("add_all(1, '2') ->", err)

# 19. Integer Tricks - divmod, pow, bit tools
# ------------------------------------
print("\n# 19. Integer tricks")
print("divmod(17, 5) =", divmod(17, 5), "(quotient and remainder in one call)")
print("divmod(-17, 5) =", divmod(-17, 5), "(remainder takes the divisor's sign)")
mins = 135
h, m = divmod(mins, 60)
print(f"{mins} minutes = {h}h {m}m")
print("pow(2, 10) =", pow(2, 10), "| pow(2, 10, 1000) =", pow(2, 10, 1000), "(modular: (2**10) % 1000, but fast even for huge exponents)")
print("pow(7, 10**18, 13) =", pow(7, 10**18, 13), "(instant; 7**(10**18) itself would never finish)")
print("pow(3, -1, 7) =", pow(3, -1, 7), "(modular inverse, 3.8+: 3 * 5 = 15 = 1 mod 7)")
print("(255).bit_length() =", (255).bit_length(), "| (256).bit_length() =", (256).bit_length(), "(bits needed to store the number)")
if sys.version_info >= (3, 10):
    print("(255).bit_count() =", (255).bit_count(), "| (0b1011).bit_count() =", (0b1011).bit_count(), "(number of 1-bits)")
else:
    print("[skip] int.bit_count needs Python 3.10+; use bin(n).count('1')")
print("bin(10) =", bin(10), "| hex(255) =", hex(255), "| oct(8) =", oct(8), "| int('ff', 16) =", int("ff", 16))
print("10 & 6 =", 10 & 6, "| 10 | 6 =", 10 | 6, "| 10 ^ 6 =", 10 ^ 6, "| 1 << 4 =", 1 << 4, "| 256 >> 2 =", 256 >> 2)
print("is power of two? n & (n-1) == 0 ->", [n for n in range(1, 20) if n & (n - 1) == 0])
print("(1.5).as_integer_ratio() =", (1.5).as_integer_ratio(), "| (0.1).as_integer_ratio() =", (0.1).as_integer_ratio())

# 20. Floating-Point Error Demos
# ------------------------------------
# - A float is a binary fraction: sign * mantissa * 2**exponent (64 bits, ~15-17 digits).
# - 0.1 is 1/10, which in binary is 0.000110011001100... forever, so it gets cut off.
print("\n# 20. Floating-point error demos")
print(f"0.1 stored as: {Decimal(0.1)}")
print("0.1 + 0.2        =", 0.1 + 0.2)
print("0.1 * 3          =", 0.1 * 3)
print("1.1 * 1.1        =", 1.1 * 1.1)
print("round(1.1*1.1, 2) =", round(1.1 * 1.1, 2), "(print-time rounding hides, not fixes, the error)")
print(f"format to 20 places: {0.1:.20f}")
print("2**53 + 1 as float:", float(2**53) + 1, "-> floats can't count past 2**53 exactly")
print("1e16 + 1 - 1e16  =", 1e16 + 1 - 1e16, "(the +1 vanished: absorption)")
print("(0.1+0.2)-0.3    =", (0.1 + 0.2) - 0.3, "(machine epsilon scale)")
print("sys.float_info.epsilon =", sys.float_info.epsilon, "(smallest gap near 1.0)")
print("sys.float_info.max     =", sys.float_info.max)
total = 0.0
for _ in range(1_000_000):
    total += 0.1
print("adding 0.1 a million times =", total, "(vs exact 100000.0; error accumulates)")
print("same with fsum =", math.fsum([0.1] * 1_000_000))

# 21. Which Number Type Should I Use?
# ------------------------------------
#   Type        Exact?        Speed     Good for                              Avoid for
#   ---------   -----------   -------   -----------------------------------   ----------------------------
#   int         yes           fastest   counting, IDs, cents as integers      fractions / measurements
#   float       NO (binary)   fast      science, graphics, ML, measurements   money, equality checks
#   Decimal     yes (base 10) slower    money, invoices, tax, exact decimals  heavy number-crunching
#   Fraction    yes           slowest   exact ratios, recipes, music theory   huge/long calculations
#                                       (numbers can grow in size)
#   complex     NO (float)    fast      signals, electrical eng., roots       -
#
# - Rule of thumb: measuring something -> float; counting or money -> int/Decimal.
# - A very common money trick: store whole cents as int (1999 = $19.99).
print("\n# 21. Which number type? (see the table in the comments above)")
cents = 1999
print("cents as int:", cents, "->", f"${cents // 100}.{cents % 100:02d}")

# 22. Worked Example 1 - Compound Interest: float vs Decimal
# ------------------------------------
print("\n# 22. Compound interest: float vs Decimal")
principal_f, rate_f, years = 10_000.0, 0.0725, 30
principal_d, rate_d = Decimal("10000.00"), Decimal("0.0725")
bal_f, bal_d = principal_f, principal_d
for year in range(1, years + 1):
    bal_f = bal_f * (1 + rate_f / 12) ** 12  # compounded monthly, yearly step
    bal_d = (bal_d * (1 + rate_d / 12) ** 12)
    bal_d = bal_d.quantize(cent, ROUND_HALF_EVEN)  # banks round to cents every period
    if year in (1, 5, 10, 20, 30):
        print(f"  year {year:2}: float={bal_f:16.6f}   Decimal={bal_d}")
print("(Decimal drifts from float by pennies because it rounds to cents EVERY period, like a real bank does)")
print("float final raw repr   :", repr(bal_f))
print("Decimal final (cents)  :", bal_d)
# - Floats are fine here to ~1e-9 relative; the REAL risk is summing millions of
#   tiny transactions and comparing totals with ==. Money code should be Decimal.
ledger_f = naive_sum([0.1] * 10) - 1.0
ledger_d = sum([Decimal("0.1")] * 10) - Decimal("1.0")
print("ledger of ten 0.10 payments minus 1.00 -> float:", ledger_f, "| Decimal:", ledger_d)

# 23. Worked Example 2 - Statistics Summary of a Small Dataset
# ------------------------------------
print("\n# 23. Statistics summary: exam scores")
scores = [72, 85, 90, 66, 85, 78, 92, 85, 61, 74, 88, 95]


def summarize(values):
    """Return a dict of common descriptive statistics."""
    q1, q2, q3 = statistics.quantiles(values, n=4)
    return {
        "count": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.fmean(values), 2),
        "median": statistics.median(values),
        "mode": statistics.mode(values),
        "stdev": round(statistics.stdev(values), 2),
        "Q1": q1, "Q3": q3,
    }


summary = summarize(scores)
for key, value in summary.items():
    print(f"  {key:7} {value}")
mean, sd = summary["mean"], summary["stdev"]
outliers = [s for s in scores if abs(s - mean) > 2 * sd]
print("scores more than 2 stdev from mean:", outliers or "none")
z_scores = {s: round((s - mean) / sd, 2) for s in (61, 85, 95)}
print("z-scores (how many stdevs from the mean):", z_scores)
curve = [round(s * Fraction(105, 100)) for s in scores]
print("scores curved by +5% (Fraction, exact):", curve)

# 24. Common Mistakes Recap
# ------------------------------------
print("\n# 24. Recap")
print("- compare floats with isclose, not ==")
print("- build Decimal from strings; quantize for money")
print("- math trig wants radians; nan != nan; use isnan")
print("- statistics.stdev = sample, pstdev = whole population")
print("- empty data -> StatisticsError; plan for it")
