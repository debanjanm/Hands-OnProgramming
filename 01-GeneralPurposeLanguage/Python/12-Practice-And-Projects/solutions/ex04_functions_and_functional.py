"""Exercise set 04: functions and functional programming.

Replace each `raise NotImplementedError` with working code. Run the tests with:
    pytest tests/test_ex04_functions_and_functional.py
"""

import functools
from functools import partial, reduce


def greet(name, greeting="Hello", *, punctuation="!"):
    # keyword-only argument after a bare *
    return f"{greeting} {name}{punctuation}"


def build_url(base, *parts, **params):
    # *args collects positionals, **kwargs collects keywords
    pieces = [base.rstrip("/")] + [p.strip("/") for p in parts]
    url = "/".join(pieces)
    if params:
        url += "?" + "&".join(f"{k}={v}" for k, v in params.items())
    return url


def append_item(item, items=None):
    # None default avoids sharing one list between calls
    return [*(items or []), item]


def make_counter(start=0, step=1):
    # closure + nonlocal remembers state between calls
    value = start - step
    def counter():
        nonlocal value
        value += step
        return value
    return counter


def make_multiplier(n):
    # inner function closes over n
    def multiply(x):
        return x * n
    return multiply


def flatten(nested):
    # recursive case for sequences, base case for plain values
    out = []
    for item in nested:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out


def clean_names(names):
    # filter -> map -> sorted with a tuple key
    return sorted(map(lambda n: n.strip().title(), filter(lambda n: n.strip(), names)),
                  key=lambda s: (len(s), s))


def merge_dicts(dicts):
    # reduce folds the list into one value; {} start handles empty input
    return reduce(lambda acc, d: {**acc, **d}, dicts, {})


def power(base, exp):
    """Helper for make_power (already done for you)."""
    return base ** exp


def make_power(exp):
    # partial pre-fills arguments of an existing function
    return partial(power, exp=exp)


def compose(*funcs):
    # reduce threads the value through each function
    return lambda x: reduce(lambda acc, f: f(acc), funcs, x)


def memoize(fn):
    # dict cache keyed on the arguments
    cache = {}
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in cache:
            cache[key] = fn(*args, **kwargs)
        return cache[key]
    return wrapper


def count_calls(fn):
    # functions are objects: store the counter on the wrapper
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return fn(*args, **kwargs)
    wrapper.calls = 0
    return wrapper
