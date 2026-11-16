"""Exercise set 07: iterators, generators and decorators.

Work from top to bottom. Each problem is marked easy, medium or hard.
"""
import contextlib
import functools


# ---------------------------------------------------------------- 1 (easy)
class Countdown:
    """Level: easy.

    An iterator that counts down from `start` to 1, then stops.
    It must be a real iterator: `iter(x) is x` and `next(x)` works.

        list(Countdown(3)) -> [3, 2, 1]
        list(Countdown(0)) -> []

    Hint: implement __iter__ (return self) and __next__ (raise StopIteration at the end).
    """

    # Idea: keep the current number as state; __next__ moves it forward.
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


# ---------------------------------------------------------------- 2 (easy)
def chunked(iterable, size):
    """Level: easy.

    Yield lists of `size` items. The last list may be shorter.
    Must work on any iterable (even a generator) and be lazy.
    Raise ValueError if size < 1.

        list(chunked([1, 2, 3, 4, 5], 2)) -> [[1, 2], [3, 4], [5]]
        list(chunked([], 3)) -> []

    Hint: collect items in a list; yield it when it is full; yield the rest at the end.
    """
    # Idea: fill a buffer, flush when full, flush the leftover at the end.
    if size < 1:
        raise ValueError("size must be at least 1")
    buffer = []
    for item in iterable:
        buffer.append(item)
        if len(buffer) == size:
            yield buffer
            buffer = []
    if buffer:
        yield buffer


# ---------------------------------------------------------------- 3 (easy)
def flatten(nested):
    """Level: easy.

    Flatten lists/tuples nested to any depth into one stream of items.
    Strings are NOT split into characters.

        list(flatten([1, [2, [3, 4]], 5])) -> [1, 2, 3, 4, 5]
        list(flatten(["ab", ["cd"]])) -> ["ab", "cd"]
        list(flatten([])) -> []

    Hint: `yield from flatten(item)` for a list or tuple, otherwise `yield item`.
    """
    # Idea: recursion with `yield from` hands the inner stream straight out.
    for item in nested:
        if isinstance(item, (list, tuple)):
            yield from flatten(item)
        else:
            yield item


# ------------------------------------------------------------- 4 (medium)
def parse_log_lines(lines):
    """Level: medium.

    A small generator pipeline for log text. For each raw line:
    strip it, skip blank lines and lines starting with '#', and split
    "LEVEL: message" at the FIRST colon. Yield (level_upper, message_stripped).
    Lines without a colon are skipped. Must be lazy (do not build a list).

        list(parse_log_lines(["info: started", "", "# note", "Error: disk: full"]))
            -> [("INFO", "started"), ("ERROR", "disk: full")]

    Hint: `line.partition(":")` returns (before, sep, after); sep is "" if no colon.
    """
    # Idea: one loop, several early `continue`s, one yield.
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        level, sep, message = line.partition(":")
        if not sep:
            continue
        yield level.strip().upper(), message.strip()


# ------------------------------------------------------------- 5 (medium)
def sliding_window(iterable, size):
    """Level: medium.

    Yield tuples of `size` consecutive items. If there are fewer than `size`
    items, yield nothing. Must work on one-shot iterators. ValueError if size < 1.

        list(sliding_window([1, 2, 3, 4], 2)) -> [(1, 2), (2, 3), (3, 4)]
        list(sliding_window("abc", 3)) -> [("a", "b", "c")]
        list(sliding_window([1, 2], 3)) -> []

    Hint: collections.deque(maxlen=size) drops the oldest item for you.
    """
    # Idea: a bounded deque is the window; yield a tuple copy once it is full.
    from collections import deque

    if size < 1:
        raise ValueError("size must be at least 1")
    window = deque(maxlen=size)
    for item in iterable:
        window.append(item)
        if len(window) == size:
            yield tuple(window)


# ------------------------------------------------------------- 6 (medium)
def averager():
    """Level: medium.

    A generator used as a coroutine. After you call next() once to start it,
    every `send(x)` gives back the running average of all numbers sent so far.

        avg = averager(); next(avg)
        avg.send(10) -> 10.0
        avg.send(20) -> 15.0
        avg.send(30) -> 20.0

    Hint: `received = yield average` both returns a value and receives one.
    """
    # Idea: keep total and count in local variables; the generator remembers them.
    total = 0
    count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


# ------------------------------------------------------------- 7 (medium)
def log_calls(func):
    """Level: medium.

    Decorator. Every call to the wrapped function appends (name, args, kwargs)
    to a list `wrapper.calls`. The result is returned unchanged.
    The wrapper must keep the original __name__ and __doc__.

        @log_calls
        def add(a, b=0): "Add."; return a + b
        add(1, b=2) -> 3
        add.calls -> [("add", (1,), {"b": 2})]
        add.__name__ -> "add"

    Hint: use functools.wraps(func) on the inner function.
    """
    # Idea: wrapper stores its own call list as an attribute.
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls.append((func.__name__, args, kwargs))
        return func(*args, **kwargs)

    wrapper.calls = []
    return wrapper


# ------------------------------------------------------------- 8 (medium)
def repeat(times):
    """Level: medium.

    Decorator WITH an argument. The decorated function runs `times` times per
    call. Return the list of all results. Keep __name__ and __doc__.
    Raise ValueError (when decorating) if times < 1.

        @repeat(3)
        def roll(): return 4
        roll() -> [4, 4, 4]

    Hint: three layers: repeat(times) -> decorator(func) -> wrapper(*args, **kwargs).
    """
    # Idea: the outer function only captures `times`; the middle one is the real decorator.
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return [func(*args, **kwargs) for _ in range(times)]

        return wrapper

    return decorator


# ------------------------------------------------------------- 9 (medium)
def timed(clock):
    """Level: medium.

    Decorator factory for timing. `clock` is a zero-argument function that
    returns the current time (tests pass a fake one). After each call,
    append `end - start` to `wrapper.durations`. Record the time even if the
    function raises (the error still propagates).

        ticks = iter([0, 5, 10, 12])
        @timed(lambda: next(ticks))
        def work(): return "ok"
        work(); work()
        work.durations -> [5, 2]

    Hint: call clock() before and after; use try/finally.
    """
    # Idea: try/finally guarantees the measurement is saved on success and failure.
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                wrapper.durations.append(clock() - start)

        wrapper.durations = []
        return wrapper

    return decorator


# ------------------------------------------------------------ 10 (medium)
def retry(times, exceptions=(Exception,), delay=1, sleep=None):
    """Level: medium.

    Decorator. Call the function up to `times` times in total. If it raises one
    of `exceptions`, wait `delay` seconds (call `sleep(delay)`) and try again.
    If the last attempt also fails, let that exception go out. Do not sleep
    after the last failure. Other exception types are not retried.
    `sleep` is passed in so tests can fake it (default: time.sleep).

        calls = []
        @retry(3, (ValueError,), delay=2, sleep=calls.append)
        def flaky(): ...   # fails twice, then works
        flaky() -> result; calls -> [2, 2]

    Hint: loop over range(times); on the final attempt re-raise.
    """
    # Idea: the loop counts attempts; sleeping only happens between attempts.
    import time

    sleeper = sleep or time.sleep

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == times:
                        raise
                    sleeper(delay)

        return wrapper

    return decorator


# ------------------------------------------------------------ 11 (hard)
def memoize(func):
    """Level: hard.

    Cache results by arguments (positional and keyword). Provide
    `wrapper.hits`, `wrapper.misses` counters and `wrapper.clear()` which
    empties the cache and resets the counters. Calls with the same arguments
    (in any keyword order) must hit the cache. Keep __name__.
    Exceptions are not cached.

        @memoize
        def square(x): return x * x
        square(4); square(4)
        (square.hits, square.misses) -> (1, 1)

    Hint: the key can be (args, tuple(sorted(kwargs.items()))).
    """
    # Idea: a dict keyed by the arguments; counters live on the wrapper.
    cache = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            wrapper.hits += 1
            return cache[key]
        result = func(*args, **kwargs)  # if this raises, nothing is stored
        cache[key] = result
        wrapper.misses += 1
        return result

    def clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.clear = clear
    return wrapper


# ------------------------------------------------------------ 12 (hard)
@contextlib.contextmanager
def collect_errors(errors, *exc_types):
    """Level: hard.

    A context manager (write it with @contextlib.contextmanager). If the body
    raises one of `exc_types`, append the exception object to the list `errors`
    and swallow it. Any other exception propagates. With no `exc_types`, treat
    it as Exception.

        errors = []
        with collect_errors(errors, ValueError):
            int("x")
        errors -> [ValueError(...)]   # and no crash

    Hint: wrap a bare `yield` in try/except.
    """
    # Idea: code before `yield` is __enter__, the except block is __exit__.
    caught = exc_types or (Exception,)
    try:
        yield errors
    except caught as error:
        errors.append(error)
