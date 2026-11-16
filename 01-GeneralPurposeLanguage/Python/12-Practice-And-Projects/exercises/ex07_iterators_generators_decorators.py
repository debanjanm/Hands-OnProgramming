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

    def __init__(self, start):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError


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
    raise NotImplementedError

