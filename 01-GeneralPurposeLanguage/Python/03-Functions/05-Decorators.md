# Decorators — Notes

## What this covers
Functions (or classes) that wrap another function to extend/modify its behavior without changing its source code — basic decorators, decorators with arguments, chaining, class-based decorators, and why `functools.wraps` matters.

## Key points
- A **decorator** takes a function and returns a new function that wraps it — possible because functions are first-class objects in Python. `@my_decorator` above a function is shorthand for `func = my_decorator(func)`.
- **Basic pattern**: `def my_decorator(func): def wrapper(*args, **kwargs): ...; return func(*args, **kwargs) ...; return wrapper`.
- **`functools.wraps(func)`** on the inner wrapper preserves the original function's `__name__`, `__doc__`, and other metadata — without it, the decorated function "looks like" `wrapper` to tools like `help()` or `inspect`.
- **Decorator factories** (decorators with arguments): a decorator that itself takes arguments needs an extra layer — `def repeat(times): def decorator(func): ...; return decorator`, used as `@repeat(times=3)`.
- **Chaining decorators** applies bottom-up: `@bold` above `@italic` above a function means `bold(italic(func))` — italic wraps first, bold wraps the result.
- **Class-based decorators**: a class with `__call__` can act as a decorator, useful when the decorator needs to keep persistent state (like a call counter) across calls.
- Built-in decorators `@staticmethod`, `@classmethod`, `@property` are decorators too, just applied to methods inside a class (see 02/03 for the OOP-specific depth).
- **`functools.singledispatch`** is itself built as a decorator — it wraps a function and lets you register type-specific overloads with `@func.register`.

## Gotchas (the part worth revising twice)
- **Without `@functools.wraps`, debugging info is lost**: the wrapper's `__name__` becomes `"wrapper"` instead of the original function's name, and `inspect.signature()` shows the wrapper's generic `(*args, **kwargs)` instead of the real signature. `functools.wraps` also copies `__wrapped__`, which `inspect.signature()` follows to recover the true signature.
- **Supporting both `@deco` and `@deco(arg=1)`** on the same decorator requires checking whether the decorator's first positional argument is the target function itself (bare usage) or `None` (parameterized usage), then branching — this is why `func=None, *, greeting="Hello"` with an `if func is not None:` check shows up.
- **Stacked decorators sharing mutable state** (like a module-level list) can observe each other's side effects — the *order* they're stacked in changes what gets appended first, since outer wraps inner.
- **`__set_name__`** on a class-based decorator fires automatically when the decorator instance is assigned as a class attribute — it's how a decorator can learn which class and attribute name it's bound to, useful for descriptor-style decorators.
- A decorator changes what name is bound at definition time — if you decorate a function and then reference the *undecorated* original by name elsewhere, you'll get surprising results (the name now always points to the wrapped version).

## When it matters
Reach for decorators for cross-cutting concerns that apply to many functions the same way: logging, timing, caching, access control, retry logic — anywhere you'd otherwise copy-paste the same "before/after" code into every function.

## One-line recap example
```python
import functools

def logger(func):
    @functools.wraps(func)          # preserves __name__/__doc__
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
```
