# Attribute Access Hooks — Notes

## What this covers
How to intercept reading, writing, deleting and listing attributes: `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`, plus the built-ins `getattr`/`setattr`/`hasattr`/`delattr`, `vars()`/`__dict__`, proxies, read-only objects, and a recap of the full lookup order.

## Key points
- `obj.x` calls `__getattribute__` for **every** read; `__getattr__` is only a **fallback** when that raised `AttributeError`.
- `__setattr__` catches every assignment (including inside `__init__`); `__delattr__` catches `del`; `__dir__` controls what `dir()` lists.
- Always finish with `super().__setattr__(...)` / `super().__getattribute__(...)` so the real storage still happens.
- **Delegation/proxy**: store a target object and forward unknown names from `__getattr__`. Good for logging, lazy loading, wrappers (design context: `08-SOLID-Principles.py`).
- **Frozen/read-only objects**: raise in `__setattr__` and `__delattr__`; set initial values through `object.__setattr__`. Compare `dataclass(frozen=True)` in `06-Dataclasses-And-Operator-Overloading.py`.
- **Typo guard**: an allow-list in `__setattr__` or `__slots__` stops `obj.colour = ...` silently creating a new attribute (slots: `02-Encapsulation.py`).
- `getattr(obj, name, default)`, `setattr`, `hasattr`, `delattr` are for names held in strings.
- `vars(obj)` is `obj.__dict__`; methods and class attributes live in `Class.__dict__` (a read-only `mappingproxy`).
- **Lookup recap**: data descriptor, then instance `__dict__`, then non-data descriptor / class attribute, then `AttributeError`, then `__getattr__` (descriptors: `09-Descriptors-And-Properties.py`).

## Gotchas (the part worth revising twice)
- **Infinite recursion**: using `self.anything` inside `__getattribute__`, or `self.x = v` inside `__setattr__`, re-enters the hook. Go through `object.__getattribute__` / `super()`.
- **`__getattr__` + `copy`/`pickle`**: these create an empty object without `__init__`, so `self._data` is missing and your `__getattr__` recurses. Raise `AttributeError` immediately for names starting with `_`.
- **`__getattr__` must raise `AttributeError`** for unknown names, never return `None`, or `hasattr` and friends lie.
- **Implicit special methods skip the hooks**: `len(proxy)`, `proxy[0]`, `proxy + 1` look on the type, so `__getattr__` does not see them. Define dunders explicitly.
- **`hasattr` runs code** (properties, `__getattr__`) and treats any `AttributeError` raised inside a property as "missing".
- An `AttributeError` raised inside a property getter falls through to `__getattr__`, giving confusing messages.
- Writing `obj.__dict__[name] = v` bypasses `__setattr__` and data descriptors.
- **Frozen is not truly frozen**: `object.__setattr__(obj, "x", v)` still works.
- `__dir__` only changes the listing; it does not create the attribute.
- Class-level reads (`Cls.attr`) use `type.__getattribute__`, so instance `__getattr__` is ignored; use a metaclass (`11-Metaclasses-And-Class-Creation.py`).
- Keys like `items` in an `AttrDict` are shadowed by real methods.

## When it matters
Use `__getattr__` for proxies, lazy attributes and dynamic APIs; `__setattr__` for validation, change tracking and frozen objects. Prefer `@property` or descriptors for a known, fixed set of attributes: hooks are broader, slower and easier to get wrong.

## One-line recap example
```python
class Proxy:
    def __init__(self, target): self._t = target
    def __getattr__(self, name):          # only called when normal lookup fails
        if name.startswith("_"): raise AttributeError(name)
        return getattr(self._t, name)

# Proxy([3, 1]).count(1) -> 1
```
