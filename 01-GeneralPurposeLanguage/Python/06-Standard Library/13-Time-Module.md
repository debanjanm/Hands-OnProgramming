# Time Module — Notes

## What this covers
The `time` module: the machine's clocks, sleeping, converting epoch seconds to calendar fields, and measuring how long code takes. `datetime` (see `02-Datetime-Module.py`) is for calendars and time zones; `time` is for clocks and stopwatches.

## Key points
- **`time.time()`** = seconds since the epoch (1970-01-01 UTC) as a float. It is the wall clock and is the same everywhere on Earth. `time_ns()` returns the exact integer nanoseconds.
- **Which clock for what**:
  - `time()` for timestamps ("what time is it?").
  - `monotonic()` for timeouts and deadlines (never goes backwards).
  - `perf_counter()` for benchmarking (highest resolution).
  - `process_time()` for CPU time used by this process (ignores sleeping).
- Monotonic and perf_counter values start from an arbitrary point. Only the **difference** means anything.
- **`sleep(s)`** pauses at least `s` seconds (can be longer). Negative values raise `ValueError`.
- **`struct_time`** has `tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst`. `gmtime()` is UTC, `localtime()` is your zone, `mktime()` converts local `struct_time` back to epoch.
- **`strftime(fmt, st)`** formats; **`strptime(text, fmt)`** parses.
- **Zones**: `time.timezone` (seconds **west** of UTC, so India is -19800), `time.tzname`, `time.daylight`. On Unix, set `os.environ["TZ"]` and call `time.tzset()` to change local time.
- **Y2038**: a signed 32-bit epoch overflows at 2038-01-19 03:14:07 UTC. Python and 64-bit systems are safe.
- **Patterns built in the file**: `format_duration` (3723 -> `1h 02m 03s` using `divmod`), a `Stopwatch` context manager and `@timed` decorator on `perf_counter`, retry with exponential backoff, a token-bucket rate limiter, `sched`, and `timeit`.
- **Inject the clock and the sleep** (`sleep=time.sleep`, `clock=time.monotonic`) so tests use a fake one and run instantly and deterministically.
- **`timeit`** runs a snippet many times, turns the garbage collector off while timing, and runs `setup` once untimed. Use `timeit.repeat(...)` and take `min()`.

## Gotchas (the part worth revising twice)
- **Never measure durations with `time.time()`.** NTP or the user can change the clock mid-run; the "duration" can even be negative.
- `os.environ["TZ"] = ...` alone does not refresh `time.timezone` / `tzname`. Call `time.tzset()`. It does not exist on Windows (`hasattr(time, "tzset")`).
- Changing `TZ` is process-wide. Prefer `datetime` with `zoneinfo` for real time-zone work.
- `strptime("09:15", "%H:%M")` fills missing parts with 1900-01-01.
- `tm_wday` starts at **Monday = 0**; `tm_mon` is 1-12.
- A float epoch only resolves about 0.24 microseconds; use `time_ns()` for finer.
- Default arguments like `sleep=time.sleep` are bound when the function is defined, so monkeypatching `time.sleep` later does nothing. Inject the function, or call `time.sleep` inside the body. If you patch, always restore it.
- `sleep` is a guess, not a wait-for-event. Use queues, events or futures when you can.
- A single run of tiny code is mostly noise; one `timeit` number alone means nothing, compare alternatives on the same machine. `timeit` is for snippets; use a profiler for whole programs.
- Don't make code logic depend on timing values (flaky tests); print or compare, don't assert on speed.

## When it matters
Timeouts and deadlines, retrying flaky network calls politely, rate limiting an API client, logging timestamps, and quick "which version is faster?" checks.

## One-line recap example
```python
import time
start = time.perf_counter(); time.sleep(0.01)
print(f"took {time.perf_counter() - start:.3f}s")   # use perf_counter/monotonic for durations, time() for timestamps
```
