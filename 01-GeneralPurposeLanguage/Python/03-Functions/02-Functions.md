# Functions — Notes

## What this covers
Everything about Python functions: defining and calling them, the many ways to pass arguments, lambdas, closures, recursion, decorators-lite (partial/annotations), and some deeper gotchas like mutable defaults and scoping rules.

## Key points
- **Basic syntax**: `def name(params):` — parameters are placeholders, arguments are the actual values passed in.
- **Return values**: `return` sends a value back; no `return` means the function implicitly returns `None`.
- **Default arguments**: `def power(base, exponent=2):` — the default is used if the caller skips that argument.
- **Keyword arguments**: pass by name (`describe_pet(pet_name="Lucy", animal_type="dog")`) — order stops mattering.
- **`*args`**: collects extra positional arguments into a tuple. **`**kwargs`**: collects extra keyword arguments into a dict.
- **Lambdas**: `lambda x: x * x` — one-expression anonymous functions, handy for short throwaway logic.
- **Higher-order functions**: functions that take/return other functions (`map`, `filter`, `sorted`, or your own like `operate_on_list`).
- **Closures**: an inner function that remembers variables from its enclosing function even after that function has returned.
- **Recursion**: a function calling itself, with a base case to stop it.
- **`functools.partial`**: locks in some arguments of a function, producing a new, simpler-to-call function.
- **Functions are first-class objects**: assignable to variables, storable in lists/dicts, passable as arguments, returnable from other functions.
- **Type hints** (`def f(name: str) -> str:`) are documentation/static-analysis only — Python does not enforce them at runtime.
- **`*` and `/` in signatures**: `*` marks everything after it keyword-only; `/` marks everything before it positional-only.
- **Introspection**: `func.__defaults__`, `func.__name__`, and `inspect.signature(func)` let you inspect a function's shape at runtime.

## Gotchas (the part worth revising twice)
- **Mutable default argument trap**: `def add_item(item, items=[]):` — the default list is created ONCE at definition time and shared across every call that doesn't pass its own list. Fix: use `items=None` and create a fresh list inside the function if `items is None`.
- **`global` vs `nonlocal`**: `global` rebinds a name in module scope; `nonlocal` rebinds a name in the nearest *enclosing function* scope (used in nested functions). Without either, assignment inside a function just creates a new local variable — it does not touch the outer one.
- **Recursion depth limit**: CPython has no tail-call optimization; each recursive call adds a stack frame, capped by `sys.getrecursionlimit()` (default 1000). Going past it raises `RecursionError`.
- **Memoization**: manual caching uses a dict keyed by arguments; `@functools.cache` (or `@functools.lru_cache`) does it automatically — same idea, no boilerplate.
- **Keyword-only/positional-only enforcement**: calling a keyword-only parameter positionally (or a positional-only parameter by name) raises `TypeError` — this is a deliberate API-design lock, not a bug.
- `input()` always returns a **string** — you must convert it yourself (`int(input(...))`) if you need a number.

## When it matters
Every non-trivial Python program is built from functions — this file is the foundation for decorators, closures-based patterns, and clean function signatures used throughout the rest of the codebase.

## One-line recap example
```python
def add_item(item, items=None):   # never use a mutable default directly
    if items is None:
        items = []
    items.append(item)
    return items
```
