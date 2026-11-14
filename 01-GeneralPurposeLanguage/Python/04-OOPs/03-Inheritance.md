# Inheritance — Notes

## What this covers
How a class can reuse and extend another class's code: overriding methods, `super()`, the five "types" of inheritance (single, multi-level, hierarchical, multiple, hybrid), MRO/the diamond problem, and mixins.

## Key points
- Inheritance lets a **derived (child) class** reuse attributes/methods from a **base (parent) class**, forming an "is-a" relationship (a `Dog` is an `Animal`). It's the main tool for following **DRY** (Don't Repeat Yourself).
- A subclass inherits public/protected members automatically, but NOT the constructor logic itself — you must explicitly call `super().__init__(...)` to run the parent's `__init__`.
- **Method overriding**: a subclass defines a method with the same name as the parent's — calling it on a subclass instance runs the subclass's version.
- **`super()`** calls the parent class's version of a method — used to extend (not fully replace) inherited behavior, especially in `__init__`.
- **Types of inheritance**: single (one parent), multi-level (a chain, A→B→C), hierarchical (multiple children from one parent), multiple (one child, several parents), hybrid (a combination of the above).
- **MRO (Method Resolution Order)**: `ClassName.__mro__` shows the exact order Python searches classes for a method. Computed via **C3 linearization**: a class always comes before its parents, and parents keep their left-to-right listed order.
- **Mixins**: small classes meant to be combined via multiple inheritance to add one focused piece of behavior — not meant to be instantiated alone, conventionally named `...Mixin`.
- `isinstance(obj, Cls)` respects the whole inheritance hierarchy (true for subclasses too); `type(obj) == Cls` only matches the exact class. Prefer `isinstance()`.

## Gotchas (the part worth revising twice)
- **The diamond problem**: if `B` and `C` both inherit from `A`, and `D` inherits from both `B` and `C`, `A` could get initialized twice. Fix: use `super().__init__()` in every level (not a hardcoded parent name) — this is "cooperative" `super()` and, following the MRO, makes `A.__init__` run exactly once.
- MRO order depends on how you list the parents: `class Bottom(Left, Right)` puts `Left` ahead of `Right` in the search order — `Bottom.__mro__` is `Bottom → Left → Right → Base → object`.
- **`raise NotImplementedError` is just a convention**, not enforcement: `class ForgottenPayment(PaymentMethodConvention): pass` instantiates just fine — the error only surfaces the moment `pay()` is actually called, which could be much later in production. A real ABC (`@abstractmethod`) catches this at instantiation instead (see 05-Abstraction.py).
- Private (`__`) members are technically inherited but not directly accessible in the subclass due to name mangling — they still exist on the instance, just under a mangled name tied to the class that defined them.
- Multiple inheritance can silently reorder which parent's method "wins" if you don't understand MRO — always check `.__mro__` when a shared ancestor is involved.

## When it matters
Reach for inheritance when multiple classes genuinely share behavior and form a real "is-a" relationship — for mixing in unrelated bits of reusable behavior, prefer mixins or composition over deep inheritance chains.

## One-line recap example
```python
class Animal:
    def speak(self):
        return "..."

class Dog(Animal):
    def speak(self):          # method overriding
        return "Woof!"
```
