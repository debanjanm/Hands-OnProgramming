# 01. The New Recommended API - np.random.default_rng()
# 02. Generator Methods - .random(), .integers(), .choice(), .normal()
# 03. Generator .shuffle() and .permutation()
# 04. The Legacy API - np.random.seed() + global functions
# 05. Why the New Generator API Is Preferred

import numpy as np

# 01. The New Recommended API - np.random.default_rng()
# ------------------------------------
# - Since NumPy 1.17, the recommended way to generate random numbers is via a
#   Generator object, created with np.random.default_rng(seed).
# - Passing a seed makes the sequence reproducible - same seed, same output,
#   every run, on every machine.
# - Unlike the legacy API, this Generator is a self-contained object - it does
#   NOT touch any global state, so different parts of a program (or different
#   threads) can each have their own independent, isolated Generator.

print("# 01. The New Recommended API - np.random.default_rng()")
print("# ------------------------------------")

rng = np.random.default_rng(seed=42)
print("rng =", rng)
print("type(rng) =", type(rng))
print("# 'seed=42' -> reproducible: rerunning this script gives identical numbers below.")

# 02. Generator Methods - .random(), .integers(), .choice(), .normal()
# ------------------------------------
# - .random(size)     -> floats in [0.0, 1.0)
# - .integers(low, high, size) -> random ints in [low, high) (high EXCLUSIVE, unlike legacy randint's inconsistent history)
# - .choice(a, size, replace=) -> random sample from an array-like
# - .normal(loc, scale, size)  -> samples from a Gaussian/normal distribution

print("\n# 02. Generator Methods")
print("# ------------------------------------")

floats = rng.random(5)
print("rng.random(5) (floats in [0,1)) =", floats)

ints = rng.integers(low=1, high=7, size=10)  # simulate 10 dice rolls, high=7 is exclusive
print("rng.integers(1, 7, size=10) (dice rolls, 1-6) =", ints)

choice_no_replace = rng.choice(["red", "green", "blue", "yellow"], size=2, replace=False)
print("rng.choice([...], size=2, replace=False) (no repeats) =", choice_no_replace)

normal_samples = rng.normal(loc=0.0, scale=1.0, size=5)  # standard normal
print("rng.normal(loc=0, scale=1, size=5) (standard normal samples) =", normal_samples)
print("# loc = mean, scale = standard deviation.")

# 03. Generator .shuffle() and .permutation()
# ------------------------------------
# - .shuffle(arr) shuffles an array IN PLACE (returns None).
# - .permutation(arr) returns a NEW shuffled array/copy, original untouched.

print("\n# 03. Generator .shuffle() and .permutation()")
print("# ------------------------------------")

deck = np.array(["A", "K", "Q", "J", "10"])
print("deck before shuffle:", deck)
rng.shuffle(deck)  # in place, no return value
print("deck after rng.shuffle(deck) (in place):", deck)

original = np.arange(5)
permuted = rng.permutation(original)
print("\noriginal =", original, "(untouched)")
print("rng.permutation(original) (new array) =", permuted)

# 04. The Legacy API - np.random.seed() + global functions
# ------------------------------------
# - Older code and many tutorials use np.random.seed(n) followed by module-level
#   functions like np.random.rand() and np.random.randint().
# - These all share ONE hidden global random state - calling np.random.seed()
#   anywhere in a program resets that shared state for EVERYTHING, including
#   unrelated code/libraries that also call np.random functions.
# - Still fully supported and works fine for quick scripts/notebooks - you WILL
#   see this style in the wild, so it's worth recognizing even if you don't write it.

print("\n# 04. The Legacy API - np.random.seed() + global functions")
print("# ------------------------------------")

np.random.seed(42)
legacy_floats = np.random.rand(5)          # floats in [0, 1), shape given as separate args
legacy_ints = np.random.randint(1, 7, size=10)  # same dice-roll simulation as above

print("np.random.seed(42) then np.random.rand(5) =", legacy_floats)
print("np.random.randint(1, 7, size=10) =", legacy_ints)
print("# Note: legacy_floats and rng.random(5) above use different algorithms internally,")
print("#       so they do NOT produce identical numbers even with the 'same' seed value.")

# 05. Why the New Generator API Is Preferred
# ------------------------------------
# - No global mutable state: two rng = default_rng(seed) instances never interfere
#   with each other or with library code elsewhere in the process. The legacy
#   global functions can silently be reseeded/advanced by code you don't control
#   (e.g. an imported library calling np.random.seed() internally).
# - Reproducibility is more reliable: a Generator's state travels with the object,
#   so passing `rng` into a function guarantees deterministic behavior regardless
#   of what else ran before it. With the legacy API, execution ORDER matters.
# - Better statistical quality: default_rng() uses the PCG64 bit generator by
#   default, which has better statistical properties and performance than the
#   legacy Mersenne Twister used by np.random.seed()/rand().
# - Both APIs still work and produce valid random numbers - new code should
#   prefer default_rng(), but you don't need to "fix" old code that already uses seed().

print("\n# 05. Why the New Generator API Is Preferred")
print("# ------------------------------------")
print("# - No shared global state (each Generator instance is independent).")
print("# - More reliable reproducibility (state travels with the object, not call order).")
print("# - PCG64 algorithm (default) has better statistical quality than legacy Mersenne Twister.")
print("# - Recommendation: use default_rng() in new code; legacy API still works, just avoid for new work.")

print("\n# End of Random Module Explanation")
