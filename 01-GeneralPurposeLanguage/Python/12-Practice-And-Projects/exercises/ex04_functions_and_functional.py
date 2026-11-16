"""Exercise set 04: functions and functional programming.

Replace each `raise NotImplementedError` with working code. Run the tests with:
    pytest tests/test_ex04_functions_and_functional.py
"""

import functools
from functools import partial, reduce


def greet(name, greeting="Hello", *, punctuation="!"):
    """Return a greeting string: greeting, a space, name, then punctuation.
    `punctuation` must be passed by keyword.

    greet("Asha") -> "Hello Asha!"
    greet("Asha", "Hi", punctuation=".") -> "Hi Asha."
    greet("Asha", "Hi", "?")  -> TypeError

    Level: easy
    Hint: A bare `*` in the signature makes everything after it keyword-only.
    """
    raise NotImplementedError


def build_url(base, *parts, **params):
    """Build a URL. Join `base` and `parts` with single '/', then add
    `?k=v&k2=v2` from params (in the order given). No '?' if no params.
    Strip extra '/' at the joins.

    build_url("http://x.com", "api", "users") -> "http://x.com/api/users"
    build_url("http://x.com/", "/api/", page=2, q="a") -> "http://x.com/api?page=2&q=a"
    build_url("http://x.com") -> "http://x.com"

    Level: easy
    Hint: *parts is a tuple, **params is a dict. Use str.strip('/') on each piece.
    """
    raise NotImplementedError


def append_item(item, items=None):
    """Return a list with `item` added at the end of `items`. Each call without
    `items` must start from a NEW empty list (avoid the mutable default gotcha).
    Do not change the list that was passed in; return a new list.

    append_item(1) -> [1]
    append_item(2) -> [2]          # not [1, 2]!
    a = [1]; append_item(2, a) -> [1, 2]; a is still [1]

    Level: easy
    Hint: Default to None, then create the list inside the function.
    """
    raise NotImplementedError


def make_counter(start=0, step=1):
    """Return a function `counter()`. The first call returns `start`, then each
    call returns the previous value plus `step`. Two counters are independent.

    c = make_counter(5, 2); c(), c(), c() -> 5, 7, 9

    Level: easy
    Hint: Keep the state in the enclosing function and use `nonlocal`.
    """
    raise NotImplementedError


def make_multiplier(n):
    """Return a function that multiplies its argument by `n`.
    Then use it: build a list of 3 multipliers (x1, x2, x3) correctly (see tests).

    double = make_multiplier(2); double(21) -> 42
    [make_multiplier(i)(10) for i in range(1, 4)] -> [10, 20, 30]

    Level: easy
    Hint: Return an inner function that uses `n` from the outer scope.
    """
    raise NotImplementedError


def flatten(nested):
    """Flatten arbitrarily nested lists/tuples into one flat list (recursion).
    Strings are NOT split into characters.

    flatten([1, [2, [3, 4]], 5]) -> [1, 2, 3, 4, 5]
    flatten(["ab", ["c"]]) -> ["ab", "c"]
    flatten([]) -> []

    Level: medium
    Hint: If an item is a list/tuple, extend with flatten(item); else append it.
    """
    raise NotImplementedError


def clean_names(names):
    """Use filter, map and lambda (no loops, no comprehensions): drop empty or
    whitespace-only names, strip spaces, title-case them, and return a list
    sorted by length, then alphabetically (use sorted with a lambda key).

    clean_names(["  zed ", "", "amy", "   ", "BOB"]) -> ["Amy", "Bob", "Zed"]
    clean_names(["mia", "al", "joe"]) -> ["Al", "Joe", "Mia"]

    Level: medium
    Hint: sorted(map(...filter(...)), key=lambda s: (len(s), s)). filter first, then map.
    """
    raise NotImplementedError


def merge_dicts(dicts):
    """Merge a list of dicts into one using functools.reduce. Later dicts win.
    Return a new dict; do not change the inputs. Empty list -> {}.

    merge_dicts([{"a": 1}, {"b": 2}, {"a": 3}]) -> {"a": 3, "b": 2}
    merge_dicts([]) -> {}

    Level: medium
    Hint: reduce(lambda acc, d: {**acc, **d}, dicts, {}) - the last argument is the start value.
    """
    raise NotImplementedError


def power(base, exp):
    """Helper for make_power (already done for you)."""
    return base ** exp


def make_power(exp):
    """Return a one-argument function that raises its argument to `exp`.
    Use functools.partial on the helper `power(base, exp)` given below.

    square = make_power(2); square(7) -> 49
    make_power(3)(2) -> 8
    make_power(0)(99) -> 1

    Level: medium
    Hint: partial(power, exp=exp) fixes the keyword argument and leaves `base` open.
    """
    raise NotImplementedError


def compose(*funcs):
    """Return a function that applies `funcs` left to right:
    compose(f, g, h)(x) == h(g(f(x))). With no funcs it returns its input.

    compose(str.strip, str.upper)("  hi ") -> "HI"
    compose(lambda x: x + 1, lambda x: x * 2)(3) -> 8
    compose()(5) -> 5

    Level: medium
    Hint: reduce over the functions with the value as the start.
    """
    raise NotImplementedError


def memoize(fn):
    """Decorator: cache results by arguments so `fn` runs once per distinct call.
    Support positional args and keyword args (all hashable). Keep fn's name.

    @memoize
    def slow(x): ...
    slow(2); slow(2)   # the body ran only once
    slow(x=2) is a different call key than slow(2) - that is fine.

    Level: hard
    Hint: Key = (args, tuple(sorted(kwargs.items()))). Use functools.wraps.
    """
    raise NotImplementedError


def count_calls(fn):
    """Decorator: wrap `fn` so each call is counted in the attribute
    `wrapper.calls` (starts at 0). Keep the original __name__ and __doc__.
    Counting happens even if fn raises.

    @count_calls
    def f(): ...
    f(); f(); f.calls -> 2; f.__name__ -> "f"

    Level: hard
    Hint: Use functools.wraps. Increment before calling fn.
    """
    raise NotImplementedError
