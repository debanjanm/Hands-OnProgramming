# Structural Design Patterns — Notes

## What this covers
Patterns for assembling classes and objects into larger structures: Adapter, Bridge, Composite, Decorator (the pattern vs Python's `@decorator`), Facade, Flyweight (with `__slots__` and `weakref`), and Proxy (virtual, protection, caching, and `__getattr__` forwarding), plus the Python-idiomatic alternative for each.

## Key points
- **Adapter**: wraps a class with the *wrong* interface so your code can use it. In Python often just a function, lambda, or small subclass.
- **Bridge**: two things vary independently (shape x color), so keep two hierarchies and let one *hold* the other. N + M classes instead of N x M.
- **Composite**: leaf and group share one interface, so a single file and a whole folder tree are treated the same. Groups forward calls to their children.
- **Decorator pattern**: wrap an object in another with the *same interface* to add behavior at runtime; wrappers stack in any order (Espresso -> Milk -> Sugar).
- **Python `@decorator`**: a language feature that wraps functions/classes at definition time. Related idea, not the same thing. Use `functools.wraps`.
- **Facade**: one simple entry point over a messy subsystem; often just a module or function in Python. The subsystem stays usable directly.
- **Flyweight**: share the *intrinsic* (unchanging) state across many objects via a factory cache; pass *extrinsic* (per-use) state in. `__slots__` shrinks each object; a `WeakValueDictionary` cache cleans itself.
- **Proxy**: same interface, but it *controls access*: **virtual** (lazy load), **protection** (permission check), **caching** (remember results).
- **`__getattr__` proxies** forward unknown attribute lookups to a target, so you don't hand-write every method.
- **Python alternatives**: duck typing (Adapter), passing a callable (Bridge), recursion over nested data (Composite), `@decorator`/`contextlib` (Decorator), a module of functions (Facade), `lru_cache`/interning/`__slots__` (Flyweight), `cached_property`/`__getattr__` (Proxy).

## Gotchas (the part worth revising twice)
- All the wrapper patterns look alike in code; **intent** differs. Adapter changes the interface, Decorator adds behavior, Proxy controls access, Facade simplifies many objects.
- Without `functools.wraps`, a decorated function loses its `__name__` and docstring.
- Composite: operations like `add()` make no sense on a leaf — decide where they live.
- `__slots__` blocks new attributes (typos raise `AttributeError`) and removes `__weakref__` unless you list it in the slots, which matters for weak caches.
- `__getattr__` only runs when normal lookup **fails**, and dunder methods (`len(proxy)`, `str(proxy)`) are looked up on the *type*, so they are **not** forwarded — define them explicitly.
- A plain dict flyweight cache keeps objects alive forever; use `weakref.WeakValueDictionary` if they should expire.
- A caching proxy serves stale data if the real answer changes; only cache pure results.
- Don't stack adapters on adapters or build deep decorator towers — debugging which layer did what gets painful. A facade that does everything becomes a god class.

## When it matters
Use them when integrating code you can't change (Adapter, Facade), when features combine in many ways (Bridge, Decorator), when data is a tree (Composite), when millions of similar objects strain memory (Flyweight), or when access to an object needs gating, delaying or caching (Proxy). In Python, check first whether a function, a module, or a stdlib helper already does the job.

## One-line recap example
```python
class LazyImage:
    def __init__(self, path): self.path, self._real = path, None
    def show(self):
        self._real = self._real or f"loaded {self.path}"   # virtual proxy: load on first use
        return self._real
```
