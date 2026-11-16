# Object Lifecycle, Copy and Serialization — Notes

## What this covers
How a Python object is born (`__new__`, `__init__`), lives (reference counting, the garbage collector, weak references), dies (`__del__`, `weakref.finalize`, context managers), and gets duplicated or saved (`copy`, `deepcopy`, `pickle`). Also the `__repr__`/`__str__`/`__format__` recap, the hash/equality contract, and how `__slots__` behaves with copy and pickle.

## Key points
- **Creation is two steps**: `__new__(cls, ...)` makes and returns the object, `__init__(self, ...)` fills it in. Use `__new__` only for singletons, caches (flyweights) and immutable subclasses (`class Celsius(float)`), where the value must be fixed at creation.
- **Reference counting** frees an object the moment its last reference goes (CPython). `sys.getrefcount(x)` reads one higher than expected because the call argument is a temporary reference.
- **Cycles** (A points to B, B points to A) never reach zero; the **cyclic GC** (`gc.collect()`) frees them. Since Python 3.4 objects with `__del__` in a cycle are collected too.
- **`weakref.ref`** refers to an object without keeping it alive (returns `None` once dead). `WeakValueDictionary` and `WeakSet` drop entries automatically, ideal for caches and observers.
- **`weakref.finalize(obj, func, *args)`** is the safe cleanup callback: runs once, never touches `obj`, can be cancelled with `.detach()`.
- **Copying**: `b = a` is only a new name. `copy.copy` is shallow (new outer object, shared inner objects). `copy.deepcopy` copies everything and keeps shared references and cycles intact via its `memo` dict.
- **`__copy__` / `__deepcopy__(memo)`** let you skip things that should not be copied (locks, caches, connections) or share on purpose.
- **`__repr__`** is for developers (unambiguous), **`__str__`** for users, **`__format__(spec)`** powers `f"{obj:spec}"`. `str()` falls back to `__repr__`, never the reverse.
- **Pickle** turns objects into bytes and back. It stores the class by name and restores `__dict__` directly.
- **`__getstate__` / `__setstate__`** choose what is pickled (drop locks, files) and rebuild it on load; `copy` uses the same hooks. **`__reduce__`** returns `(callable, args)` and rebuilds through a constructor, so `__init__` does run.
- **Hash contract**: `a == b` implies `hash(a) == hash(b)`. Define `__eq__` alone and the class becomes unhashable.
- **`__slots__`** classes pickle and copy fine on protocol 2+; add `'__weakref__'` to the slots if you need weak references.
- **Context managers** (`with`, `__enter__`/`__exit__`, `contextlib.contextmanager`, `ExitStack`) give guaranteed cleanup at a known moment.

## Gotchas (the part worth revising twice)
- `__init__` runs on **every** `Config()` call even when `__new__` returns the existing singleton, so it re-initialises shared state.
- If `__new__` returns something that is not an instance of `cls`, `__init__` is skipped.
- `del obj` does **not** call `__del__`; it only removes one name. `__del__` runs when the last reference disappears.
- `__del__` problems: timing is not guaranteed, exceptions inside it are printed and **ignored**, it also runs on half-built objects when `__init__` raised (attributes may be missing), and at interpreter exit globals may already be `None`. Never use it for must-happen cleanup.
- Plain `list`, `dict`, `int`, `str` cannot be weak-referenced; slotted classes need `'__weakref__'`.
- Shallow copy shares inner mutables, including a list inside a tuple. `[[0]*3]*3` is three references to one row.
- `list.copy()`, `dict.copy()` and `a[:]` are shallow too.
- Neither `copy` nor `pickle.loads` calls `__init__`. Anything `__init__` sets up must be restored in `__setstate__` or `__copy__`.
- Pickle cannot handle lambdas, local functions/classes, locks, open files or generators, and the class must be importable at load time.
- **Never unpickle untrusted data**: `__reduce__` can make loading run arbitrary code.
- Hash on fields that never change. Mutate a key while it sits in a set or dict and lookups silently fail, yet the object is still inside.
- A copy or unpickled object is `==` the original only if your `__eq__` says so, and is never `is` the original.
- Return a non-empty dict from `__getstate__` on Python before 3.11; a falsy state skipped `__setstate__`.

## When it matters
Caches and registries that must not leak memory (weak refs), classes that own files, sockets or locks (context managers, `finalize`, `__getstate__`), objects sent to other processes or saved to disk (pickle, which `multiprocessing` uses), undo/snapshot features (deepcopy), and anything stored in sets or used as dict keys (hash contract). Related files: `01-Class-Object.py`, `06-Dataclasses-And-Operator-Overloading.py`, `02-Encapsulation.py` (slots).

## One-line recap example
```python
import copy, pickle

class Box:
    def __init__(self, items): self.items = items

b = Box([1, 2])
shallow, deep, loaded = copy.copy(b), copy.deepcopy(b), pickle.loads(pickle.dumps(b))
# shallow.items is b.items -> True | deep.items is b.items -> False | loaded.items == [1, 2] (no __init__ call)
```
