import math
import random
import secrets
import string
import sys
import statistics
from collections import Counter

# 01. random and secrets - Introduction
# ------------------------------------
# - random: "pseudo-random" numbers - produced by a formula (Mersenne Twister)
#   starting from a seed. Same seed -> same sequence. Great for simulations,
#   games, tests, sampling. NEVER for passwords, tokens or anything security-related.
# - secrets: random numbers from the operating system's secure source
#   (the same one used for crypto keys). Unpredictable by design, cannot be seeded.
# - WHY two modules? "Looks random" and "cannot be guessed" are different goals.
#   Reproducibility is a feature in a simulation and a catastrophic bug in a password.

print("# 01. random and secrets - Introduction")
print("# ------------------------------------")

# 02. Seeding and Reproducibility
# ------------------------------------
# - random.seed(x) resets the generator to a known starting state.
# - Seed -> same numbers every run. This is what makes tests and experiments repeatable.
print("\n# 02. Seeding and reproducibility")
random.seed(42)
first_run = [random.random() for _ in range(3)]
random.seed(42)
second_run = [random.random() for _ in range(3)]
random.seed(7)
other_seed = [random.random() for _ in range(3)]
print("seed 42 run 1:", [round(v, 4) for v in first_run])
print("seed 42 run 2:", [round(v, 4) for v in second_run])
print("same?", first_run == second_run)
print("seed  7      :", [round(v, 4) for v in other_seed], "(different seed, different stream)")
print("# - Without seed(), Python seeds itself from the OS, so each run differs.")

# 03. getstate() and setstate() - Save and Replay a Stream
# ------------------------------------
# - The generator's whole internal state can be saved and restored,
#   like a bookmark in the stream of random numbers.
print("\n# 03. getstate() / setstate()")
random.seed(2024)
random.random()  # burn one value
bookmark = random.getstate()
after_bookmark = [random.randint(1, 100) for _ in range(5)]
random.setstate(bookmark)
replayed = [random.randint(1, 100) for _ in range(5)]
print("draws after bookmark:", after_bookmark)
print("replayed from bookmark:", replayed, "-> identical:", after_bookmark == replayed)

# 04. random(), uniform(), randint(), randrange()
# ------------------------------------
random.seed(1)
print("\n# 04. random() / uniform() / randint() / randrange()")
print("random()          ->", round(random.random(), 4), "(float in [0.0, 1.0): 0.0 possible, 1.0 never)")
print("uniform(10, 20)   ->", round(random.uniform(10, 20), 4), "(float between the two bounds)")
print("randint(1, 6)     ->", random.randint(1, 6), "(INCLUSIVE: 1 and 6 both possible)")
print("randrange(1, 6)   ->", random.randrange(1, 6), "(EXCLUSIVE end, like range(): 1..5 only)")
print("randrange(0, 100, 10) ->", random.randrange(0, 100, 10), "(step works: multiples of 10)")

# - Prove the inclusive/exclusive gotcha by counting what shows up
random.seed(1)
seen_randint = sorted(set(random.randint(1, 6) for _ in range(500)))
seen_randrange = sorted(set(random.randrange(1, 6) for _ in range(500)))
print("values seen from randint(1, 6)   :", seen_randint)
print("values seen from randrange(1, 6) :", seen_randrange, "<- never 6!")
print("# - Rule: randint(a, b) == randrange(a, b + 1). Pick one and be consistent.")

# - Random float in a custom range: scale random()
random.seed(1)
low, high = -5.0, 5.0
print("custom range via scaling:", round(low + (high - low) * random.random(), 4))

# 05. choice(), choices(), sample() - Picking from a Sequence
# ------------------------------------
# - choice(seq)        : ONE item
# - choices(seq, k=n)  : n items WITH replacement (repeats possible); supports weights
# - sample(seq, k=n)   : n UNIQUE items, WITHOUT replacement (like dealing cards)
random.seed(5)
colors = ["red", "green", "blue", "yellow", "purple"]
print("\n# 05. choice / choices / sample")
print("choice(colors)      ->", random.choice(colors))
print("choices(colors, k=8)->", random.choices(colors, k=8), "(repeats are normal)")
print("sample(colors, k=3) ->", random.sample(colors, k=3), "(all different)")

# - Replacement matters: choices can hand out more items than exist; sample cannot.
print("choices(colors, k=10) works :", len(random.choices(colors, k=10)), "items from only 5 colors")
try:
    random.sample(colors, k=10)
except ValueError as err:
    print("sample(colors, k=10) ->", type(err).__name__ + ":", err)

# - weights: relative likelihoods (they don't need to add up to 1)
random.seed(11)
loot = random.choices(["common", "rare", "legendary"], weights=[70, 25, 5], k=1000)
print("weighted loot drops (1000 rolls, weights 70/25/5):", dict(Counter(loot)))
random.seed(11)
cum = random.choices(["a", "b", "c"], cum_weights=[10, 20, 100], k=1000)
print("cum_weights=[10,20,100] means 10%/10%/80%:", dict(sorted(Counter(cum).items())))

# - Gotchas (sample on a set: Python 3.11+ raises TypeError; 3.9/3.10 only warned)
try:
    random.choice([])
except IndexError as err:
    print("choice([]) ->", type(err).__name__ + ":", err)
try:
    random.sample({"a", "b", "c"}, 2)  # sets aren't sequences
except TypeError as err:
    print("sample(set, 2) ->", type(err).__name__ + ":", err)
print("fix: sample(sorted(my_set), 2) ->", random.sample(sorted({"a", "b", "c"}), 2), "(sort first so seeding stays reproducible)")
print("sample from range is memory-friendly:", random.sample(range(1_000_000), 3), "(does not build a million-item list)")

# 06. shuffle() vs sample() - In Place vs New List
# ------------------------------------
# - shuffle(x) rearranges x IN PLACE and returns None.
# - sample(x, len(x)) returns a NEW shuffled list and leaves x untouched.
random.seed(3)
print("\n# 06. shuffle (in place) vs sample (new list)")
deck_a = [1, 2, 3, 4, 5, 6]
result = random.shuffle(deck_a)
print("shuffle() returned:", result, "<- None! (classic bug: x = random.shuffle(x))")
print("deck_a after shuffle:", deck_a)
original = [1, 2, 3, 4, 5, 6]
shuffled_copy = random.sample(original, len(original))
print("sample(original, len(original)) ->", shuffled_copy, "| original untouched:", original)
try:
    random.shuffle("abc")  # strings are immutable
except TypeError as err:
    print("shuffle('abc') ->", type(err).__name__, "(immutable sequences can't be shuffled in place)")
print("shuffle a string via list:", "".join(random.sample("abcdef", 6)))

# 07. Distributions - A Tiny Text Histogram
# ------------------------------------
# - random can draw from many statistical distributions, not just "flat" ones.
# - We bucket 5000 draws and print bars so you can SEE the shape.


def text_histogram(values, bins=10, lo=None, hi=None, width=40):
    """Print a horizontal histogram. Values outside [lo, hi) are ignored."""
    lo = min(values) if lo is None else lo
    hi = max(values) if hi is None else hi
    step = (hi - lo) / bins
    counts = [0] * bins
    for v in values:
        idx = int((v - lo) / step)
        if 0 <= idx < bins:
            counts[idx] += 1
    peak = max(counts) or 1
    for i, c in enumerate(counts):
        bar = "#" * round(width * c / peak)
        print(f"  {lo + i * step:7.2f} | {bar} {c}")


print("\n# 07. Distributions")
N = 5000

random.seed(100)
print("\nuniform(0, 10) - flat: every value equally likely")
text_histogram([random.uniform(0, 10) for _ in range(N)], bins=8, lo=0, hi=10)

random.seed(100)
gauss_values = [random.gauss(50, 10) for _ in range(N)]
print("\ngauss(mu=50, sigma=10) - the bell curve (heights, test scores, measurement noise)")
text_histogram(gauss_values, bins=10, lo=20, hi=80)
print(f"  sample mean = {statistics.fmean(gauss_values):.2f}, stdev = {statistics.stdev(gauss_values):.2f} (target 50, 10)")
print("  (normalvariate(mu, sigma) gives the same shape; gauss is a bit faster but not thread-safe)")

random.seed(100)
print("\ntriangular(0, 10, mode=2) - when you only know min, max and 'most likely'")
text_histogram([random.triangular(0, 10, 2) for _ in range(N)], bins=8, lo=0, hi=10)

random.seed(100)
exp_values = [random.expovariate(1 / 5) for _ in range(N)]  # lambda = 1/mean
print("\nexpovariate(1/5) - waiting times between random events (mean ~ 5 minutes between calls)")
text_histogram(exp_values, bins=8, lo=0, hi=24)
print(f"  sample mean = {statistics.fmean(exp_values):.2f} (target 5)")

random.seed(100)
print("\nbetavariate(2, 5) - values between 0 and 1 (probabilities, conversion rates)")
text_histogram([random.betavariate(2, 5) for _ in range(N)], bins=8, lo=0, hi=1)

# 08. random.Random() - Independent Instances
# ------------------------------------
# - The module-level functions (random.random(), ...) share ONE hidden global generator.
#   Any library that calls random.seed() or draws numbers disturbs your stream.
# - random.Random(seed) gives you your own private generator - isolated and reproducible.
print("\n# 08. random.Random() - independent generators")
rng_a = random.Random(99)
rng_b = random.Random(99)
print("rng_a:", [rng_a.randint(1, 100) for _ in range(5)])
print("rng_b:", [rng_b.randint(1, 100) for _ in range(5)], "(same seed -> same stream, independently)")
rng_c = random.Random(100)
random.seed(0)
random.random()  # touching the global generator...
print("rng_c is unaffected by the global one:", [rng_c.randint(1, 100) for _ in range(5)])
print("# - Pattern: pass an rng into functions (def simulate(rng): ...) so tests can inject a seeded one.")


def roll_dice(rng, n=3, sides=6):
    return [rng.randint(1, sides) for _ in range(n)]


print("roll_dice(Random(8)) twice ->", roll_dice(random.Random(8)), roll_dice(random.Random(8)))

# 09. randbytes() and getrandbits() (Python 3.9+)
# ------------------------------------
print("\n# 09. randbytes() / getrandbits()")
if sys.version_info >= (3, 9):
    rng = random.Random(1)
    print("randbytes(4) ->", rng.randbytes(4).hex(), "(seeded, so reproducible; NOT secure)")
    print("type:", type(rng.randbytes(4)).__name__)
else:
    print("[skip] randbytes needs Python 3.9+")
print("getrandbits(8) ->", random.Random(1).getrandbits(8), "(an int with 8 random bits: 0..255)")

# 10. Why random is NOT Secure
# ------------------------------------
# - Mersenne Twister is deterministic: after seeing 624 consecutive 32-bit outputs
#   an attacker can reconstruct the full internal state and predict EVERY future value.
# - Even weak seeds (like the time of day) can be brute-forced.
# - So: never use random for passwords, tokens, session IDs, reset links, API keys.
print("\n# 10. random is predictable (demo)")
victim = random.Random(12345)
state = victim.getstate()
guess = random.Random()
guess.setstate(state)  # an attacker who learns the state...
actual_next = [victim.randint(0, 9) for _ in range(6)]
predicted_next = [guess.randint(0, 9) for _ in range(6)]
print("victim's next 6 'random' digits :", actual_next)
print("attacker's prediction           :", predicted_next, "-> identical:", actual_next == predicted_next)
print("# - Real attacks recover the state from observed outputs; the point: it is just math.")

# 11. secrets - Cryptographically Strong Randomness
# ------------------------------------
# - Uses os.urandom / the OS entropy pool. No seed, not reproducible, not predictable.
# - Output differs every run, so we print LENGTHS and TYPES, never the values.
print("\n# 11. secrets - tokens, choice, randbelow")
hex_tok = secrets.token_hex(16)
url_tok = secrets.token_urlsafe(16)
raw_tok = secrets.token_bytes(16)
print("token_hex(16)     -> str of", len(hex_tok), "hex chars (16 bytes = 32 hex digits) e.g. password reset code")
print("token_urlsafe(16) -> str of", len(url_tok), "chars (base64url, safe inside URLs) e.g. magic-link tokens")
print("token_bytes(16)   -> bytes of length", len(raw_tok), "(raw material for keys)")
print("token_hex() default size is", len(secrets.token_hex()) // 2, "bytes (a sensible modern default)")
print("two tokens equal? ->", secrets.token_hex(16) == secrets.token_hex(16), "(never, in practice)")
print("secrets.randbelow(10) -> int in 0..9:", 0 <= secrets.randbelow(10) < 10, "(exclusive upper bound, like randrange)")
print("secrets.choice('abc') -> one of the characters:", secrets.choice("abc") in "abc")
print("secrets.randbits(8)   -> int below 256:", secrets.randbits(8) < 256)
try:
    secrets.SystemRandom().seed(1)
    print("SystemRandom().seed() is silently ignored - you cannot make it reproducible")
except Exception as err:
    print("seed error:", err)

# 12. compare_digest() - Timing-Safe Comparison
# ------------------------------------
# - Normal == stops at the FIRST differing character. An attacker can measure
#   tiny response-time differences to guess a secret character by character.
# - secrets.compare_digest takes the same time however much matches.
# - Use it for tokens, API keys, password hashes, HMAC signatures.
print("\n# 12. compare_digest()")
stored_token = "a1b2c3d4e5f6"
print("equal strings    ->", secrets.compare_digest(stored_token, "a1b2c3d4e5f6"))
print("different strings->", secrets.compare_digest(stored_token, "a1b2c3d4e5f7"))
print("bytes also work  ->", secrets.compare_digest(b"abc", b"abc"))
try:
    secrets.compare_digest("café", "cafe")  # non-ASCII str is not allowed
except TypeError as err:
    print("non-ASCII str ->", type(err).__name__ + ":", err)
print("fix: encode first ->", secrets.compare_digest("café".encode(), "café".encode()))


def check_api_key(provided, expected):
    """Compare in constant time (accepts str or bytes, str encoded as UTF-8)."""
    return secrets.compare_digest(str(provided).encode(), str(expected).encode())


print("check_api_key('s3cret', 's3cret') ->", check_api_key("s3cret", "s3cret"))
print("check_api_key('s3cret', 'guess!') ->", check_api_key("s3cret", "guess!"))

# 13. Safe Password and Token Generator
# ------------------------------------
print("\n# 13. Safe password / token generator")


def make_password(length=16):
    """Random password with at least 1 lower, 1 upper, 1 digit and 1 symbol."""
    if length < 8:
        raise ValueError("password length must be >= 8")
    symbols = "!@#$%^&*-_"
    alphabet = string.ascii_letters + string.digits + symbols
    while True:  # re-roll until every character class appears (fast: usually 1-2 tries)
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd) and any(c in symbols for c in pwd)):
            return pwd


def entropy_bits(length, alphabet_size):
    return length * math.log2(alphabet_size)


pwd = make_password(16)
checks = {
    "length 16": len(pwd) == 16,
    "has lower": any(c.islower() for c in pwd),
    "has upper": any(c.isupper() for c in pwd),
    "has digit": any(c.isdigit() for c in pwd),
    "has symbol": any(c in "!@#$%^&*-_" for c in pwd),
}
print("generated password checks (value itself not printed):", checks)
print("approx entropy of a 16-char password from 72 symbols:", round(entropy_bits(16, 72), 1), "bits")
print("a 4-word passphrase from a 2048-word list:", round(entropy_bits(4, 2048), 1), "bits")
try:
    make_password(4)
except ValueError as err:
    print("make_password(4) ->", err)

# - Passphrase: easier for humans to remember, still strong
words = ["apple", "river", "stone", "cloud", "tiger", "maple", "ocean", "ember", "frost", "lunar"]
passphrase = "-".join(secrets.choice(words) for _ in range(4))
print("passphrase has 4 words:", len(passphrase.split("-")) == 4, "(toy 10-word list for demo; use thousands of words in real life)")

# - Token with prefix for an API key
api_key = "sk_" + secrets.token_urlsafe(24)
print("api key looks like 'sk_...' with length", len(api_key))

# 14. Which Module for Which Job?
# ------------------------------------
#   Job                                        Use                         Why
#   ----------------------------------------   -------------------------   ----------------------------------
#   Password, API key, reset token, session id secrets                     unpredictable, OS entropy
#   CSRF token / OTP / invite code             secrets                     same
#   Compare a token/secret from a user         secrets.compare_digest      timing-safe
#   Shuffle a deck, dice, game events          random                      fast, can seed for replay
#   Unit tests needing "random" data           random.Random(seed)         reproducible failures
#   Simulations, bootstrap, A/B splits         random.Random(seed)         repeatable experiments
#   Machine learning / big numeric arrays      numpy.random.Generator      fast, vectorized, see below
#   Unique IDs without secrecy                 uuid.uuid4()                standard format (also random-based)
#   Fair lottery with real money at stake      secrets.SystemRandom        auditable-quality randomness
#
# - Rule of thumb: if a guessed value could hurt someone -> secrets. Else -> random.
print("\n# 14. Which module for which job? (see the table in the comments above)")

# 15. Realistic Example - Shuffling and Dealing a Deck
# ------------------------------------
print("\n# 15. Shuffle and deal a deck")
ranks = [str(n) for n in range(2, 11)] + list("JQKA")
suits = ["S", "H", "D", "C"]
deck = [r + s for s in suits for r in ranks]
rng = random.Random(2025)
rng.shuffle(deck)
hands = {name: [deck.pop() for _ in range(5)] for name in ("Ann", "Raj", "Mei")}
for name, hand in hands.items():
    print(f"  {name}: {' '.join(hand)}")
print("  cards left in deck:", len(deck), "| no duplicates dealt:", len(set(sum(hands.values(), []))) == 15)

# 16. Realistic Example - Dice Simulation
# ------------------------------------
# - Roll two dice 60000 times and compare with theory (7 is the most common sum).
print("\n# 16. Dice simulation (two dice, 60000 rolls)")
rng = random.Random(7)
sums = Counter(rng.randint(1, 6) + rng.randint(1, 6) for _ in range(60_000))
for total in range(2, 13):
    ways = 6 - abs(total - 7)
    expected = 60_000 * ways / 36
    bar = "#" * round(sums[total] / 400)
    print(f"  {total:2}: {sums[total]:5} (theory {expected:7.0f}) {bar}")

# 17. Realistic Example - Monte Carlo: Estimating Pi
# ------------------------------------
print("\n# 17. Monte Carlo estimate of pi")
rng = random.Random(1)
n = 200_000
inside = sum(1 for _ in range(n) if rng.random() ** 2 + rng.random() ** 2 <= 1)
print(f"  pi ~ {4 * inside / n:.4f} from {n} random points (true 3.14159...)")

# 18. Realistic Example - A/B Test Split
# ------------------------------------
# - Randomly assign users to groups. A seeded Random makes the assignment auditable.
print("\n# 18. A/B split")
users = [f"user{i:03d}" for i in range(1, 21)]
rng = random.Random(314)
shuffled = users[:]
rng.shuffle(shuffled)
half = len(shuffled) // 2
group_a, group_b = sorted(shuffled[:half]), sorted(shuffled[half:])
print("  group A:", group_a)
print("  group B:", group_b)
print("  all assigned exactly once:", sorted(group_a + group_b) == users)
# - Weighted variant: 90% control / 10% experiment, per user
rng = random.Random(314)
assignments = Counter(rng.choices(["control", "experiment"], weights=[90, 10], k=1000))
print("  90/10 split on 1000 users:", dict(assignments))

# 19. Realistic Example - Bootstrap Sample
# ------------------------------------
# - Bootstrap: resample your data WITH replacement many times to see how much a
#   statistic (the mean) would wobble. Gives a confidence interval with no formulas.
print("\n# 19. Bootstrap confidence interval for the mean")
sample_data = [23, 29, 31, 35, 36, 38, 41, 42, 45, 48, 52, 55]
rng = random.Random(99)
boot_means = sorted(statistics.fmean(rng.choices(sample_data, k=len(sample_data))) for _ in range(2000))
low, high = boot_means[int(0.025 * 2000)], boot_means[int(0.975 * 2000)]
print(f"  sample mean = {statistics.fmean(sample_data):.2f}")
print(f"  95% bootstrap interval for the mean: [{low:.2f}, {high:.2f}]")
print("  (choices = with replacement - exactly what bootstrapping needs; sample would be wrong here)")

# 20. NumPy's Generator
# ------------------------------------
# - For large arrays and data science, use NumPy: numpy.random.default_rng(seed)
#   returns a Generator that makes millions of numbers in one vectorized call.
# - See 07-NumPy/07-Random-Module.py in this repo for the full NumPy version
#   (seeding, shuffling arrays, distributions, reproducible experiments).
print("\n# 20. NumPy's Generator")
print("# - Big numeric work -> numpy.random.default_rng(seed). See 07-NumPy/07-Random-Module.py")

# 21. Recap
# ------------------------------------
print("\n# 21. Recap")
print("- seed() for reproducibility; Random(seed) for isolated streams")
print("- randint is inclusive, randrange is exclusive; shuffle returns None")
print("- choices = with replacement (weights ok); sample = without")
print("- random is predictable -> passwords/tokens need secrets")
print("- compare secrets with compare_digest, not ==")
