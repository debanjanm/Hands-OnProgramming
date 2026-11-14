# Random And Secrets — Notes

## What this covers
`random` for repeatable "random" numbers (simulations, games, tests, sampling) and `secrets` for unguessable values (passwords, tokens). They solve opposite problems.

## Key points
- **`random` is pseudo-random**: a formula (Mersenne Twister) plus a seed. Same seed gives the same sequence. `random.seed(42)` makes a run repeatable.
- **`getstate()` / `setstate()`** bookmark and replay the stream.
- **Single numbers**: `random()` (float in 0.0 up to, not including, 1.0), `uniform(a, b)`, `randint(a, b)` (both ends included), `randrange(a, b, step)` (end excluded, like `range`).
- **Picking**: `choice(seq)` for one; `choices(seq, k=n, weights=...)` with replacement; `sample(seq, k=n)` without replacement (all unique).
- **`shuffle(x)`** reorders a list in place and returns `None`. `sample(x, len(x))` returns a new shuffled list and leaves `x` alone.
- **Distributions**: `gauss` / `normalvariate` (bell curve), `triangular` (min, max, most likely), `expovariate` (waiting times), `betavariate` (values between 0 and 1).
- **`random.Random(seed)`** is your own private generator. It is not disturbed by other code touching the global one. Pass it into functions so tests can inject a seeded one.
- **`randbytes(n)`** (3.9+) gives random bytes; `getrandbits(k)` gives k random bits.
- **`secrets`** uses the operating system's secure randomness: `token_hex`, `token_urlsafe`, `token_bytes`, `choice`, `randbelow(n)`, `randbits`. No seed, never repeats.
- **`secrets.compare_digest(a, b)`** compares secrets in constant time.

| Job | Use |
|-----|-----|
| Passwords, API keys, reset tokens, session IDs | `secrets` |
| Comparing a user-supplied secret | `secrets.compare_digest` |
| Games, dice, card shuffles, A/B splits, bootstrap | `random.Random(seed)` |
| Large numeric arrays, ML | `numpy.random.default_rng` (see `07-NumPy/07-Random-Module.py`) |

## Gotchas (the part worth revising twice)
- `randint(1, 6)` can return 6; `randrange(1, 6)` never does. `randint(a, b) == randrange(a, b + 1)`.
- `x = random.shuffle(x)` makes `x` equal to `None`. Shuffle in place, don't assign.
- `shuffle` fails on strings and tuples (immutable). Use `sample(seq, len(seq))`.
- `sample(population, k)` raises `ValueError` if `k` is larger than the population, and `TypeError` on a set in 3.11+. Use `sorted(my_set)` first.
- `choices` can repeat items (with replacement), which is what bootstrapping needs. `sample` cannot.
- `choice([])` raises `IndexError`.
- Weights in `choices` are relative (70/25/5), not percentages that must add to 100.
- **`random` is not secure.** Anyone who learns the generator's state can predict every future value. Never use it for anything a guesser could exploit.
- `==` on secrets leaks timing information. Use `compare_digest`.
- `compare_digest` refuses non-ASCII `str`; encode to bytes first.
- Printing a generated token defeats the point in logs. Treat them like passwords.

## When it matters
Reproducible tests and simulations (seed it), fair shuffles and splits, Monte Carlo estimates, and any login, token or key-generation code (must be `secrets`).

## One-line recap example
```python
import random, secrets
random.Random(7).randint(1, 6)       # repeatable dice roll for tests
secrets.token_urlsafe(16)            # unguessable URL-safe token for real use
```
