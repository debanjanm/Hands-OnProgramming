import cProfile
import gc
import io
import linecache
import os
import pstats
import re
import subprocess
import sys
import tempfile
import textwrap
import time
import timeit
import tracemalloc
from array import array
from collections import deque
from functools import lru_cache

# 01. Profiling and Benchmarking - Introduction
# ------------------------------------
# - "Premature optimization is the root of all evil" (Knuth). The fix is not
#   "never optimize" - it is "never optimize by GUESSING". Measure first.
# - Humans are terrible at predicting where a program is slow. The line you
#   think is slow is usually fine; the real cost hides in a loop you forgot.
# - Two different questions, two different tools:
#     * BENCHMARKING = "how long does THIS small thing take / which of these
#       two versions is faster?"  -> timeit, time.perf_counter
#     * PROFILING    = "in my WHOLE program, WHERE does the time (or memory)
#       go?"  -> cProfile, tracemalloc
#
# The optimization workflow (print it, tape it to your monitor):
#   1. Make it CORRECT first (and have a test that proves it).
#   2. Measure the real workload (not a toy input).
#   3. Profile to find the HOT SPOT (the 5% of code that eats 90% of time).
#   4. Change ONE thing. Only one - otherwise you won't know what helped.
#   5. Re-measure. Keep the change only if the numbers really improved AND
#      the tests still pass.
#   6. Stop when it is fast enough. Faster than "enough" costs readability.
#
# - This file prints timings only in COARSE form (relative factors rounded
#   to the nearest 0.5, times to one significant digit) because exact
#   numbers change on every machine and every run. The factors are the lesson.
# - Nothing below ever *asserts* on a timing - timings are noisy facts of
#   life, not test conditions. Asserts are used only to prove two versions
#   return the SAME answer (correct first!).

print("# 01. Profiling and Benchmarking - Introduction")
print("# ------------------------------------")
print("# workflow: correct -> measure -> find hot spot -> change ONE thing -> re-measure")


# Helpers used by the whole file ---------------------------------------
def coarse_x(ratio):
    """Format a speed ratio coarsely so output is stable run to run."""
    if ratio >= 100:
        return ">=100x"
    if ratio >= 10:
        return f"{round(ratio / 5) * 5:.0f}x"
    return f"{round(ratio * 2) / 2:.1f}x"


def one_sig(value):
    """Round to one significant digit (3.7 -> 4, 0.0042 -> 0.004)."""
    return float(f"{value:.1g}")


def fmt_time(seconds):
    """~2 us, ~30 ms ... one significant digit, unit chosen automatically."""
    for unit, scale in (("s", 1), ("ms", 1e3), ("us", 1e6), ("ns", 1e9)):
        value = seconds * scale
        if value >= 1:
            return f"~{one_sig(value):g} {unit}"
    return "~0 ns"


def fmt_size(num_bytes):
    """~4 MiB / ~300 KiB / ~50 B - one significant digit."""
    if num_bytes >= 1024 ** 2:
        return f"~{one_sig(num_bytes / 1024 ** 2):g} MiB"
    if num_bytes >= 1024:
        return f"~{one_sig(num_bytes / 1024):g} KiB"
    return f"~{one_sig(num_bytes):g} B"


def run_py(args, cwd):
    """Run `python <args>` in a child process with no bytecode files."""
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, *args], capture_output=True, text=True,
        cwd=cwd, timeout=120, env=env,
    )


# 02. Manual Timing with time.perf_counter
# ------------------------------------
# - time.time() is the wall clock and can jump (NTP, daylight saving).
#   time.perf_counter() is a monotonic, high-resolution clock made for
#   measuring DURATIONS. Always use perf_counter (or process_time for CPU
#   time only) to time code.
# - perf_counter's absolute value is meaningless - only DIFFERENCES matter.

print("\n# 02. Manual Timing with time.perf_counter")


def work():
    return sum(i * i for i in range(20_000))


start = time.perf_counter()
result = work()
elapsed = time.perf_counter() - start
print("result:", result)
print("one run took:", fmt_time(elapsed))

# - GOTCHA: ONE run is a single noisy sample. The first run can be slower
#   (cold caches, lazy imports); a background process can steal the CPU.
#   That is why benchmarking tools repeat the measurement many times.
samples = []
for _ in range(7):
    t0 = time.perf_counter()
    work()
    samples.append(time.perf_counter() - t0)
print("7 runs, slowest / fastest:", coarse_x(max(samples) / min(samples)),
      "<- same code, same input: this is noise")

# - perf_counter measures wall time (includes waiting). process_time()
#   measures only CPU time of this process (no sleeping). Compare:
t_wall = time.perf_counter()
t_cpu = time.process_time()
time.sleep(0.05)
print("sleep(0.05): wall time passed =", time.perf_counter() - t_wall > 0.04,
      "| CPU time barely moved =", time.process_time() - t_cpu < 0.04)


# A reusable context-manager timer for quick "how long did this block take"
class Stopwatch:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc):
        self.elapsed = time.perf_counter() - self.start


with Stopwatch() as sw:
    work()
print("Stopwatch context manager measured:", fmt_time(sw.elapsed))

# 03. timeit - the Right Way to Micro-Benchmark
# ------------------------------------
# - timeit runs a tiny piece of code MANY times in a tight loop, with the
#   garbage collector switched OFF by default, using perf_counter.
# - timeit.timeit(stmt, setup, number)   -> TOTAL seconds for `number` runs
#   (divide by number to get per-call time!).
# - timeit.repeat(...) / Timer.repeat()   -> a LIST of totals, one per repeat.
# - Timer.autorange()                     -> picks `number` for you so the
#   whole loop takes at least 0.2 seconds.

print("\n# 03. timeit - the Right Way to Micro-Benchmark")

number = 20_000
total = timeit.timeit("sum(range(100))", number=number)
print("timeit() returns the TOTAL for all runs, so per call =",
      fmt_time(total / number))

# `setup` runs ONCE, is NOT timed. Put data creation there.
total = timeit.timeit("d[k]", setup="d = {i: i for i in range(1000)}; k = 500",
                      number=number)
print("dict lookup (setup builds the dict once):", fmt_time(total / number))

# Timer.repeat: run the whole measurement several times -> list of totals
timer = timeit.Timer("sum(range(100))")
runs = timer.repeat(repeat=5, number=number)
print("Timer.repeat(repeat=5) returned a list of", len(runs), "totals")

# WHY take the MIN of the repeats (not the mean)?
# - Noise from other processes only ever makes a run SLOWER, never faster.
#   So the fastest repeat is the closest to "what the code really costs";
#   slower ones contain extra junk that is not your code's fault.
# - The docs of timeit say exactly this: use min(), not mean/std-dev.
print("fastest repeat is the 'true cost'; slowest/fastest =",
      coarse_x(max(runs) / min(runs)), "(extra time = noise, not your code)")

# Timer.autorange chooses `number` itself
n_auto, t_auto = timeit.Timer("sum(range(100))").autorange()
print("autorange picked a loop count of the form 1/2/5 x 10^k:",
      n_auto in {m * 10 ** k for m in (1, 2, 5) for k in range(0, 9)})

# `globals=` lets the timed code see names from YOUR module. Without it
# the statement runs in an empty namespace.


def square(x):
    return x * x


try:
    timeit.timeit("square(7)", number=10)  # no globals -> NameError
except NameError as err:
    print("without globals= ->", type(err).__name__, "(timeit can't see your functions)")

total = timeit.timeit("square(7)", globals=globals(), number=number)
print("with globals=globals():", fmt_time(total / number), "per call")

# A callable also works - handy for lambdas, and no string-quoting pain
total = timeit.timeit(lambda: square(7), number=number)
print("with a lambda:", fmt_time(total / number), "per call (includes lambda call overhead)")

# GOTCHA 1: constant folding. Python computes `2 ** 10` ONCE at compile
# time, so timing it measures an empty loop, not exponentiation.
t_const = timeit.timeit("2 ** 10", number=number)
t_var = timeit.timeit("a ** b", setup="a = 2; b = 10", number=number)
print("`2 ** 10` (folded at compile time) vs `a ** b`:",
      coarse_x(t_var / t_const), "slower with variables - the first was never really computing!")

# GOTCHA 2: timeit turns the garbage collector OFF during timing. Code that
# allocates lots of container objects may be slower in real life. To include
# GC use setup="gc.enable()".
print("GC enabled during a normal timeit run?  False (that's timeit's default)")

# GOTCHA 3: the command-line form `python -m timeit` picks number/repeat for
# you (autorange) and prints "best of 5". Same tool, zero script needed.
with tempfile.TemporaryDirectory() as tmp:
    proc = run_py(["-m", "timeit", "-s", "d = list(range(100))", "sum(d)"], tmp)
    line = proc.stdout.strip()
    line = re.sub(r"^\d+ loops", "N loops", line)
    line = re.sub(r"[\d.]+ (nsec|usec|msec|sec)", r"T \1", line)
    print("$ python -m timeit -s 'd = list(range(100))' 'sum(d)'")
    print(" ", line)

# 04. A Reusable benchmark() Helper
# ------------------------------------
# - Comparing two snippets is the most common thing you do. Wrap the
#   boring part: repeat each candidate, take the min, print how much slower
#   each is than the winner (1.0x = the winner).
# - It does not assert - it just shows you the numbers.

print("\n# 04. A Reusable benchmark() Helper")
print("# benchmark(title, {label: callable}) -> min of repeats, relative speed, 1.0x = winner")


def benchmark(title, candidates, number=1000, repeat=5):
    """candidates: {label: zero-arg callable}. Prints per-call time and
    relative speed (1.0x = fastest). Returns {label: seconds_per_call}."""
    results = {}
    for label, fn in candidates.items():
        # min over repeats = least noisy estimate (see section 03)
        results[label] = min(timeit.repeat(fn, number=number, repeat=repeat)) / number
    fastest = min(results.values())
    print(f"\n{title}")
    for label, secs in results.items():
        print(f"  {label:<26}{fmt_time(secs):>10}/call  {coarse_x(secs / fastest):>6}")
    return results


# 05. Micro-Benchmarks - Concrete Comparisons
# ------------------------------------
# - Each comparison first checks both versions give the SAME answer.

print("\n# 05. Micro-Benchmarks - Concrete Comparisons")

# 05a. string concatenation in a loop vs join
parts = [str(i) for i in range(2_000)]


def concat_plus():
    s = ""
    for p in parts:
        s += p  # CPython often optimizes this in place when `s` is a local...
    return s


class Holder:
    s = ""


def concat_plus_attr():
    h = Holder()
    h.s = ""
    for p in parts:
        h.s = h.s + p  # ...but NOT when the string lives somewhere else
    return h.s


def concat_join():
    return "".join(parts)


assert concat_plus() == concat_plus_attr() == concat_join()
benchmark("string building (2000 pieces):", {
    "s += p (local variable)": concat_plus,
    "h.s = h.s + p (attribute)": concat_plus_attr,
    "''.join(parts)": concat_join,
}, number=200)
print("  -> join wins. `+=` on a plain local variable is rescued by a CPython trick")
print("     (it grows the string in place); when the string lives in an attribute, a")
print("     dict or a list slot the trick is off and every + copies the whole string.")
print("     join builds the result once - the portable, always-fast choice.")

# 05b. list.pop(0) vs deque.popleft()
N_POP = 20_000


def list_pop0():
    data = list(range(N_POP))
    while data:
        data.pop(0)  # shifts EVERY remaining element one step left: O(n)


def deque_popleft():
    data = deque(range(N_POP))
    while data:
        data.popleft()  # O(1): a deque is built for both ends


benchmark(f"remove from the FRONT, {N_POP} items:", {
    "list.pop(0)": list_pop0,
    "deque.popleft()": deque_popleft,
}, number=3, repeat=3)
print("  -> same result, but a queue needs a deque (see 06-Standard Library/01-Collections-Module.py)")

# 05c. membership: `in` on a list vs a set
sizes = [1_000, 10_000]
for size in sizes:
    as_list = list(range(size))
    as_set = set(as_list)
    needle = size - 1  # worst case for the list: the last element
    assert (needle in as_list) == (needle in as_set)
    benchmark(f"`needle in container`, {size} items (worst case):", {
        "x in list  (O(n) scan)": lambda: needle in as_list,
        "x in set   (O(1) hash)": lambda: needle in as_set,
    }, number=2_000)
print("  -> list gets 10x slower with 10x data; the set stays flat.")

# 05d. f-string vs str.format vs % formatting
name, age = "Asha", 31


def fstring():
    return f"{name} is {age} years old"


def dot_format():
    return "{} is {} years old".format(name, age)


def percent():
    return "%s is %d years old" % (name, age)


assert fstring() == dot_format() == percent()
benchmark("string formatting:", {
    "f-string": fstring,
    "str.format()": dot_format,
    "% operator": percent,
}, number=50_000)
print("  -> the gap is tiny. Pick the readable one (f-string). NEVER choose a")
print("     formatting style for speed - this is the classic micro-optimization trap.")

# 06. Noise, Warm-up and Fair Comparisons
# ------------------------------------
# - Why the same code gives different numbers every run:
#     * CPU frequency scaling / turbo boost / thermal throttling
#     * other processes (browser, indexer, antivirus) stealing cores
#     * CPU caches: first touch of data is slower than the 10th
#     * Python itself: lazy imports, specialised bytecode warming up (3.11+
#       adaptive interpreter), memory allocator warming up
# - Defences:
#     * WARM UP: call the function once (untimed) before measuring.
#     * REPEAT several times, take the MIN (section 03).
#     * Close heavy apps; plug in a laptop; do not benchmark on battery.
#     * Use the SAME input for the candidates you compare.
#     * Compare RATIOS on the same machine, in the same run - never compare
#       today's absolute numbers with last month's.
#     * Beware 'the interpreter warmed up on candidate A for free' - run
#       the candidates in alternating order if the difference is small.

print("\n# 06. Noise, Warm-up and Fair Comparisons")
work()  # warm-up call: not timed
spread = timeit.repeat(work, number=50, repeat=7)
print("7 repeats of the SAME code, slowest / fastest:", coarse_x(max(spread) / min(spread)))
print("-> differences below ~10-20% between two candidates are usually noise.")
print("   If the gap is that small, you have not found anything worth changing.")

# 07. cProfile - Where Does the Time Go in a Whole Program?
# ------------------------------------
# - A benchmark tells you how fast ONE snippet is. A PROFILER watches your
#   whole program run and records, per function: how many times it was
#   called and how much time was spent inside it.
# - cProfile is in the standard library, written in C (low overhead).
# - Below is a deliberately slow program: it reads "records", normalizes
#   them, and removes duplicates with a list membership test (O(n^2)).


def normalize(text):
    return text.strip().lower()


def parse_line(line):
    return normalize(line.split(",")[0])


def load(lines):
    return [parse_line(line) for line in lines]


def slow_unique(keys):
    seen = []
    for key in keys:
        key = normalize(key)
        if key not in seen:  # <- the hot spot: scans the whole list every time
            seen.append(key)
    return seen


def make_lines(count):
    # ~half of the lines repeat an earlier value, with messy case/spaces
    return [f"  User{(i * 7) % (count // 2)}  ,payload,{i}" for i in range(count)]


def run_pipeline(count=4_000):
    keys = load(make_lines(count))
    return len(slow_unique(keys))


print("\n# 07. cProfile - Where Does the Time Go in a Whole Program?")
print("pipeline result (unique users):", run_pipeline())

profiler = cProfile.Profile()
profiler.enable()
run_pipeline()
profiler.disable()


def sanitized_stats(stats, sort_key, limit, restriction=None):
    """pstats prints times/paths that change every run. Keep the structure
    (columns, ncalls, function names), replace the changing numbers."""
    buf = io.StringIO()
    stats.stream = buf
    stats.strip_dirs().sort_stats(sort_key)
    if restriction:
        stats.print_stats(restriction, limit)
    else:
        stats.print_stats(limit)
    text = buf.getvalue()
    out = []
    for raw in text.splitlines():
        line = raw.rstrip()
        if not line:
            continue
        if re.search(r"function calls", line):
            line = re.sub(r"[\d,]+ function calls( \([\d,]+ primitive calls\))? in [\d.]+ seconds",
                          "N function calls in T seconds", line)
        elif re.match(r"\s*\d", line):  # a data row: ncalls tottime percall cumtime percall name
            m = re.match(r"\s*(\S+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+(.*)", line)
            if m:
                ncalls, where = m.groups()
                where = re.sub(r"\.py:\d+", ".py:LINE", where)
                line = f"  {ncalls:>9}  t.ttt  t.ttt  t.ttt  t.ttt  {where}"
        out.append(line)
    return "\n".join(out)


stats = pstats.Stats(profiler)
print("\n--- sort_stats('cumulative').print_stats(6) (numbers masked, structure real) ---")
print(sanitized_stats(stats, "cumulative", 6))

print("""
How to read the columns:
  ncalls    how many times the function was called. "4000/1" style means
            total calls / primitive calls (the two differ only for recursion).
  tottime   time spent INSIDE the function's own lines, EXCLUDING functions
            it called. This is where the work really happens.
  percall   tottime / ncalls (the first 'percall').
  cumtime   time in the function INCLUDING everything it called (cumulative).
            A top-level function always has a big cumtime - that alone does
            not make it the problem.
  percall   cumtime / ncalls (the second 'percall').
  filename:lineno(function)   which function the row is about.

Rule of thumb:
  * sort by 'cumulative' to see which BRANCH of the program is expensive
  * sort by 'tottime' to see which single function is expensive itself
  * then drill down: 'cumulative' finds the neighbourhood, 'tottime'
    finds the house.""")

print("--- sort_stats('tottime'): the function that burns time by itself ---")
print(sanitized_stats(pstats.Stats(profiler), "tottime", 3))

# ncalls is the most STABLE column - a very frequent tiny function can be
# the problem just by being called a million times.
rows = pstats.Stats(profiler).stats
normalize_calls = [v[1] for k, v in rows.items() if k[2] == "normalize"][0]
print("\nnormalize() was called", normalize_calls, "times (4000 via parse_line + 4000 from slow_unique)")

# Coarse share of total time, which is the thing you actually act on
total_time = sum(v[2] for v in rows.values())
tot_by_func = {k[2]: v[2] / total_time for k, v in rows.items()}
top_name, top_share = max(tot_by_func.items(), key=lambda kv: kv[1])
print(f"biggest single consumer of tottime: {top_name}() with "
      f"~{round(top_share * 10) * 10}% of the total")
print("-> found the hot spot: `key not in seen` scans a list. Next: change ONE thing")
print("   (use a set) and re-measure. Section 15 does exactly that.")

# print_callers / print_callees: "who calls this function?"
print("\n--- print_callers('normalize'): who is responsible for those calls? ---")
buf = io.StringIO()
pstats.Stats(profiler, stream=buf).strip_dirs().print_callers("normalize")
for raw in buf.getvalue().splitlines():
    if raw.strip():
        masked = re.sub(r"\d+\.\d+", "t.ttt", raw)
        masked = re.sub(r"\.py:\d+", ".py:LINE", masked)
        print(" ", masked.rstrip())
rows = pstats.Stats(profiler).stats
(_, _, _, _, callers_of_normalize), = [v for k, v in rows.items() if k[2] == "normalize"]
for (_, _, caller_name), (n_calls, *_rest) in sorted(callers_of_normalize.items(), key=lambda kv: kv[0][2]):
    print(f"  -> {caller_name}() made {n_calls} of the calls")
print("-> print_callees('fn') is the mirror image: what does fn call?")

# Restricting the report to function names with a regex string
print("\n--- print_stats('slow_|load', 5): restrict rows with a regex ---")
print(sanitized_stats(pstats.Stats(profiler), "cumulative", 5, restriction="slow_|load"))

# 08. cProfile from the Command Line (-o file + pstats)
# ------------------------------------
# - In real life you profile a SCRIPT without editing it:
#       python -m cProfile -s cumulative myscript.py
#   or save the raw data and analyse it later (or on another machine):
#       python -m cProfile -o out.prof myscript.py
#       python -m pstats out.prof        (interactive prompt)
# - Saved .prof files can also be opened by visualisers (snakeviz, below).

print("\n# 08. cProfile from the Command Line (-o file + pstats)")
child_script = textwrap.dedent('''
    def helper(n):
        return n * 2

    def busy(count):
        total = 0
        for i in range(count):
            total += helper(i)
        return total

    def main():
        busy(50_000)
        busy(10)

    main()
''')
with tempfile.TemporaryDirectory() as tmp:
    script_path = os.path.join(tmp, "target.py")
    prof_path = os.path.join(tmp, "out.prof")
    with open(script_path, "w") as f:
        f.write(child_script)
    proc = run_py(["-m", "cProfile", "-o", prof_path, script_path], tmp)
    print("exit code of `python -m cProfile -o out.prof target.py`:", proc.returncode)
    print("profile file written:", os.path.exists(prof_path))
    loaded = pstats.Stats(prof_path)  # load the saved data
    mine = {k[2]: v for k, v in loaded.stats.items() if k[0].endswith("target.py")}
    for fname in ("main", "busy", "helper"):
        cc, nc, tt, ct, callers = mine[fname]
        print(f"  {fname:<7} ncalls={nc}")
    ranked = sorted(mine, key=lambda n: mine[n][3], reverse=True)
    print("  functions ordered by cumtime:", ranked)

# 09. Profiling Overhead - the Profiler Slows Things Down
# ------------------------------------
# - cProfile hooks every function call and return. Code that makes millions
#   of TINY calls slows down a lot under the profiler; code that does a few
#   big C-level operations barely changes.
# - Consequences:
#     * absolute times in a profile are inflated - trust the PROPORTIONS
#     * tiny functions look more expensive than they really are
#     * never profile and benchmark at the same time
# - For a sampling profiler with near-zero overhead use py-spy (section 18).

print("\n# 09. Profiling Overhead - the Profiler Slows Things Down")


def tiny(x):
    return x + 1


def many_tiny_calls():
    total = 0
    for i in range(100_000):
        total = tiny(total)
    return total


def one_big_call():
    return sum(range(2_000_000))  # one C-level call: nothing for the profiler to hook


def under_profiler(fn):
    pr = cProfile.Profile()
    t0 = time.perf_counter()
    pr.enable()
    fn()
    pr.disable()
    return time.perf_counter() - t0


def plain(fn):
    t0 = time.perf_counter()
    fn()
    return time.perf_counter() - t0


for fn in (many_tiny_calls, one_big_call):
    t_plain = min(plain(fn) for _ in range(3))
    t_prof = min(under_profiler(fn) for _ in range(3))
    print(f"  {fn.__name__:<16} profiled / unprofiled = {coarse_x(t_prof / t_plain)}")
print("-> many tiny calls get notably slower under cProfile; one big C call does not.")

# 10. tracemalloc - Where Does the MEMORY Go?
# ------------------------------------
# - Slow can also mean "memory hungry" (swapping, GC pressure, crashes in
#   a container). tracemalloc (stdlib) tracks every Python memory
#   allocation and remembers the line of code that made it.
# - Workflow: start() -> take_snapshot() before/after -> compare_to().
# - Cost: tracing slows the program (maybe 2x) - use it for investigation only.

print("\n# 10. tracemalloc - Where Does the MEMORY Go?")
tracemalloc.start()
snap_before = tracemalloc.take_snapshot()

records = [str(i) * 5 for i in range(50_000)]                    # LINE_A: list of strings
index = {text: position for position, text in enumerate(records)}  # LINE_B: dict built from them

snap_after = tracemalloc.take_snapshot()
this_file = "*" + os.path.basename(__file__)
only_mine = [tracemalloc.Filter(True, this_file)]  # ignore stdlib internals
diffs = (snap_after.filter_traces(only_mine)
         .compare_to(snap_before.filter_traces(only_mine), "lineno"))
print("top allocation lines (what the line of source is + how much it added):")
for stat in diffs[:2]:
    frame = stat.traceback[0]
    source = linecache.getline(frame.filename, frame.lineno).split("#")[0].strip()
    print(f"  {fmt_size(stat.size_diff):>10}  {source}")

# get_traced_memory() -> (current, peak). PEAK is what crashes you: memory
# that was needed for a moment and then freed still counted.
tracemalloc.reset_peak()
baseline_now, _ = tracemalloc.get_traced_memory()
temp = [0] * 2_000_000   # a big temporary: 16 MB of pointers
del temp                 # freed again...
current_now, peak_now = tracemalloc.get_traced_memory()
print("after creating and freeing a 2,000,000-item list:")
print("  current is back near the start:", current_now - baseline_now < 100_000)
print("  but the PEAK remembers it:", peak_now - baseline_now > 10_000_000)
tracemalloc.stop()


def measure_peak(builder):
    """Peak bytes needed while `builder()` runs (and keeps its result)."""
    tracemalloc.start()
    tracemalloc.reset_peak()
    obj = builder()
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    del obj
    return peak


# 11. sys.getsizeof vs Deep Size
# ------------------------------------
# - sys.getsizeof(obj) is SHALLOW: it counts the object itself, NOT the
#   things it points to. A list of 1000 big strings reports the size of
#   1000 pointers, not the strings.
# - Recursively adding up what an object refers to gives the "deep" size.

print("\n# 11. sys.getsizeof vs Deep Size")


def deep_size(obj, seen=None):
    """Sum sizes of obj and everything it references (each object once)."""
    seen = set() if seen is None else seen
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        size += sum(deep_size(k, seen) + deep_size(v, seen) for k, v in obj.items())
    elif isinstance(obj, (list, tuple, set, frozenset, deque)):
        size += sum(deep_size(item, seen) for item in obj)
    elif hasattr(obj, "__dict__"):
        size += deep_size(vars(obj), seen)
    return size


print("empty list:", sys.getsizeof([]), "bytes | one int:", sys.getsizeof(1),
      "bytes | empty str:", sys.getsizeof(""), "bytes  (64-bit CPython 3.12)")
words = [f"{i:03d}" * 300 for i in range(100)]  # 100 DIFFERENT 900-char strings
print("list of 100 different strings of 900 chars:")
print("  getsizeof (shallow):", fmt_size(sys.getsizeof(words)), "<- just the pointers!")
print("  deep_size:          ", fmt_size(deep_size(words)), "<- the real footprint")
shared = "y" * 1000
same_everywhere = [shared] * 100
print("100 references to ONE string -> deep_size counts it once:",
      fmt_size(deep_size(same_everywhere)))
print("-> tracemalloc (section 10) is the practical measure; deep_size is for explanation.")

# 12. Memory Tricks (measured, not claimed)
# ------------------------------------
# - Four classic ways to shrink memory. Each is measured with tracemalloc
#   and printed as a relative factor.

print("\n# 12. Memory Tricks (measured, not claimed)")


# 12a. __slots__: no per-instance __dict__
class PointDict:
    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


class PointSlots:
    __slots__ = ("x", "y", "z")  # fixed attributes -> no __dict__ per object

    def __init__(self, x, y, z):
        self.x, self.y, self.z = x, y, z


peak_dict = measure_peak(lambda: [PointDict(i, i, i) for i in range(50_000)])
peak_slots = measure_peak(lambda: [PointSlots(i, i, i) for i in range(50_000)])
print("50,000 points, regular class vs __slots__:", fmt_size(peak_dict), "vs", fmt_size(peak_slots),
      f"-> slots use {coarse_x(peak_dict / peak_slots)} less")
print("  has __dict__?  regular:", hasattr(PointDict(1, 2, 3), "__dict__"),
      "| slots:", hasattr(PointSlots(1, 2, 3), "__dict__"))
print("  slots price: can't add new attributes ->",
      end=" ")
try:
    PointSlots(1, 2, 3).w = 4
except AttributeError:
    print("AttributeError on p.w = 4")

# 12b. generator instead of list: don't hold what you don't need
peak_list = measure_peak(lambda: sum([i * i for i in range(500_000)]))
peak_gen = measure_peak(lambda: sum(i * i for i in range(500_000)))
print("sum of 500,000 squares, list comp vs generator expression:",
      fmt_size(peak_list), "vs", fmt_size(peak_gen),
      f"-> generator uses {coarse_x(peak_list / max(peak_gen, 1))} less")
print("  (generators also START producing immediately - see 05-Python Advanced/02-Generators.py)")

# 12c. array.array: compact typed numbers instead of a list of int objects
peak_pylist = measure_peak(lambda: list(range(1_000_000, 2_000_000)))
peak_array = measure_peak(lambda: array("i", range(1_000_000, 2_000_000)))
print("1,000,000 ints, list vs array('i'):", fmt_size(peak_pylist), "vs", fmt_size(peak_array),
      f"-> array is {coarse_x(peak_pylist / peak_array)} smaller")
print("  (a list stores a pointer + a full 28-byte int object each; an array stores raw 4-byte ints;")
print("   for big numeric data the real answer is NumPy - see 07-NumPy/)")

# 12d. interning: many equal strings -> share ONE object
# - Strings built at runtime are separate objects even when equal.
#   sys.intern() makes equal strings share a single copy (and makes ==
#   checks an identity check). Useful for millions of repeated labels.
labels = ["ok", "error", "retry", "timeout"]
peak_plain = measure_peak(lambda: ["status_" + labels[i % 4] for i in range(200_000)])
peak_interned = measure_peak(lambda: [sys.intern("status_" + labels[i % 4]) for i in range(200_000)])
print("200,000 repeated labels, plain vs sys.intern:", fmt_size(peak_plain), "vs",
      fmt_size(peak_interned), f"-> interned is {coarse_x(peak_plain / peak_interned)} smaller")
a = "".join(["sta", "tus"])
b = "".join(["sta", "tus"])
print("equal but separate objects:", a == b, a is b,
      "| after sys.intern:", sys.intern(a) is sys.intern(b))

# 13. Algorithmic Complexity - Growth Beats Constant Factors
# ------------------------------------
# - Big-O says HOW the time grows when the input grows.
#     O(n)    double the input -> about double the time
#     O(n^2)  double the input -> about FOUR times the time
# - You can see it without any theory: double n, look at the ratio.
# - A better algorithm beats any micro-tweak once n is big enough.

print("\n# 13. Algorithmic Complexity - Growth Beats Constant Factors")


def quadratic(n):
    count = 0
    for i in range(n):
        for j in range(n):
            count += 1
    return count


def linear(n):
    count = 0
    for i in range(n):
        count += 1
    return count


def best_time(fn, arg, repeat=3):
    return min(timeit.repeat(lambda: fn(arg), number=1, repeat=repeat))


def growth_table(fn, sizes):
    times = [best_time(fn, n) for n in sizes]
    ratios = [round(times[i + 1] / times[i]) for i in range(len(times) - 1)]
    return ratios


quad_ratios = growth_table(quadratic, [500, 1000, 2000])
lin_ratios = growth_table(linear, [200_000, 400_000, 800_000])
print("each step DOUBLES n; how much longer does it take (rounded)?")
print("  O(n^2) loop:", quad_ratios, "-> about 4x per doubling")
print("  O(n)   loop:", lin_ratios, "-> about 2x per doubling")
print("-> if a program that is fine at n=1,000 melts at n=100,000, this is why:")
print("   an O(n^2) piece grows 10,000x, an O(n) piece grows 100x.")

# 14. Caching - Do Not Recompute What You Already Know
# ------------------------------------
# - functools.lru_cache remembers results keyed by the arguments.
# - It trades MEMORY for TIME: perfect for pure functions (same input ->
#   same output, no side effects) called repeatedly with the same args.
# - cache_info() tells you hits, misses, size - tune maxsize from real data.

print("\n# 14. Caching - Do Not Recompute What You Already Know")
calls = {"naive": 0}


def fib_naive(n):
    calls["naive"] += 1
    return n if n < 2 else fib_naive(n - 1) + fib_naive(n - 2)


@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


assert fib_naive(24) == fib_cached(24)
print("fib(24) naive made", calls["naive"], "function calls")
print("fib(24) cached:", fib_cached.cache_info())
t_naive = min(timeit.repeat(lambda: fib_naive(22), number=1, repeat=3))
t_cached = min(timeit.repeat(lambda: (fib_cached.cache_clear(), fib_cached(22)), number=1, repeat=3))
print("fib(22) even from a cold cache: cached is", coarse_x(t_naive / t_cached), "faster")
print("-> misses = distinct arguments really computed; hits = work saved.")
print("  GOTCHAS: arguments must be hashable; the cache holds references (memory");
print("  leak risk on methods and unbounded maxsize=None); cache_clear() to reset.")

# 15. The Optimization Ladder (with a Worked Example)
# ------------------------------------
# - Climb in THIS order, and stop as soon as it is fast enough:
#     1. Better ALGORITHM / DATA STRUCTURE   (10x - 10,000x)
#     2. Do less work (cache, early exit, avoid repeated conversions)
#     3. Use built-ins / library code written in C (sum, sorted, set, NumPy)
#     4. Parallelise (threads/processes/async - only after 1-3)
#     5. Micro-optimizations (local variable lookups, tweaking syntax)
#     6. Rewrite hot loops in C/Cython/Rust/Numba (last resort)
# - Each rung down gives less and costs more readability.
#
# Worked example: "does this list contain duplicates?" (worst case: none).

print("\n# 15. The Optimization Ladder (with a Worked Example)")


def has_dupes_naive(items):  # O(n^2): compare every pair in Python
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j]:
                return True
    return False


def has_dupes_tweaked(items):  # still O(n^2): micro-optimized, `in` scans in C
    for i, item in enumerate(items):
        if item in items[i + 1:]:
            return True
    return False


def has_dupes_sorted(items):  # O(n log n): sort, then neighbours must match
    ordered = sorted(items)
    return any(a == b for a, b in zip(ordered, ordered[1:]))


def has_dupes_set(items):  # O(n): a set can't hold duplicates
    return len(set(items)) != len(items)


candidates = [has_dupes_naive, has_dupes_tweaked, has_dupes_sorted, has_dupes_set]

# Step 1: CORRECT first - all versions must agree, including the edge cases
for sample in ([], [1], [1, 1], [1, 2, 3], [3, 1, 2, 3], list(range(50)) + [7]):
    answers = {fn(sample) for fn in candidates}
    assert len(answers) == 1, (fn.__name__, sample)
print("all four versions agree on empty / single / duplicate / unique inputs")

data = list(range(2_000))  # worst case: no duplicate, so nothing returns early
results = benchmark("duplicate check on 2000 unique ints (worst case):", {
    "naive nested loops    O(n^2)": lambda: has_dupes_naive(data),
    "tweaked slice+in      O(n^2)": lambda: has_dupes_tweaked(data),
    "sorted neighbours     O(n log n)": lambda: has_dupes_sorted(data),
    "set                   O(n)": lambda: has_dupes_set(data),
}, number=1, repeat=3)
print("-> the micro-tweak helped (the scan moved into C) but it is still quadratic:")

double = list(range(4_000))
t_small = min(timeit.repeat(lambda: has_dupes_tweaked(data), number=1, repeat=3))
t_big = min(timeit.repeat(lambda: has_dupes_tweaked(double), number=1, repeat=3))
s_small = min(timeit.repeat(lambda: has_dupes_set(data), number=50, repeat=3))
s_big = min(timeit.repeat(lambda: has_dupes_set(double), number=50, repeat=3))
print("   doubling the input: tweaked takes", f"{round(t_big / t_small)}x longer",
      "| set takes", f"{round(s_big / s_small)}x longer")
print("-> THE lesson: the algorithm change (set) beat every micro-optimization")
print("   by a wide margin. Always ask 'is there a better data structure?' first.")

# Back to the profile from section 07: apply the one-line fix to the hot spot
def fast_unique(keys):
    seen = set()
    ordered = []
    for key in keys:
        key = normalize(key)
        if key not in seen:  # set lookup: O(1) instead of scanning a list
            seen.add(key)
            ordered.append(key)
    return ordered


sample_keys = load(make_lines(4_000))
assert slow_unique(sample_keys) == fast_unique(sample_keys)  # same answer, same order
benchmark("section-07 pipeline step, list vs set for `seen`:", {
    "slow_unique (list)": lambda: slow_unique(sample_keys),
    "fast_unique (set)": lambda: fast_unique(sample_keys),
}, number=3, repeat=3)
print("-> workflow complete: found it with the profiler, changed ONE thing, re-measured.")

# 16. Garbage Collection and gc.disable()
# ------------------------------------
# - Python frees most objects instantly via reference counting. The cyclic
#   garbage collector (module gc) exists only for REFERENCE CYCLES
#   (a -> b -> a) that reference counting can't free.
# - It runs automatically when many container objects have been created,
#   so allocation-heavy code pays a small tax. gc.disable() removes it.
# - CAVEATS - this is a real-world trap, not a free speed-up:
#     * disabling GC means cycles are NEVER freed -> memory leak
#     * the gain is often small, depends on the Python version, and shows up
#       only in code creating millions of long-lived containers
#     * always re-enable (try/finally) and measure on YOUR workload
#     * timeit disables GC by default (section 03) - results may flatter you

print("\n# 16. Garbage Collection and gc.disable()")


def build_many_containers():
    return [[i] for i in range(200_000)]


def timed(fn):
    t0 = time.perf_counter()
    keep = fn()
    elapsed = time.perf_counter() - t0
    del keep
    return elapsed


was_enabled = gc.isenabled()
try:
    gc.enable()
    t_gc_on = min(timed(build_many_containers) for _ in range(3))
    gc.disable()
    t_gc_off = min(timed(build_many_containers) for _ in range(3))
finally:
    if was_enabled:
        gc.enable()
print("200,000 small LIVE lists, time with GC on / GC off:", coarse_x(t_gc_on / t_gc_off),
      "(big only because every list stays alive and the collector keeps re-scanning them)")
print("  for ordinary code that frees what it allocates the gap is far smaller - measure YOUR workload")


class Node:
    pass


a_node, b_node = Node(), Node()
a_node.other, b_node.other = b_node, a_node  # a reference cycle
del a_node, b_node  # refcounts never hit zero: only the GC can free them
print("gc.collect() found unreachable cycle garbage:", gc.collect() > 0)
print("current thresholds (gen0, gen1, gen2):", gc.get_threshold())
print("-> better than disabling: gc.freeze() after startup, or reduce container churn")

# 17. Vectorization and Concurrency (Pointers)
# ------------------------------------
# - Numeric loops over big arrays: do NOT optimize the Python loop - remove
#   it. NumPy runs the loop in compiled C over a compact array.
#   See 07-NumPy/08-Performance-And-Vectorization.py for loop-vs-vectorized
#   timings and broadcasting tricks.
# - Waiting on network/files/DB: threads or asyncio overlap the waiting.
#   CPU-heavy pure Python: multiprocessing to use several cores.
#   See 05-Python Advanced/09-Multithreading-And-Multiprocessing.py and
#   05-Python Advanced/10-Async-Await.py.
# - Rule: concurrency is rung 4 of the ladder. Parallelising a bad algorithm
#   gives you a bad algorithm that uses more cores.

print("\n# 17. Vectorization and Concurrency (Pointers)")
print("numeric loops  -> 07-NumPy/08-Performance-And-Vectorization.py")
print("I/O waiting    -> 05-Python Advanced/09-Multithreading-And-Multiprocessing.py (threads)")
print("                  05-Python Advanced/10-Async-Await.py (asyncio)")
print("CPU-bound      -> multiprocessing / ProcessPoolExecutor (same file as threads)")

# 18. External Tools (Reference Only - Not Run Here)
# ------------------------------------
# - The standard library gets you far. These third-party tools are what
#   people reach for next. Install with pip (needs the network), so this
#   file just lists them.

print("\n# 18. External Tools (reference only - pip install <name>)")
tools = [
    ("py-spy", "sampling profiler: attach to a RUNNING process (even in production), no code change, tiny overhead, flame graphs"),
    ("scalene", "CPU + memory + GPU profiler, tells you Python time vs native (C) time per line"),
    ("line_profiler", "time spent PER LINE inside functions you decorate with @profile (kernprof -l -v script.py)"),
    ("memray", "memory profiler from Bloomberg: tracks native allocations, flame graphs, find leaks"),
    ("snakeviz", "browser visualiser for cProfile .prof files (sunburst / icicle charts)"),
    ("pyinstrument", "low-overhead statistical profiler with a readable call-tree report"),
    ("pytest-benchmark", "benchmarks inside your test suite, with saved results to catch regressions"),
]
for name_, purpose in tools:
    print(f"  {name_:<17}{purpose}")
print("also built in: python -X importtime script.py  (slow imports), python -m timeit, python -m cProfile")

# 19. Real-World Checklist
# ------------------------------------
# - Before touching code:
#     [ ] is it actually too slow? (a user complaint or a number, not a hunch)
#     [ ] do I have a test that pins the correct behaviour?
#     [ ] do I have a repeatable benchmark on realistic data?
# - While optimizing:
#     [ ] profile first, change ONE thing, re-measure, keep notes
#     [ ] algorithm / data structure before micro-tweaks
#     [ ] compare ratios from the same run, take min of repeats
# - After:
#     [ ] tests still pass; code still readable; comment WHY it's done that way
#     [ ] keep the benchmark so a future change can't silently undo the gain

print("\n# 19. Real-World Checklist")
print("# slow? -> test -> repeatable benchmark -> profile -> change ONE thing -> re-measure -> keep the benchmark")
