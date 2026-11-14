# Random Module (NumPy) — Notes

## What this covers
Generating random numbers with NumPy's modern `Generator` API
(`np.random.default_rng`) and recognizing the older legacy API
(`np.random.seed` + global functions) that most existing code still uses.

## Key points
- **New API**: `rng = np.random.default_rng(seed)` creates a `Generator` object.
  Call methods on it: `rng.random(size)` (floats in `[0,1)`), `rng.integers(low, high, size)`
  (ints, `high` exclusive), `rng.choice(arr, size, replace=)`, `rng.normal(loc, scale, size)`.
- `rng.shuffle(arr)` shuffles **in place** (returns `None`); `rng.permutation(arr)`
  returns a **new** shuffled array, leaving the original untouched.
- **Legacy API**: `np.random.seed(n)` followed by module-level functions like
  `np.random.rand()` / `np.random.randint()`. Still works, still common in older
  code and tutorials.
- The legacy API shares **one hidden global state** across the whole process —
  `np.random.seed()` resets it for everything, including unrelated library code.
  The new `Generator` object carries its own independent state.

## Gotchas (the part worth revising twice)
- Same seed value, different API (`default_rng(42)` vs `np.random.seed(42)`)
  does **not** produce the same numbers — they use different underlying
  algorithms (PCG64 vs legacy Mersenne Twister). Don't expect cross-API reproducibility.
- Legacy global functions can be silently reseeded or advanced by imported
  library code you don't control — reproducibility with the legacy API depends
  on call *order*, not just the seed.
- `.integers(low, high)` is `high`-exclusive, same convention as Python's `range()`.

## When it matters
Any time reproducibility matters — ML train/test splits, simulations, unit
tests with random inputs — use `default_rng(seed)` and pass the `rng` object
around explicitly rather than relying on global state.

## One-line recap example
```python
import numpy as np
rng = np.random.default_rng(seed=42)   # preferred over np.random.seed(42)
print(rng.integers(1, 7, size=5))      # reproducible dice rolls
```
