# Composition vs Inheritance — Notes

## What this covers
How to choose between "is-a" (inheritance) and "has-a" (composition): delegation (including `__getattr__` forwarding), mixins done right, strategy by composition, `Protocol` for dependencies, refactoring an inheritance tree, the fragile base class problem, the diamond, and when inheritance really is the right tool.

## Key points
- **Inheritance = is-a**, **composition = has-a**. Test: can you say "X is a Y" always, with no exceptions? A `Stack` is not a `list` (you cannot insert in the middle of a stack).
- **Favor composition**: inheritance is the tightest coupling (the child depends on the parent's internals); composition hides the part behind a small interface so it can be swapped, mocked and tested alone.
- **Delegation**: the outer object forwards calls to the inner one. Explicit forwarding methods are clear; `__getattr__` forwards everything that is not found normally.
- **Strategy by composition**: put the part that varies (discount, tax, movement, weapon) behind a tiny interface and pass it in. 2 axes x 3 options becomes 5 small pieces instead of 6 subclasses. A function can be a strategy.
- **Runtime swapping**: a composed part is just an attribute, so `obj.mover = Swim()` changes behavior live; base classes cannot be changed like that.
- **`typing.Protocol`** describes the shape a dependency needs (`send(msg)`), with no inheritance; with **dependency injection** (pass parts in the constructor, default if none) tests inject a fake easily.
- **Mixins** add one focused capability to unrelated classes: narrow name, no or little state, documented contract, placed on the left of the base list, cooperative `super()`.
- **Refactor a tree**: name the axes of variation, give each a small interface, replace subclasses with one host holding one part per axis. A decorator-style part (`WithBonus(inner, 500)`) wraps another part to stack behavior.
- **Diamond**: Python solves it with the MRO and cooperative `super()`; composition avoids it by holding parts side by side.
- **Inheritance is right** for a real, stable is-a (Liskov holds): custom exception hierarchies, framework base classes (`Exception`, `Thread`, `TestCase`), small interface-only ABCs, `class Celsius(float)`.

## Gotchas (the part worth revising twice)
- **Fragile base class**: a subclass that overrides `add()` and `add_all()` counts items twice the day the parent's `add_all()` starts calling `add()`. The child never changed; the parent's internals did. Wrapping the parent instead of inheriting is immune.
- `__getattr__` only catches **reads** (writes land on the wrapper), and does **not** forward dunders (`len(w)`, `w[i]`, `with w`) because those are looked up on the class. Guard names starting with `_` or you get infinite recursion.
- Forwarded methods are invisible to IDEs, `dir()` and type checkers.
- A wrapper is not an instance of the inner type: `isinstance(wrapper, list)` is `False`.
- `Protocol` is checked by type checkers, not at runtime. `@runtime_checkable` + `isinstance` only checks method **names**, never signatures.
- Mixin traps: forgetting the method the mixin needs (error only at call time), two mixins with the same method (left silently wins), a mixin placed to the right of a base that already defines the method (dead code), stateful mixins with their own `__init__`.
- One forgotten `super()` call in a diamond silently skips the rest of the chain.
- Default argument `def __init__(self, part=Printer())` creates one part shared by every host. Use `None` and build inside.
- Inheriting only to reuse code leaks the parent's public methods (`BadOrder().send` exists) and creates a false is-a.
- Do not over-split: too many tiny parts is its own mess. Split only along real axes of change.

## When it matters
Whenever you are about to write `class A(B)` just to reuse code, when behavior varies in several independent ways, when you must swap behavior at runtime or in tests, or when a third-party parent class may change under you. Related files: `03-Inheritance.py` (MRO, super), `05-Abstraction.py` (ABC vs Protocol), `08-SOLID-Principles.py` (Liskov, Dependency Inversion), `07-Custom-Containers-And-ABCs.py`.

## One-line recap example
```python
class Order:
    def __init__(self, notifier):      # has-a, injected; any object with .send(...) works
        self.notifier = notifier
    def place(self):
        return self.notifier.send("order placed")
```
