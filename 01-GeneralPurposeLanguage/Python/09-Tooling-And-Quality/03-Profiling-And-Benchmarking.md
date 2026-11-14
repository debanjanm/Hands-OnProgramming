# Profiling and Benchmarking — Notes

## What this covers
How to find out what is slow (and what uses memory) before changing anything: `timeit`, `perf_counter`, `cProfile`/`pstats`, `tracemalloc`, and the order in which to optimize.

## Key points
- **Workflow:** make it correct (with a test) -> measure on a realistic input -> profile to find the hot spot -> change ONE thing -> re-measure -> stop when fast enough.
- **Benchmark** = how fast is this snippet / which of two versions is faster (`timeit`). **Profile** = where does the whole program spend time (`cProfile`).
- Time with `time.perf_counter()` (monotonic, for durations), never `time.time()`. `process_time()` counts CPU time only (sleeping does not count).
- `timeit.timeit(...)` returns the **total** for all `number` runs: divide to get per-call. `Timer.repeat()` returns a list; take the **min** — noise only ever makes a run slower.
- `setup=` runs once and is not timed. `globals=globals()` lets the statement see your functions (otherwise `NameError`). `python -m timeit` does the same from the shell.
- A small `benchmark()` helper (repeat, min, print "1.0x = fastest") makes comparisons quick. Always check both versions return the same result first.
- **cProfile columns:** `ncalls` = calls; `tottime` = time in the function's own lines (excluding what it called); `cumtime` = including callees; `percall` = divided by ncalls. Sort by `cumulative` to find the branch, by `tottime` to find the function. `print_callers('f')` shows who calls `f`.
- `python -m cProfile -o out.prof script.py` saves data; load it later with `pstats.Stats("out.prof")`.
- **tracemalloc:** `start()`, `take_snapshot()` before/after, `compare_to(old, "lineno")` shows which source lines allocated memory. `get_traced_memory()` gives `(current, peak)`; the **peak** is what crashes you.
- `sys.getsizeof` is shallow (a list of big strings reports only the pointers); sum recursively for the real size.
- Measured memory wins: `__slots__` (~1.5x smaller objects here), generators instead of lists (huge), `array('i')` vs list of ints (~10x), `sys.intern` for many repeated strings (several x).
- **Complexity:** double n; O(n) takes ~2x longer, O(n²) takes ~4x. Growth beats constant factors.
- `functools.lru_cache` trades memory for time; `cache_info()` shows hits/misses.
- **Ladder:** better algorithm/data structure -> do less work/cache -> built-ins and C-backed libraries (NumPy) -> concurrency -> micro-tweaks -> rewrite in C/Rust. Example: duplicate check O(n²) -> `set` is ~100x+ faster; a micro-tweak of the nested loop stayed quadratic.
- Other tools: `py-spy` (attach to a running process), `scalene`, `line_profiler`, `memray`, `snakeviz`, `pyinstrument`, `pytest-benchmark`.

## Gotchas (the part worth revising twice)
- One run is one noisy sample (CPU speed, background load, cold caches). Warm up, repeat, take the min; gaps under ~10–20% are usually noise.
- `timeit("2 ** 10")` measures nothing: the constant is folded at compile time.
- `timeit` switches the garbage collector off by default, so allocation-heavy code can look faster than in real life.
- The profiler slows code that makes millions of tiny calls (about 3x here) but barely touches one big C call. Trust the proportions, not the absolute times.
- A profiler only sees function calls: an `in` scan on a list shows up as `tottime` of the calling function, not as its own row.
- `gc.disable()` is not a free speed-up: cycles are never freed (leak), and gains depend on workload. Always re-enable in `finally`.
- `s += x` is only fast on a local variable (a CPython trick); `"".join(parts)` is the safe choice. `list.pop(0)` is O(n): use `deque.popleft()`.
- Never pick f-string vs `.format()` for speed: the gap is tiny. Never assert on timings in tests.

## When it matters
Before any "make it faster" change, and whenever something is slow or memory-hungry in real data. Keep the benchmark so a later change cannot silently undo the gain. Vectorization: `07-NumPy/08-Performance-And-Vectorization.py`; concurrency: `05-Python Advanced/09-Multithreading-And-Multiprocessing.py`.

## One-line recap example
```python
import timeit
print(min(timeit.repeat("x in s", "s = set(range(10_000)); x = 9_999", number=10_000, repeat=5)) / 10_000)  # min of repeats / number = per-call time
```
