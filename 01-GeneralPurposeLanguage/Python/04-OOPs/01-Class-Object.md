# Class & Object — Notes

## What this covers
The basics of OOP in Python: what classes and objects are, how to create them, magic methods, `self`, class vs instance variables, reference semantics, and some deeper internals like `__slots__`, `__new__` vs `__init__`, and metaclasses.

## Key points
- **Class** = blueprint/template (logical entity). **Object** = an instance of a class (physical entity in memory). One class, many possible objects.
- Create a class with `class ClassName:`; create an object by calling the class like a function: `my_dog = Dog("Buddy", "Golden Retriever")`.
- **`__init__`** is the constructor — runs automatically when an object is created, used to set up instance attributes.
- **`self`** is the first parameter of instance methods — it refers to the specific object the method was called on; Python passes it automatically.
- **Class variables** are shared by all instances (defined in the class body, outside any method). **Instance variables** are unique per object (usually set in `__init__` via `self.x = ...`).
- **Magic methods** (dunder methods) implement special behavior: `__init__` (construct), `__str__` (friendly display for `print()`/`str()`), `__repr__` (unambiguous, debugging-oriented display).
- **Reference variables**: variables holding objects store a reference, not the value itself. Assigning `data2 = data1` makes both point to the same object — mutating through one is visible through the other ("pass-by-object-reference").
- Modify an attribute with plain dot assignment; delete one with `del obj.attribute`; delete the whole object with `del obj`.
- **`__slots__`** declares a fixed set of attribute names, skipping the per-instance `__dict__` — less memory, faster attribute access, but no arbitrary new attributes afterward.
- **`__new__`** creates and returns the instance (runs first); **`__init__`** initializes it (runs second, returns `None`). Overriding `__new__` is rare — mostly for singletons.
- A **metaclass** (default: `type`) controls how classes themselves are created — advanced, rarely needed.

## Gotchas (the part worth revising twice)
- **Class variable as mutable default is a shared trap**: `items = []` as a class attribute is ONE list shared by every instance — mutating it via one instance affects all of them. Fix: initialize mutable state inside `__init__` so each instance gets its own.
- `__repr__` vs `__str__`: `__str__` is for end users (friendly), `__repr__` is for developers (ideally `eval`-able, recreates the object). If `__str__` is missing, `print()`/`str()` fall back to `__repr__`. Every class should define `__repr__`.
- `__slots__` trades away flexibility: instances can't get new attributes on the fly, and any attribute a `@property` backs (e.g. `_radius`) must also be listed in `__slots__`, since there's no `__dict__` fallback.
- `__new__` reusing an existing instance (e.g. Singleton pattern) does NOT skip `__init__` — Python still calls `__init__` on whatever `__new__` returns, so a second "construction" call can silently overwrite state.
- Accessing a class variable through an instance (`emp1.company_name`) works, but it's still the same shared class-level value — assigning to it via the instance creates a new *instance* variable instead (shadowing, doesn't mutate the class variable).

## When it matters
This is the foundation for every other OOP topic (encapsulation, inheritance, polymorphism) — you reach for classes whenever you need to bundle related data and behavior together.

## One-line recap example
```python
class Dog:
    def __init__(self, name):
        self.name = name          # instance variable, unique per object
    def __repr__(self):
        return f"Dog({self.name!r})"
```
