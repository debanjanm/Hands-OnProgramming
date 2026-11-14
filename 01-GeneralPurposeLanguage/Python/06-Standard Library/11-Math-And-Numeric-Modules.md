# Math And Numeric Modules — Notes

## What this covers
Python's number toolboxes: `math`, `cmath`, `decimal`, `fractions`, `statistics` and the `numbers` family tree. The big idea: floats are fast but not exact, so pick the type that matches the job.

## Key points
- **`math`** works on floats: constants (`pi`, `e`, `tau`, `inf`, `nan`), `sqrt`, `exp`, `log/log2/log10`, trig, `hypot`, `dist`.
- **Integer helpers** in `math`: `gcd`, `lcm`, `factorial`, `comb` (order does not matter), `perm` (order matters), `isqrt` (exact integer square root), `prod`.
- **`floor` / `ceil` / `trunc`** only differ for negatives: floor goes down, ceil goes up, trunc goes toward zero.
- **`math.isclose(a, b, rel_tol=, abs_tol=)`** is the right way to compare floats. Use `abs_tol` when one side can be 0.
- **`math.fsum`** adds floats accurately; a plain running total drifts.
- **`cmath`** is `math` for complex numbers: `cmath.sqrt(-1)` gives `1j`, `polar` / `rect` convert both ways.
- **`decimal.Decimal`** does exact base-10 maths. Build it from **strings**. Use `quantize(Decimal("0.01"), rounding=...)` to round money. `localcontext()` changes precision temporarily.
- **`fractions.Fraction`** keeps exact ratios (`1/3 + 1/6 == 1/2`). `limit_denominator(n)` finds the nearest simple fraction.
- **`statistics`**: `mean`, `fmean`, `median`, `median_low/high`, `mode`, `multimode`, `stdev` (sample), `pstdev` (population), `variance`, `quantiles`; `correlation` and `linear_regression` need 3.10+.
- **`numbers`**: `Integral < Rational < Real < Complex < Number`. Use `isinstance(x, numbers.Real)` to accept any real number type.
- **Integer tricks**: `divmod(a, b)`, `pow(a, b, m)` (fast modular power), `bit_length()`, `bit_count()` (3.10+).

| Type | Exact? | Use for |
|------|--------|---------|
| `int` | yes | counting, IDs, cents |
| `float` | no | science, graphics, measurements |
| `Decimal` | yes (base 10) | money, tax, invoices |
| `Fraction` | yes | exact ratios |

## Gotchas (the part worth revising twice)
- `round()` uses banker's rounding: `round(2.5) == 2`, `round(3.5) == 4`. And `round(2.675, 2) == 2.67` because the stored float is slightly below 2.675.
- `Decimal(0.1)` copies the float's error (`0.1000000000000000055...`). Write `Decimal("0.1")`. Same trap for `Fraction(0.1)`.
- `Decimal + float` raises `TypeError` on purpose. `Decimal + int` is fine.
- Decimal precision counts **significant digits** (default 28) and applies to results, not to the numbers you type.
- Trig functions want **radians**: `math.sin(90)` is not 1. Use `math.radians()`.
- `nan != nan`, so test with `math.isnan()`. `max(1, nan, 2)` depends on argument order.
- `1.0 / 0` raises `ZeroDivisionError` (it does not give `inf`), but `1e308 * 10` silently becomes `inf`, and `math.exp(1000)` raises `OverflowError`.
- `stdev` of one value, or `mean([])`, raises `StatisticsError`. `stdev` divides by n-1 (sample); `pstdev` divides by n.
- `math.log(1000, 10)` can give `2.9999999999999996`; use `log10`.
- Python 3.12's built-in `sum()` got smarter for floats, so don't rely on older `sum` drift demos; use `fsum` when accuracy matters.
- `isinstance(True, int)` is `True` (bool is an int), and `Decimal` is a `Number` but not a `Real`.

## When it matters
Money code (use `Decimal` and `quantize`), comparing computed floats in tests (`isclose`), quick data summaries without pandas (`statistics`), and recipes or ratios that must stay exact (`Fraction`).

## One-line recap example
```python
from decimal import Decimal, ROUND_HALF_UP
print(Decimal("2.675").quantize(Decimal("0.01"), ROUND_HALF_UP))   # 2.68  (round(2.675, 2) gives 2.67)
```
