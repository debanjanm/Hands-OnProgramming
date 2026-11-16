# Creational Design Patterns — Notes

## What this covers
Patterns for controlling how objects get created: Singleton (four Pythonic ways plus thread-safety), Factory Method, Simple Factory (dict and classmethods), Abstract Factory, Builder (with fluent chaining), Prototype (via `copy`), Object Pool, and Borg/Monostate — plus the Python note that functions, dicts and modules often replace the pattern entirely.

## Key points
- **Singleton** = one instance and one access point. Four ways in Python: a **module-level object** (modules are imported once, simplest), a **metaclass** whose `__call__` caches instances, overriding **`__new__`** to return a saved instance, or a **class decorator** that returns a cached instance.
- **Thread-safe Singleton** uses double-checked locking: check, take a `threading.Lock`, check again, then create.
- **Factory Method**: the base class calls an overridable `create_...()` method; subclasses decide which concrete class to build.
- **Simple Factory**: a dict of `name -> class` replaces `if/elif` chains. **Classmethod factories** (`from_string`, `from_dict`) give a class several named constructors; use `cls(...)` so subclasses work.
- **Abstract Factory**: one factory per *family* of related products so they always match (dark button + dark checkbox).
- **Builder**: collect optional parts step by step, then `build()`. **Fluent** builders return `self` from each step so calls chain.
- **Prototype**: clone an existing object with `copy.copy` (shallow) or `copy.deepcopy` (full); a registry of prototypes lets clients ask for clones by name; define `__copy__` for custom rules.
- **Object Pool**: pre-create expensive objects, lend them out, take them back. A context manager guarantees they come back.
- **Borg/Monostate**: many instances sharing one `__dict__` — shared state without shared identity.
- **Pythonic note**: classes and functions are first-class, modules are singletons, `functools.partial` presets arguments, dataclasses with defaults replace many Builders.

## Gotchas (the part worth revising twice)
- A `__new__` Singleton still runs `__init__` on **every** call, so a careless `__init__` resets state each time.
- The decorator Singleton turns the class name into a **function**, so `isinstance(x, Database)` and subclassing break.
- Without a lock, two threads can both see "no instance yet" and both create one. Check again *inside* the lock.
- Shallow copies **share** inner mutable objects (`shallow.loot is template.loot`). Use `deepcopy` when children must be independent.
- Don't copy objects holding files, sockets or locks — build them fresh.
- Pool items must always be returned (`try/finally` or a context manager), otherwise the pool slowly runs dry. Pooled objects may also carry stale state from the last user.
- Borg is still hidden global state: same testing pain as Singleton, and subclasses share state too unless given their own dict.
- Singleton `a is b` is `True`; Borg `a is b` is `False` but their attributes match.
- A dict cache in a factory keeps objects alive forever; `weakref.WeakValueDictionary` lets unused ones disappear.

## When it matters
Use these when construction itself is the pain: many types chosen at runtime (factory), many optional parts (builder), costly setup (prototype/pool), or a rule that only one shared thing may exist (singleton). If a plain function, dict, module or dataclass solves it, prefer that — don't add a pattern just to look structured.

## One-line recap example
```python
class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *a, **k):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*a, **k)
        return cls._instances[cls]

class Config(metaclass=SingletonMeta): ...

# Config() is Config() -> True
```
