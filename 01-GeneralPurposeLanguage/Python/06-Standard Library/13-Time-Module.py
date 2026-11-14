import time
import os
import sys
import math
import gc
import random
import sched
import timeit
from functools import wraps

# 01. time Module - Introduction
# ------------------------------------
# - time = the machine's CLOCKS: "what moment is it?" and "how long did that take?"
# - datetime (see 02-Datetime-Module.py) = human CALENDARS: dates, time zones,
#   date arithmetic like "3 weeks from Tuesday".
# - Quick rule:
#     calendar / dates / zones / "show this to a user"  -> datetime
#     epoch seconds / stopwatch / sleeping / benchmarks -> time
# - The time module is a thin wrapper over the C library, so some behaviour
#   (time zones, tzset, clock resolution) depends on your operating system.
# - Several demos need the SAME answer on every machine, so we pin the local
#   time zone to UTC where it matters (and restore it at the end).

print("# 01. time Module - Introduction")
print("# ------------------------------------")

HAS_TZSET = hasattr(time, "tzset")  # not available on Windows
ORIGINAL_TZ = os.environ.get("TZ")  # remember, so we can restore it at the end


def set_tz(tz_name):
    """Change the process's local time zone (Unix only). Returns True if applied."""
    if not HAS_TZSET:
        return False
    os.environ["TZ"] = tz_name
    time.tzset()  # re-read TZ; without this the old zone stays cached
    return True


def restore_tz():
    if not HAS_TZSET:
        return
    if ORIGINAL_TZ is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = ORIGINAL_TZ
    time.tzset()


set_tz("UTC")  # deterministic local time for the printed examples below

# 02. time.time() - The Epoch Clock
# ------------------------------------
# - Seconds since the "epoch": 1970-01-01 00:00:00 UTC, as a float.
# - Same number everywhere on Earth - it is NOT local time.
# - It is the wall clock: the OS (or NTP, or a human) can change it at any moment.
print("\n# 02. time.time() - seconds since the epoch")
now = time.time()
print("type:", type(now).__name__)
print("it is a large number (> 1.7 billion since Nov 2023):", now > 1_700_000_000)
print("epoch 0 as a date:", time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(0)))
print("epoch 1_700_000_000 is:", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(1_700_000_000)))

# 03. time_ns() - Integer Nanoseconds
# ------------------------------------
# - A float has ~15-16 significant digits. An epoch value like 1700000000.123456789
#   uses 10 of them for the seconds, leaving only ~6 for the fraction.
# - time_ns() returns an exact INTEGER count of nanoseconds - no rounding.
print("\n# 03. time_ns() vs time()")
ns = time.time_ns()
print("time_ns() type:", type(ns).__name__, "| about 1e18 big:", ns > 10**18)
print("smallest float step at epoch scale (math.ulp):", math.ulp(1.7e9), "seconds (~0.24 microseconds)")
print("-> float epoch times can't distinguish events closer than that; ns ints can.")
print("ns // 1_000_000_000 == int(time.time()) (give or take a tick):", abs(ns // 1_000_000_000 - int(time.time())) <= 1)

# 04. Which Clock for What?
# ------------------------------------
#   Function              What it measures                          Can jump?           Use for
#   -------------------   ---------------------------------------   -----------------   ---------------------------
#   time.time()           wall clock (epoch)                        YES (NTP/user)      timestamps, logs, "now"
#   time.monotonic()      steady clock, only moves forward          never backwards     timeouts, deadlines, intervals
#   time.perf_counter()   highest-resolution steady clock           never backwards     benchmarking short code
#   time.process_time()   CPU time used by THIS process only        never backwards     "how much CPU did I burn?"
#   time.thread_time()    CPU time of the current thread            never backwards     per-thread CPU cost
#
# - Each also has an _ns twin (monotonic_ns, perf_counter_ns, ...) returning ints.
# - The numbers from monotonic/perf_counter have an ARBITRARY starting point.
#   Only the DIFFERENCE between two readings means anything.
print("\n# 04. Which clock for what? (see the table above)")
print("monotonic() value is meaningless alone; differences matter:", time.monotonic() > 0)

# 05. Why NOT time.time() for Durations
# ------------------------------------
# - If the wall clock is adjusted while you measure (NTP sync, daylight saving
#   handled by the OS, the user changing the date), your duration is garbage -
#   it can even be NEGATIVE.
# - We simulate a wall clock getting corrected by one hour mid-measurement.
print("\n# 05. time.time() can go backwards (simulated)")


class FakeWallClock:
    """A pretend wall clock we can push around. Stands in for time.time()."""

    def __init__(self, start):
        self.now = start

    def __call__(self):
        return self.now


wall = FakeWallClock(1_700_000_000.0)
start = wall()
wall.now += 2.0      # 2 seconds of real work...
wall.now -= 3600.0   # ...then NTP corrects the clock back one hour
elapsed = wall() - start
print(f"measured with the wall clock: {elapsed:+.1f} seconds  <- negative duration! nonsense")
print("monotonic() never does this; the OS guarantees it. Check it ourselves:")
previous = time.monotonic()
went_backwards = False
for _ in range(200_000):
    current = time.monotonic()
    if current < previous:
        went_backwards = True
    previous = current
print("  200,000 monotonic() readings, ever went backwards?", went_backwards)
info = time.get_clock_info("monotonic")
print("  monotonic clock: monotonic =", info.monotonic, "| adjustable =", info.adjustable)
info_wall = time.get_clock_info("time")
print("  wall clock     : monotonic =", info_wall.monotonic, "| adjustable =", info_wall.adjustable)

# 06. perf_counter and process_time - Wall Time vs CPU Time
# ------------------------------------
# - perf_counter  = real elapsed time (includes sleeping, waiting for disk/network).
# - process_time  = only time the CPU actually worked for you (NOT counting sleep/waiting).
print("\n# 06. perf_counter (wall) vs process_time (CPU)")
w0, c0 = time.perf_counter(), time.process_time()
time.sleep(0.2)  # waiting costs wall time but almost no CPU
w1, c1 = time.perf_counter(), time.process_time()
print("after sleep(0.2):   wall elapsed >= 0.2:", (w1 - w0) >= 0.2, "| CPU elapsed < wall elapsed:", (c1 - c0) < (w1 - w0))

w0, c0 = time.perf_counter(), time.process_time()
total = 0
for i in range(1_500_000):  # busy work: CPU AND wall both advance
    total += i * i
w1, c1 = time.perf_counter(), time.process_time()
print("after busy loop:    wall and CPU both advanced:", (w1 - w0) > 0 and (c1 - c0) > 0)
print("(timings vary per machine, so we print comparisons, not raw numbers)")
print("perf_counter_ns() is an int:", isinstance(time.perf_counter_ns(), int))

# 07. sleep() - Pausing Execution
# ------------------------------------
# - sleep(seconds) pauses the current thread. Fractions are allowed.
# - It guarantees AT LEAST that long, never less (Python 3.5+). It can sleep longer:
#   the OS may not wake you the instant the timer fires.
# - Never use sleep to "wait for something to finish" if you can wait on the
#   real event (threads, queues, futures) instead - sleeping is a guess.
print("\n# 07. sleep() sleeps at least as long as asked")
for requested in (0.01, 0.05, 0.1):
    t0 = time.monotonic()
    time.sleep(requested)
    slept = time.monotonic() - t0
    print(f"  requested {requested:.2f}s -> slept >= requested: {slept >= requested}")
try:
    time.sleep(-1)
except ValueError as err:
    print("sleep(-1) ->", type(err).__name__ + ":", err)
print("sleep(0) is legal: yields the CPU for a moment; returns", time.sleep(0))

# 08. struct_time - The Calendar as a Named Tuple
# ------------------------------------
# - gmtime(secs)    -> struct_time in UTC
# - localtime(secs) -> struct_time in the machine's local zone
# - Both default to "now" when called with no argument.
print("\n# 08. struct_time fields (epoch 1_700_000_000 in UTC)")
st = time.gmtime(1_700_000_000)
print(st)
fields = ["tm_year", "tm_mon", "tm_mday", "tm_hour", "tm_min", "tm_sec", "tm_wday", "tm_yday", "tm_isdst"]
for f in fields:
    print(f"  {f:9} = {getattr(st, f)}")
print("  tm_zone   =", st.tm_zone, "| tm_gmtoff =", st.tm_gmtoff)
print("  tm_wday: Monday is 0 (not Sunday!) ->", ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][st.tm_wday])
print("  tm_mon is 1-12 (not 0-11); tm_yday is 1-366")
print("  it's a tuple too: st[0] =", st[0], "| unpack first 3:", st[:3])

# 09. localtime, gmtime, mktime - Converting Between Forms
# ------------------------------------
# - mktime(struct_time) is the INVERSE of localtime(): local struct_time -> epoch.
# - calendar.timegm() is the inverse of gmtime() (UTC) - mktime assumes LOCAL time.
print("\n# 09. localtime / gmtime / mktime")
print("localtime(0) (TZ pinned to UTC):", time.localtime(0).tm_hour, ":", time.localtime(0).tm_min)
epoch = 1_700_000_000
roundtrip = time.mktime(time.localtime(epoch))
print("mktime(localtime(epoch)) == epoch:", roundtrip == epoch, "->", int(roundtrip))
# mktime normalises out-of-range values: day 32 of January becomes February 1
normalised = time.localtime(time.mktime((2024, 1, 32, 12, 0, 0, 0, 0, -1)))
print("mktime((2024, 1, 32, ...)) ->", time.strftime("%Y-%m-%d", normalised), "(day 32 rolled into February)")
print("time.ctime(0) :", time.ctime(0), "(quick human string, fixed English format)")
print("time.asctime(gmtime(86400)):", time.asctime(time.gmtime(86400)))

# 10. strftime and strptime - Formatting and Parsing
# ------------------------------------
# - strftime(format, struct_time): time -> text    ("f" = format)
# - strptime(text, format):        text -> struct_time ("p" = parse)
print("\n# 10. strftime / strptime")
st = time.gmtime(1_700_000_000)
print("strftime ISO         :", time.strftime("%Y-%m-%dT%H:%M:%S", st))
print("strftime friendly    :", time.strftime("%A, %d %B %Y, %I:%M %p", st))
print("strftime day of year :", time.strftime("day %j of %Y, week %U", st))
parsed = time.strptime("2024-03-15 14:30:05", "%Y-%m-%d %H:%M:%S")
print("strptime ->", parsed.tm_year, parsed.tm_mon, parsed.tm_mday, parsed.tm_hour, parsed.tm_min, parsed.tm_sec)
print("weekday computed for us (Mon=0):", parsed.tm_wday)
only_time = time.strptime("09:15", "%H:%M")
print("GOTCHA - missing parts get defaults: year =", only_time.tm_year, ", month =", only_time.tm_mon, ", day =", only_time.tm_mday, "(1900-01-01!)")
try:
    time.strptime("15/03/2024", "%Y-%m-%d")
except ValueError as err:
    print("format mismatch ->", type(err).__name__ + ":", err)
print("# - struct_time has no real timezone awareness; for aware date-times use datetime (see 02-Datetime-Module.py).")

# 11. Time Zones: timezone, tzname, TZ env var and tzset()
# ------------------------------------
# - time.timezone = seconds WEST of UTC (so India, east of UTC, is NEGATIVE: -19800).
# - time.tzname   = (standard name, daylight-saving name).
# - time.daylight = non-zero if the zone has a DST rule.
# - Changing os.environ["TZ"] does nothing until you call time.tzset() (Unix only).
print("\n# 11. Time zones, TZ and tzset()")
if HAS_TZSET:
    zones = [
        ("UTC", "UTC"),
        ("IST-5:30", "India (no DST, 5h30 EAST of UTC)"),
        ("EST5EDT,M3.2.0,M11.1.0", "US Eastern (DST rules)"),
    ]
    summer_epoch = 1_720_000_000   # 2024-07-03 in the northern summer
    winter_epoch = 1_705_000_000   # 2024-01-11 in the northern winter
    for tz, label in zones:
        set_tz(tz)
        s_summer = time.localtime(summer_epoch)
        s_winter = time.localtime(winter_epoch)
        print(f"TZ={tz!r}  ({label})")
        print(f"   tzname={time.tzname}  timezone={time.timezone}s  daylight={time.daylight}")
        print(f"   summer epoch -> {time.strftime('%Y-%m-%d %H:%M %Z', s_summer)} (isdst={s_summer.tm_isdst})")
        print(f"   winter epoch -> {time.strftime('%Y-%m-%d %H:%M %Z', s_winter)} (isdst={s_winter.tm_isdst})")
    print("same instant, three different clock readings - the epoch never changed, only the display zone did.")
    print("GOTCHA: the module-level variables only refresh on tzset():")
    set_tz("UTC")
    os.environ["TZ"] = "IST-5:30"  # changed the env var, but NO tzset() call
    print("   TZ env var is now IST, but time.timezone is still", time.timezone, "and tzname", time.tzname, "(stale)")
    time.tzset()
    print("   after tzset(): time.timezone =", time.timezone, "and tzname =", time.tzname)
    print("   (some platforms re-read TZ inside localtime() on their own - don't rely on it; always call tzset())")
    set_tz("UTC")
else:
    print("[skip] time.tzset() is not available on this platform (Windows).")
print("# - In real code prefer datetime + zoneinfo for zones; mutating TZ is process-wide and affects EVERYTHING.")

# 12. The Epoch and the Year 2038 Problem
# ------------------------------------
# - Old systems stored the epoch seconds in a signed 32-bit integer.
#   Max value 2**31 - 1 = 2,147,483,647 -> 2038-01-19 03:14:07 UTC. One second later it
#   wraps to a NEGATIVE number (1901). Embedded devices, old file formats, old databases suffer.
# - Python ints are unlimited, and the machine's time_t is 64-bit on modern systems,
#   so Python itself is safe for ~292 billion years.
print("\n# 12. Epoch and Y2038")
max32 = 2**31 - 1
print("2**31 - 1 =", max32, "->", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(max32)))
wrapped = max32 + 1 - 2**32  # what a signed 32-bit int would wrap to
print("one second later, a 32-bit signed int wraps to", wrapped, "->", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(wrapped)))
print("64-bit/Python is fine: gmtime(2**31) ->", time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(2**31)))
print("year 3000:", time.strftime("%Y-%m-%d", time.gmtime(32503680000)))
print("negative epochs = before 1970:", time.strftime("%Y-%m-%d", time.gmtime(-86400)))

# 13. Human-Friendly Duration Formatting
# ------------------------------------


def format_duration(seconds):
    """Turn seconds into '1h 02m 03s' style text (days if needed, ms if under 1s)."""
    if seconds < 0:
        return "-" + format_duration(-seconds)
    if seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    total = int(round(seconds))
    days, rem = divmod(total, 86_400)
    hours, rem = divmod(rem, 3_600)
    minutes, secs = divmod(rem, 60)
    if days:
        return f"{days}d {hours:02d}h {minutes:02d}m {secs:02d}s"
    if hours:
        return f"{hours}h {minutes:02d}m {secs:02d}s"
    if minutes:
        return f"{minutes}m {secs:02d}s"
    return f"{secs}s"


print("\n# 13. format_duration() helper")
cases = [0.0042, 0.5, 5, 59.6, 75, 3723, 86_400 + 3_661, -90]
for sec in cases:
    print(f"  {sec:>10} -> {format_duration(sec)}")
assert format_duration(3723) == "1h 02m 03s"
assert format_duration(75) == "1m 15s"
assert format_duration(0.5) == "500ms"
print("(divmod does the heavy lifting: seconds -> minutes -> hours -> days)")

# 14. Stopwatch Context Manager and @timed Decorator
# ------------------------------------
# - perf_counter is THE right clock for measuring how long code takes.
# - A context manager (a class with __enter__/__exit__) is perfect for "time this block";
#   a decorator is perfect for "time this function every call".
# - See the OOP/Advanced folders for how decorators and context managers work in depth.


class Stopwatch:
    """with Stopwatch() as sw: ...   then sw.elapsed is the duration in seconds."""

    def __init__(self, label="block"):
        self.label = label
        self.elapsed = 0.0
        self._start = None

    def __enter__(self):
        self._start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.elapsed = time.perf_counter() - self._start  # runs even if the block raised
        return False  # do NOT swallow exceptions


def timed(func):
    """Decorator: records how long each call took in func.timings (and keeps the name/docstring)."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:  # still record the time when the function raises
            wrapper.timings.append(time.perf_counter() - start)
    wrapper.timings = []
    return wrapper


print("\n# 14. Stopwatch and @timed")
with Stopwatch("sleepy") as sw:
    time.sleep(0.03)
print(f"Stopwatch measured the sleep: >= 0.03s -> {sw.elapsed >= 0.03}  (about {sw.elapsed * 1000:.0f} ms, varies)")
try:
    with Stopwatch("failing") as sw_err:
        raise RuntimeError("boom")
except RuntimeError:
    print("Stopwatch still recorded time when the block raised:", sw_err.elapsed >= 0)


@timed
def slow_square(n):
    """Square n after a tiny pause."""
    time.sleep(0.01)
    return n * n


print("slow_square(7) =", slow_square(7), "| slow_square(8) =", slow_square(8))
print("recorded", len(slow_square.timings), "timings, all >= 0.01s:", all(t >= 0.01 for t in slow_square.timings))
print("decorator preserved name and docstring:", slow_square.__name__, "|", slow_square.__doc__)
print("average call:", format_duration(sum(slow_square.timings) / len(slow_square.timings)), "(varies per machine)")

# 15. Retry with Exponential Backoff (injected sleep)
# ------------------------------------
# - When a call to a flaky service fails, don't hammer it. Wait, then wait LONGER each time
#   (1s, 2s, 4s, ...). That's "exponential backoff". Adding random "jitter" stops a crowd
#   of clients from all retrying at the exact same instant.
# - Testing trick: pass the sleep function IN as a parameter. In production it is time.sleep;
#   in a test it is a fake that just records the delays, so the test finishes instantly.
print("\n# 15. Retry with exponential backoff")


def retry(func, attempts=5, base_delay=1.0, factor=2.0, max_delay=30.0, jitter=None, sleep=time.sleep):
    """Call func(); on exception wait base_delay * factor**n (capped) and try again.

    jitter: optional random.Random; if given, each wait is a random fraction (0.5-1.0) of the delay.
    sleep:  injectable so tests/demos don't really wait.
    """
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception as err:
            if attempt == attempts:
                raise  # out of attempts: let the caller see the real error
            delay = min(base_delay * factor ** (attempt - 1), max_delay)
            if jitter is not None:
                delay *= jitter.uniform(0.5, 1.0)
            print(f"  attempt {attempt} failed ({err}); waiting {delay:.2f}s")
            sleep(delay)


class Flaky:
    """Fails the first `fail_times` calls, then succeeds."""

    def __init__(self, fail_times):
        self.calls = 0
        self.fail_times = fail_times

    def __call__(self):
        self.calls += 1
        if self.calls <= self.fail_times:
            raise ConnectionError(f"server busy #{self.calls}")
        return "OK"


recorded = []
flaky = Flaky(3)
print("succeeds on 4th try, base delay 1s (sleep replaced by a recorder):")
print("  result:", retry(flaky, attempts=5, sleep=recorded.append))
print("  delays that WOULD have been slept:", recorded, "-> total", sum(recorded), "s skipped")

recorded = []
print("with jitter (seeded Random so output is repeatable):")
retry(Flaky(3), attempts=5, jitter=random.Random(42), sleep=recorded.append)
print("  delays:", [round(d, 2) for d in recorded])

print("gives up after the last attempt and re-raises:")
recorded = []
try:
    retry(Flaky(99), attempts=3, base_delay=0.5, sleep=recorded.append)
except ConnectionError as err:
    print("  final error:", err, "| delays:", recorded)

print("the delay is capped by max_delay:", [min(1 * 2.0 ** n, 10) for n in range(6)])

# - Alternative style: monkeypatch time.sleep itself for the duration of a test.
#   Catch: a default argument (sleep=time.sleep) is evaluated ONCE when retry() is defined,
#   so it keeps the REAL sleep forever. Look the function up at CALL time instead.
def retry_late_bound(func, attempts=4, base_delay=1.0):
    for attempt in range(1, attempts + 1):
        try:
            return func()
        except Exception:
            if attempt == attempts:
                raise
            time.sleep(base_delay * 2 ** (attempt - 1))  # looked up on the time module each call


real_sleep = time.sleep
patched_calls = []
time.sleep = patched_calls.append  # replace the real function for the duration of the demo
try:
    result = retry_late_bound(Flaky(2), base_delay=0.25)
finally:
    time.sleep = real_sleep  # ALWAYS restore, or every later sleep() in the process is broken
print("\nmonkeypatched time.sleep + late lookup ->", result, "| captured delays:", patched_calls)
print("restored real sleep:", time.sleep is real_sleep)
print("Prefer injection (the sleep= parameter above): explicit, no global patching, no restore needed.")

# 16. Rate Limiter - Token Bucket with an Injected Clock
# ------------------------------------
# - A token bucket allows short bursts but caps the long-run rate:
#     * bucket holds up to `capacity` tokens; every request spends 1 token
#     * tokens refill continuously at `rate` per second
#     * empty bucket -> the request is refused (or must wait)
# - It reads time from an injected clock function, so a FakeClock gives a
#   perfectly deterministic demo. In production pass time.monotonic.
print("\n# 16. Token-bucket rate limiter")


class TokenBucket:
    def __init__(self, rate, capacity, clock=time.monotonic):
        self.rate = rate
        self.capacity = capacity
        self.clock = clock
        self.tokens = float(capacity)
        self.last = clock()

    def allow(self, cost=1):
        now = self.clock()
        # refill based on how much time passed, never above capacity
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.rate)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False

    def wait_time(self, cost=1):
        """Seconds until `cost` tokens are available (0 if available now)."""
        deficit = cost - self.tokens
        return max(0.0, deficit / self.rate)


class FakeClock:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def advance(self, seconds):
        self.t += seconds


clock = FakeClock()
bucket = TokenBucket(rate=2, capacity=3, clock=clock)  # 2 tokens/second, bursts of 3
print("rate 2/s, burst 3. Sending a request every 0.1 simulated seconds:")
log = []
for i in range(12):
    ok = bucket.allow()
    log.append("ok " if ok else "NO ")
    print(f"  t={clock.t:4.1f}s request {i + 1:2}: {'allowed' if ok else 'REFUSED'}   (tokens left {bucket.tokens:.2f})")
    clock.advance(0.1)
print("pattern:", "".join(log))
print("burst of 3 goes through instantly, then throughput settles near 2/second.")
clock.advance(5)  # a long quiet period...
print("after 5 quiet seconds the bucket is full again:", bucket.allow(), bucket.allow(), bucket.allow(), "then", bucket.allow())
print("wait_time() tells a caller how long to sleep:", round(bucket.wait_time(), 2), "s")

# 17. sched - A Tiny Event Scheduler
# ------------------------------------
# - sched.scheduler runs functions at chosen times, in order, in ONE thread.
# - enter(delay, priority, func, args) = "run after delay seconds"; lower priority number wins ties.
# - run() blocks until all events are done (or cancelled).
# - It is fine for small scripts. For real apps look at threading.Timer, asyncio, APScheduler, cron.
print("\n# 17. sched - schedule events")
scheduler = sched.scheduler(time.monotonic, time.sleep)
fired = []


def fire(name):
    fired.append(name)
    print("  fired:", name)


scheduler.enter(0.06, 1, fire, ("C - after 0.06s",))
scheduler.enter(0.02, 1, fire, ("A - after 0.02s",))
scheduler.enter(0.04, 1, fire, ("B - after 0.04s",))
cancelled = scheduler.enter(0.01, 1, fire, ("X - cancelled, never runs",))
scheduler.cancel(cancelled)
print("events queued:", len(scheduler.queue), "(the cancelled one is gone)")
scheduler.run()
print("order of execution:", [name[0] for name in fired], "-> sorted by time, not by insertion order")

# - Same moment? priority decides (smaller number first)
fired.clear()
scheduler.enter(0.01, 5, fire, ("low priority (5)",))
scheduler.enter(0.01, 1, fire, ("high priority (1)",))
scheduler.run()

# - Re-scheduling itself gives a repeating job
ticks = []


def repeating(count):
    ticks.append(count)
    if count < 3:
        scheduler.enter(0.01, 1, repeating, (count + 1,))


scheduler.enter(0.01, 1, repeating, (1,))
scheduler.run()
print("self-rescheduling job ran:", ticks)

# 18. timeit - Quick Micro-Benchmarks
# ------------------------------------
# - timeit runs a snippet many times and returns total seconds. Why not just
#   subtract two time.perf_counter() calls? One run of tiny code is dominated by noise.
# - timeit helpers:
#     * uses the best clock (perf_counter) for you
#     * temporarily DISABLES the garbage collector, so a random GC pause doesn't spoil one run
#     * the `setup` code runs once and is not timed
# - Use timeit.repeat() and take min(): the fastest run is the one least disturbed by other
#   programs; averages mostly measure how busy your laptop was.
print("\n# 18. timeit")
seen_gc = []
timeit.timeit(lambda: seen_gc.append(gc.isenabled()), number=3)
print("garbage collector enabled while timeit runs?", seen_gc[0], "| enabled again afterwards?", gc.isenabled())

loops = 20_000
t_join = timeit.timeit("''.join(parts)", setup="parts = ['x'] * 100", number=loops)
t_concat = timeit.timeit("s = ''\nfor p in parts: s += p", setup="parts = ['x'] * 100", number=loops)
print(f"join  : {t_join:.4f}s for {loops} runs  (varies per machine)")
print(f"concat: {t_concat:.4f}s for {loops} runs  (varies per machine)")
print("-> a number alone is meaningless; compare the two alternatives on the SAME machine.")

runs = timeit.repeat("sum(range(1000))", number=2_000, repeat=5)
print("repeat() returns one total per repeat:", len(runs), "values | best (min) =", f"{min(runs):.4f}s", "(varies)")
per_call_us = min(runs) / 2_000 * 1e6
print(f"per call about {per_call_us:.1f} microseconds (varies)")

# - Timer object, and a callable instead of a string
timer = timeit.Timer(lambda: sorted(range(200, 0, -1)))
n, secs = timer.autorange()
print("autorange() picks a loop count automatically so the run lasts >= 0.2s; it chose a count >= 1:", n >= 1)
print("in notebooks/IPython the magic `%timeit expr` does all of this for you.")
print("command line: python3 -m timeit -s 'x = list(range(100))' 'sorted(x)'")
print("# - timeit is for tiny snippets. To find WHERE a whole program is slow, use a profiler")
print("#   (cProfile and friends - covered in a later tooling file).")

# 19. Practical Pattern - Deadlines with monotonic
# ------------------------------------
# - "Keep trying for at most N seconds" is a deadline, and deadlines belong on monotonic().
print("\n# 19. Deadline loop with monotonic()")


def wait_until(predicate, timeout, poll=0.01):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(poll)
    return False


ready_at = time.monotonic() + 0.05
print("condition becomes true within 0.05s, wait up to 1s ->", wait_until(lambda: time.monotonic() >= ready_at, 1.0))
print("condition never true, wait up to 0.05s            ->", wait_until(lambda: False, 0.05))

# 20. Recap
# ------------------------------------
restore_tz()  # leave the process time zone the way we found it
print("\n# 20. Recap")
print("- time() = wall clock (timestamps); monotonic()/perf_counter() = durations")
print("- sleep() waits AT LEAST the time asked; inject it so tests don't wait")
print("- TZ + tzset() changes localtime (Unix); prefer datetime/zoneinfo for zones")
print("- timeit for micro-benchmarks, min of repeat(); profile for whole programs")
