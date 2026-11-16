# Metaclasses and Class Creation — Notes

## What this covers
Classes as objects, building classes with `type(name, bases, ns)`, the exact steps of a `class` statement, custom metaclasses (`__new__`, `__init__`, `__call__`, `__prepare__`), and the lighter alternatives: `__init_subclass__`, `__class_getitem__`, `__set_name__` and class decorators. Includes registries, metaclass conflicts and when not to use any of this.

## Key points
- A class is an object; its class is its **metaclass**. The default metaclass is `type`, and `type(type)` is `type`.
- `class Foo: ...` is sugar for `type("Foo", bases, namespace)`; calling `type` directly builds classes at runtime.
- **Class creation order**: choose metaclass, `__prepare__` (namespace), run the body, `Meta.__new__` (and inside it `__set_name__` on attributes, then `__init_subclass__`), `Meta.__init__`, bind the name.
- **Metaclass `__new__`** can change the namespace/bases before the class exists; **`__init__`** only post-processes it; **`__call__`** controls instance creation (singleton, cache); **`__prepare__`** supplies the body namespace.
- **`__init_subclass__`** (parent classmethod) runs on each subclass definition, with class keyword arguments. It handles most registry/validation needs.
- **`__class_getitem__`** makes `Cls[int]` work, as in `list[int]`.
- **`__set_name__`** is how descriptors learn their name during class creation (see `09-Descriptors-And-Properties.py`).
- **Class decorators** take a finished class and return it modified: simplest option, and `dataclass` is one (`06-Dataclasses-And-Operator-Overloading.py`).
- **Registry choice**: `__init_subclass__` is simpler; a metaclass is only needed to alter the namespace or control instantiation.
- Methods defined on a metaclass are visible on the class but not on its instances (instance basics: `01-Class-Object.py`; ABCs, which use a metaclass: `05-Abstraction.py`).

## Gotchas (the part worth revising twice)
- **Metaclass conflict**: a class has one metaclass. Mixing bases with unrelated metaclasses (for example `ABC` plus your own) raises `TypeError`; fix by writing a combined metaclass, or avoid it with `__init_subclass__`.
- Metaclass hooks also run for the **base class itself**; registries need `if bases:` to skip it.
- In `__new__` the first argument is the **metaclass**; in `__init__` it is the **new class**. Pass `mcls` to `super().__new__`.
- `__init_subclass__` is never called for the class that defines it, only for its subclasses; call `super().__init_subclass__(**kwargs)` to keep cooperative inheritance working.
- `__set_name__` is **not** called for attributes assigned to the class afterwards (`Cls.x = Field()`).
- A singleton metaclass silently ignores constructor arguments on later calls.
- A class decorator is not inherited by subclasses; a registering decorator will miss them.
- If the metaclass defines `__getitem__`, it wins over `__class_getitem__`.
- Metaclasses are inherited: subclasses use the parent's metaclass automatically.

## When it matters
Only when building frameworks (ORMs, plugin systems, enums, ABCs) where classes must be inspected or rewritten as they are defined. For application code try, in order: a function, a class decorator, `__init_subclass__`, a descriptor, and only then a metaclass.

## One-line recap example
```python
class Plugin:
    registry = {}
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        Plugin.registry[cls.__name__] = cls

class Csv(Plugin): ...     # Plugin.registry -> {'Csv': <class Csv>}
```
