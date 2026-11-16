# Descriptors and Properties — Notes

## What this covers
The descriptor protocol (`__get__`, `__set__`, `__delete__`, `__set_name__`), data vs non-data descriptors, the attribute lookup order, and how `property`, `classmethod`, `staticmethod` and plain methods are all descriptors. Also reusable validated fields, lazy/cached attributes, and storage choices (including `WeakKeyDictionary`).

## Key points
- A **descriptor** is an object stored as a *class* attribute that defines `__get__`, `__set__` and/or `__delete__`. Python calls them when the attribute is read, assigned or deleted on an instance.
- **Data descriptor** = has `__set__` or `__delete__`. **Non-data descriptor** = only `__get__`.
- **Lookup order** for `obj.name`: data descriptor on the class, then `obj.__dict__`, then non-data descriptor / plain class attribute, then `__getattr__` (see `10-Attribute-Access-Hooks.py`).
- **Functions are non-data descriptors**: `obj.method` calls `function.__get__(obj, type(obj))` and returns a bound method. That is the whole secret of `self` (basics in `01-Class-Object.py`).
- **`classmethod`** binds the class, **`staticmethod`** binds nothing, **`property`** is a data descriptor (it always defines `__set__`, raising if there is no setter).
- **`__set_name__(self, owner, name)`** runs once at class creation so a descriptor learns the attribute name it was assigned to.
- A **validated-field descriptor** writes a rule once and reuses it for many attributes; store the value in the instance `__dict__` under a private key.
- A non-data descriptor that writes its result into `obj.__dict__` under its own name is a **lazy/cached** attribute (`functools.cached_property` works like this).
- `property` basics are in `02-Encapsulation.py`; here we look underneath it and build our own.

## Gotchas (the part worth revising twice)
- **Descriptor state is shared**: there is one descriptor object per class. `self.value = v` inside `__set__` makes every instance share one value. Store per-instance data on the instance (or in a keyed structure).
- **`WeakKeyDictionary` storage** needs instances that are hashable AND weak-referenceable. `__slots__` without `__weakref__`, or a class that defines `__eq__` without `__hash__`, raises `TypeError`. A plain `dict` keyed by instance leaks memory.
- **Descriptors only work on the class.** Putting one in an instance's `__dict__` (`obj.x = Desc()`) is just storing a value; `__get__` never fires.
- **Class-level assignment replaces the descriptor**: `Cls.attr = 5` does not call `__set__`, it deletes the descriptor.
- **Non-data descriptors can be shadowed**: `obj.attr = x` writes to the instance dict and wins. If you need true read-only, define `__set__` that raises.
- `__get__` is also called on the class (`obj is None`); return `self` there or you will break `help()` and introspection.
- **`cached_property`** needs an instance `__dict__` (fails with `__slots__`), never refreshes on its own, and `del obj.attr` clears the cache.
- `__set_name__` is not called for descriptors attached after the class exists; call it yourself.

## When it matters
Use a descriptor when the same attribute rule (type check, range check, logging, lazy load) repeats across many attributes or classes, or when you need to understand why methods, properties and `__slots__` behave as they do. ORMs and validation libraries are built on this.

## One-line recap example
```python
class Positive:
    def __set_name__(self, owner, name): self.n = "_" + name
    def __get__(self, obj, cls=None): return self if obj is None else getattr(obj, self.n)
    def __set__(self, obj, v):
        if v <= 0: raise ValueError("must be positive")
        setattr(obj, self.n, v)

class Item:
    price = Positive()   # Item().price = -1 -> ValueError
```
