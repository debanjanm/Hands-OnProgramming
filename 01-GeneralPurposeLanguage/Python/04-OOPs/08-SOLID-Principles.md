# SOLID Principles — Notes

## What this covers
Five OOP design principles that make code easier to maintain and extend, each shown with a "bad" version and a "good" fix, plus a combined example showing them reinforcing each other.

## Key points
- **S — Single Responsibility**: a class should have only one reason to change. Bad: one `Invoice` class does both math AND printing. Good: split into `Invoice` (math) and `InvoicePrinter` (display) — each has one job.
- **O — Open/Closed**: code should be open for extension but closed for modification. Bad: an `if/elif` chain on `shape["type"]` that needs editing for every new shape. Good: each shape is its own class implementing `area()` — `total_area()` never changes when a new shape is added.
- **L — Liskov Substitution**: a subclass must be usable anywhere its parent is expected, without breaking correctness. Bad: `SquareBad(RectangleBad)` overrides `set_width`/`set_height` to change both dimensions at once, silently breaking code that assumes setting width doesn't touch height.
- **I — Interface Segregation**: don't force a class to implement methods it doesn't need — prefer several small, focused interfaces over one large one. Bad: a fat `WorkerBad` interface forces a `Robot` to implement `eat()`. Good: split into `Workable` and `Eatable`, implement only what applies.
- **D — Dependency Inversion**: depend on abstractions, not concrete implementations. Bad: `NotifierBad` is hard-wired to `EmailSenderBad` inside its own `__init__`. Good: `Notifier` takes any `MessageSender` (an ABC) injected from outside — swapping senders needs no edit to `Notifier`.

## Gotchas (the part worth revising twice)
- **Liskov violations often look "correct" in real-world terms but break code**: a `Square` really *is* a kind of `Rectangle` conceptually, but forcing it to inherit `Rectangle`'s mutable `set_width`/`set_height` interface breaks any code that assumes those two are independent — the fix is usually to not model it as inheritance at all.
- **The combined example (#08) shows SRP + OCP + DIP reinforcing each other**: `NotificationService` has one job (fan out messages — SRP), new channels like `PushSender` are added without touching existing code (OCP), and the dispatcher only ever depends on the `MessageSender` abstraction, never a concrete sender (DIP).
- **SOLID is not dogma — it's a tool, not a checklist**: for a 50-line script or throwaway prototype, applying all five principles is over-engineering — the extra classes/interfaces add indirection with no future change to protect against. Apply it when a codebase is large, long-lived, or has multiple contributors and changing requirements; write the simple direct version first, then introduce structure when duplication/fragility actually shows up as pain.

## When it matters
Reach for SOLID when a codebase will be maintained and extended by more than just you over time — it pays off by making future changes safer and cheaper, at the cost of some upfront indirection.

## One-line recap example
```python
class Notifier:
    def __init__(self, sender: MessageSender):  # depends on abstraction, not EmailSender directly
        self.sender = sender
    def notify(self, message):
        self.sender.send(message)   # any MessageSender works - swap freely (DIP)
```
