from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

# 01. Is-A vs Has-A
# ------------------------------------
# - Inheritance = "is-a":  a Dog IS an Animal. The child gets the parent's whole public surface.
# - Composition = "has-a": a Car HAS an Engine. The car holds an engine object and USES it.
# - Inheritance basics: see 03-Inheritance.py. This file is about CHOOSING between the two.
# - Quick test: can you say "X is a Y" in every situation, forever, without exceptions?
#   If not, use has-a. A Stack is not a List (you cannot insert in the middle of a stack).
class Engine:
    def start(self):
        return "engine running"

class Car:
    def __init__(self):
        self.engine = Engine()          # has-a
    def drive(self):
        return f"car drives, {self.engine.start()}"

print("# 01. Is-A vs Has-A")
print(Car().drive())

# 02. Favor Composition Over Inheritance - Why
# ------------------------------------
# - Inheritance is the TIGHTEST coupling in Python: the child depends on the parent's methods, attributes
#   AND its internal call order.
# - Composition keeps objects behind a small interface, so parts can be swapped, tested and reused alone.
# - Inheritance is fixed at class-definition time; a composed part can change at runtime (section 7).
# - Inheritance leaks everything: a Stack that inherits list also exposes insert(), sort(), reverse()...
# - It is a guideline ("favor"), not a ban. Section 18 shows when inheritance wins.
class BadStack(list):
    def push(self, x):
        self.append(x)

class Stack:
    def __init__(self):
        self._items = []                # hidden: callers cannot break the stack rule
    def push(self, x):
        self._items.append(x)
    def pop(self):
        return self._items.pop()
    def __len__(self):
        return len(self._items)

print("\n# 02. Favor Composition Over Inheritance - Why")
bad = BadStack()
bad.push(1); bad.push(2)
bad.insert(0, "oops")                   # allowed, and it breaks stack discipline
print("BadStack after insert(0):", list(bad))
good = Stack()
good.push(1); good.push(2)
print("Stack has insert?", hasattr(good, "insert"), "| pop ->", good.pop(), "| len ->", len(good))

# 03. Delegation - Forwarding Calls by Hand
# ------------------------------------
# - Delegation: the outer object receives a call and passes it to the inner object.
# - Explicit forwarding methods are boring but clear: you expose ONLY what you choose to.
# - Cost: one tiny wrapper per method. For many methods see __getattr__ in section 4.
class Printer:
    def print_text(self, text):
        return f"printing: {text}"
    def status(self):
        return "idle"

class Office:
    def __init__(self):
        self._printer = Printer()
    def print_text(self, text):               # explicit delegation
        return self._printer.print_text(text)

print("\n# 03. Delegation - Forwarding Calls by Hand")
off = Office()
print(off.print_text("report"))
print("status exposed?", hasattr(off, "status"), "(not forwarded on purpose)")

# 04. Delegation with __getattr__
# ------------------------------------
# - __getattr__(name) is called ONLY when normal lookup fails, so it is a perfect fallback to forward to the inner object.
# - Gotchas:
#   * It only catches READS. Writes (obj.x = 1) land on the wrapper unless you also define __setattr__.
#   * Dunder methods (len(obj), obj[i], for, with) are looked up on the CLASS, not the instance, so
#     __getattr__ does NOT forward them. You must define them explicitly.
#   * Forwarding a name before the inner object exists loops forever (RecursionError): guard names
#     starting with "_" or use object.__getattribute__ inside __getattr__.
#   * It hides the real interface: IDEs, dir() and type checkers cannot see forwarded methods.
class Logged:
    """Wraps any object and logs every forwarded method call."""
    def __init__(self, target):
        self._target = target
    def __getattr__(self, name):
        if name.startswith("_"):                  # protects against recursion
            raise AttributeError(name)
        attr = getattr(self._target, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                print(f"   -> calling {name}{args}")
                return attr(*args, **kwargs)
            return wrapper
        return attr

print("\n# 04. Delegation with __getattr__")
lg = Logged([3, 1, 2])
lg.append(0)
lg.sort()
print("inner list now:", lg._target)
lg.extra = "set on the wrapper, not the list"
print("write landed on wrapper:", "extra" in lg.__dict__, "| list has extra:", hasattr(lg._target, "extra"))
try:
    len(lg)
except TypeError as e:
    print("len(wrapper) ->", e)

class Fixed(Logged):
    def __len__(self):
        return len(self._target)
print("after adding __len__ explicitly:", len(Fixed([1, 2, 3])))

# 05. Inheriting Just to Reuse Code - The Smell
# ------------------------------------
# - "I need the helper methods, so I will subclass" makes a false is-a and inherits baggage you do not want.
# - Fix: keep the helper in its own class (or plain function) and HOLD it.
# - Also ask: do I need a class at all? A plain function is the lightest form of reuse.
class Notifier:
    def send(self, to, msg):
        return f"sent '{msg}' to {to}"

class BadOrder(Notifier):                 # an Order is not a Notifier!
    def place(self):
        return self.send("customer", "order placed")

class Order:
    def __init__(self, notifier):
        self.notifier = notifier          # has-a, injected
    def place(self):
        return self.notifier.send("customer", "order placed")

print("\n# 05. Inheriting Just to Reuse Code - The Smell")
print("BadOrder exposes send() publicly:", hasattr(BadOrder(), "send"))
print("Order:", Order(Notifier()).place())

# 06. Strategy by Composition
# ------------------------------------
# - Strategy pattern: put the part that varies behind a small interface and pass it in.
# - Inheritance version: one subclass per variation, and combinations explode (2 axes x 3 options = 6 classes).
# - Composition version: one class + pick one object per axis (2 + 3 = 5 small pieces, any mix).
# - In Python a strategy can be as light as a function or lambda. Patterns catalogue: see 14-Creational-Design-Patterns.py
#   and 16-Behavioral-Design-Patterns.py; SOLID link: 08-SOLID-Principles.py (Open/Closed).
class Discount:
    def apply(self, price): return price
class TenPercent(Discount):
    def apply(self, price): return price * 0.9
class Flat5(Discount):
    def apply(self, price): return price - 5

class Cart:
    def __init__(self, discount, tax_rate):
        self.discount = discount
        self.tax_rate = tax_rate
    def total(self, price):
        return round(self.discount.apply(price) * (1 + self.tax_rate), 2)

print("\n# 06. Strategy by Composition")
print("10% off, 10% tax:", Cart(TenPercent(), 0.10).total(100))
print("flat 5 off, 20% tax:", Cart(Flat5(), 0.20).total(100))
print("function as strategy:", sum(f(100) for f in [lambda p: p * 0.5]))

# 07. Swapping Behavior at Runtime
# ------------------------------------
# - A composed part is just an attribute, so you can replace it while the program runs.
# - This is the State pattern idea: the object changes behavior by changing what it holds.
# - A class's base classes cannot be changed this simply, so "is-a" is frozen at definition time.
class Walk:
    def move(self): return "walking"
class Swim:
    def move(self): return "swimming"

class Creature:
    def __init__(self, mover):
        self.mover = mover
    def move(self):
        return self.mover.move()

print("\n# 07. Swapping Behavior at Runtime")
cr = Creature(Walk())
print("on land :", cr.move())
cr.mover = Swim()
print("in water:", cr.move())

# 08. Protocol - Structural Typing for Dependencies
# ------------------------------------
# - typing.Protocol describes the SHAPE a dependency must have; any class with those methods fits,
#   no inheritance, no registration (ABC vs Protocol: see 05-Abstraction.py).
# - Perfect for composition: "I need something with .send(msg)" instead of "I need a Notifier subclass".
# - Protocols are checked by type checkers (mypy, pyright), NOT at runtime. Python itself stays duck-typed.
# - @runtime_checkable allows isinstance(), but it only checks that the method NAMES exist, not signatures.
@runtime_checkable
class Sender(Protocol):
    def send(self, msg: str) -> str: ...

class EmailSender:                      # note: does not inherit Sender
    def send(self, msg: str) -> str:
        return f"email: {msg}"

class SmsSender:
    def send(self, msg: str) -> str:
        return f"sms: {msg}"

class AlertService:
    def __init__(self, sender: Sender):  # depends on the shape only
        self.sender = sender
    def alert(self, text):
        return self.sender.send(f"ALERT {text}")

class FakeSender:                        # a test double, no inheritance either
    def __init__(self):
        self.sent = []
    def send(self, msg):
        self.sent.append(msg)
        return "ok"

print("\n# 08. Protocol - Structural Typing for Dependencies")
print(AlertService(EmailSender()).alert("disk full"))
print(AlertService(SmsSender()).alert("disk full"))
fake = FakeSender()
AlertService(fake).alert("test")
print("test double recorded:", fake.sent)
print("isinstance(EmailSender(), Sender):", isinstance(EmailSender(), Sender))
print("isinstance(object(), Sender)     :", isinstance(object(), Sender))

class WrongSignature:
    def send(self):                      # wrong parameters
        return "?"
print("runtime check cannot see bad signature:", isinstance(WrongSignature(), Sender))

# 09. Dependency Injection - The Natural Partner
# ------------------------------------
# - "Has-a" is best when the part is PASSED IN (constructor arguments) instead of built inside.
# - Built inside:  hard to test, hard to swap (Order creates its own Notifier).
# - Passed in:     tests inject a fake, production injects the real one (sections 5 and 8; Dependency Inversion in 08-SOLID-Principles.py).
# - Offer a sensible default so callers who do not care can ignore it.
class Report:
    def __init__(self, sender=None):
        self.sender = sender or EmailSender()     # default dependency
    def publish(self):
        return self.sender.send("report ready")

print("\n# 09. Dependency Injection - The Natural Partner")
print("default :", Report().publish())
print("injected:", Report(SmsSender()).publish())

# 10. Mixins Done Right
# ------------------------------------
# - A mixin is a small class that adds ONE focused capability and is not meant to stand alone.
# - Rules for healthy mixins:
#   * One job, narrow name ending in Mixin (JsonMixin, ReprMixin).
#   * No __init__ of its own and no state, or only well-named state.
#   * Depend on a tiny, documented contract from the host class ("needs self.to_dict()").
#   * Put mixins on the LEFT of the base list so their methods win (MRO: see 03-Inheritance.py).
#   * Call super() in cooperative methods so the chain is not broken.
# - Use a mixin for a behavior shared by UNRELATED classes; use composition when the behavior needs its own state/lifecycle.
import json

class JsonMixin:
    """Needs the host to provide .to_dict()."""
    def to_json(self):
        return json.dumps(self.to_dict(), sort_keys=True)

class ReprMixin:
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in sorted(vars(self).items()))
        return f"{type(self).__name__}({fields})"

class User(JsonMixin, ReprMixin):
    def __init__(self, name, age):
        self.name, self.age = name, age
    def to_dict(self):
        return {"name": self.name, "age": self.age}

class Product(JsonMixin, ReprMixin):
    def __init__(self, sku):
        self.sku = sku
    def to_dict(self):
        return {"sku": self.sku}

print("\n# 10. Mixins Done Right")
print(User("ann", 30).to_json(), "|", Product("A1").to_json())
print(repr(User("ann", 30)))
print("MRO:", [c.__name__ for c in User.__mro__])

# 11. Mixin Pitfalls
# ------------------------------------
# - Hidden contract: a mixin calls a method the host must define. Forget it and you get an AttributeError at call time.
# - Name clashes: two mixins both define save(); the LEFT one silently wins.
# - Order matters: putting a mixin on the right of a base that already defines the method makes the mixin dead code.
# - Mixins with state and their own __init__ create diamond/ordering headaches. Prefer composition for stateful parts.
# - If your mixin list reaches 4-5 classes, you are building a deep hierarchy in disguise.
class Broken(JsonMixin):
    pass                                # forgot to_dict

class SaveA:
    def save(self): return "A.save"
class SaveB:
    def save(self): return "B.save"
class Both(SaveA, SaveB):
    pass
class Base:
    def save(self): return "Base.save"
class Late(Base, SaveA):                # mixin on the right: never reached
    pass

print("\n# 11. Mixin Pitfalls")
try:
    Broken().to_json()
except AttributeError as e:
    print("missing contract ->", e)
print("clash, left wins:", Both().save())
print("mixin on the right is dead code:", Late().save())

# 12. The Fragile Base Class Problem
# ------------------------------------
# - A subclass depends on HOW the parent works inside, not only on what it promises.
# - A harmless-looking change in the parent (an internal method now calls another one) breaks the child.
# - Classic example: a counting list overrides add() and addAll(). If the parent's addAll() calls add() internally,
#   items are counted twice. Whether it does is an implementation detail the child cannot see.
# - Defences: prefer composition; document which methods are safe to override; mark classes final by convention.
class Bag:
    def __init__(self):
        self.items = []
    def add(self, x):
        self.items.append(x)
    def add_all(self, xs):                 # version 1: loops by itself
        for x in xs:
            self.items.append(x)

class CountingBag(Bag):
    def __init__(self):
        super().__init__()
        self.count = 0
    def add(self, x):
        self.count += 1
        super().add(x)
    def add_all(self, xs):
        self.count += len(xs)
        super().add_all(xs)

print("\n# 12. The Fragile Base Class Problem")
c1 = CountingBag()
c1.add_all([1, 2, 3])
print("parent v1 -> count:", c1.count, "(correct)")

def new_add_all(self, xs):                 # parent v2: "refactored" to reuse add()
    for x in xs:
        self.add(x)
Bag.add_all = new_add_all                  # simulate the parent's new release
c2 = CountingBag()
c2.add_all([1, 2, 3])
print("parent v2 -> count:", c2.count, "(wrong! child never changed)")

# the composition fix: wrap, do not inherit
class CountingBagSafe:
    def __init__(self):
        self._bag = Bag()
        self.count = 0
    def add(self, x):
        self.count += 1
        self._bag.add(x)
    def add_all(self, xs):
        for x in xs:
            self.add(x)                    # our own code decides, parent internals do not matter
c3 = CountingBagSafe()
c3.add_all([1, 2, 3])
print("composition  -> count:", c3.count, "(correct whatever the parent does)")

# 13. Refactoring an Inheritance Tree into Composition
# ------------------------------------
# - Smell: the tree has several independent axes (what it IS x how it MOVES x how it ATTACKS).
#   Every new combination needs a new subclass: Robot, FlyingRobot, SwimmingRobot, FlyingShootingRobot...
# - Steps:
#   1. Name each axis of variation.
#   2. Give each axis a tiny interface (Protocol or simple base).
#   3. Replace the subclasses with ONE class that holds one object per axis.
#   4. Build combinations by passing parts in. No new class needed.
# Before: the explosion
class Unit:
    def describe(self): return "unit"
class FlyingUnit(Unit):
    def describe(self): return "unit that flies"
class ArmedUnit(Unit):
    def describe(self): return "unit that shoots"
class FlyingArmedUnit(FlyingUnit, ArmedUnit):   # needs its own class for the mix
    def describe(self): return "unit that flies and shoots"

# After: parts + one host
class Fly:
    name = "flies"
class Crawl:
    name = "crawls"
class Gun:
    name = "shoots"
class Unarmed:
    name = "is harmless"

class Agent:
    def __init__(self, movement, weapon):
        self.movement, self.weapon = movement, weapon
    def describe(self):
        return f"unit that {self.movement.name} and {self.weapon.name}"

print("\n# 13. Refactoring an Inheritance Tree into Composition")
print("before:", FlyingArmedUnit().describe(), "| classes needed for 2x2 mixes: 4+")
for mv in (Fly(), Crawl()):
    for wp in (Gun(), Unarmed()):
        print("after :", Agent(mv, wp).describe())

# 14. Refactoring Example - Employees and Pay
# ------------------------------------
# - Before: Employee -> Manager / Engineer, each overriding pay(). Now a manager is promoted to a contractor:
#   you cannot change an existing object's class tree, you would have to rebuild it.
# - After: Employee HAS a PayPolicy. A promotion is just `emp.policy = NewPolicy()`.
# - Tests get easier too: test each policy on its own, no Employee needed.
class Salaried:
    def __init__(self, yearly): self.yearly = yearly
    def monthly(self): return round(self.yearly / 12, 2)
class Hourly:
    def __init__(self, rate, hours): self.rate, self.hours = rate, hours
    def monthly(self): return self.rate * self.hours
class WithBonus:
    """Decorator-style composition: wraps another policy and adds to it."""
    def __init__(self, inner, bonus): self.inner, self.bonus = inner, bonus
    def monthly(self): return self.inner.monthly() + self.bonus

class Employee:
    def __init__(self, name, policy):
        self.name, self.policy = name, policy
    def pay(self):
        return f"{self.name}: {self.policy.monthly()}"

print("\n# 14. Refactoring Example - Employees and Pay")
e = Employee("sam", Hourly(20, 100))
print(e.pay())
e.policy = Salaried(60000)                      # changed role, same object
print(e.pay())
e.policy = WithBonus(Salaried(60000), 500)      # stack behaviors
print(e.pay())

# 15. Diamond Problem - Solved by Composition
# ------------------------------------
# - Diamond: D(B, C), both B and C extend A. Which A-method runs? Python answers with the MRO (C3 linearization),
#   and cooperative super() calls make it work, but it needs discipline from EVERY class in the chain.
# - Gotcha: if one class forgets to call super(), the rest of the chain is silently skipped.
# - With composition there is no diamond: the host holds its parts side by side and calls each one by name.
#   Nothing is inherited, so nothing is ambiguous.
class A:
    def hello(self): return ["A"]
class B(A):
    def hello(self): return ["B"] + super().hello()
class C(A):
    def hello(self): return ["C"] + super().hello()
class D(B, C):
    def hello(self): return ["D"] + super().hello()

class BadB(A):
    def hello(self): return ["BadB"]            # forgot super(): chain stops here
class E(BadB, C):
    def hello(self): return ["E"] + super().hello()

print("\n# 15. Diamond Problem - Solved by Composition")
print("D.mro:", [k.__name__ for k in D.__mro__])
print("cooperative chain:", D().hello())
print("one forgotten super():", E().hello(), "(C was skipped)")

class Part1:
    def hello(self): return "part1"
class Part2:
    def hello(self): return "part2"
class Host:
    def __init__(self):
        self.p1, self.p2 = Part1(), Part2()
    def hello(self):
        return [self.p1.hello(), self.p2.hello()]   # explicit, no MRO
print("composition:", Host().hello())

# 16. Composition with Abstract Parts
# ------------------------------------
# - You can still use ABCs (05-Abstraction.py) for the PARTS. That is inheritance used correctly:
#   small, stable, interface-only base classes; the host itself stays flat.
# - Gotcha: do not let the ABC grow data and logic over time, it becomes the fragile base class again (section 12).
class Storage(ABC):
    @abstractmethod
    def save(self, key, value): ...
    @abstractmethod
    def load(self, key): ...

class MemoryStorage(Storage):
    def __init__(self): self.d = {}
    def save(self, key, value): self.d[key] = value
    def load(self, key): return self.d[key]

class Cache:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.hits = 0
    def get(self, key, compute):
        try:
            value = self.storage.load(key)
            self.hits += 1
        except KeyError:
            value = compute()
            self.storage.save(key, value)
        return value

print("\n# 16. Composition with Abstract Parts")
cache = Cache(MemoryStorage())
print(cache.get("k", lambda: "computed"), cache.get("k", lambda: "computed again"), "| hits:", cache.hits)
try:
    Storage()
except TypeError as e:
    print("abstract part cannot be built ->", e)

# 17. Composition Gotchas
# ------------------------------------
# - Boilerplate: forwarding methods by hand is verbose. Accept it, or use __getattr__ (section 4) knowing its limits.
# - Broken identity: wrapper is NOT an instance of the inner type, so isinstance(wrapper, list) is False.
#   If code downstream needs isinstance, composition may not fit (or register an ABC).
# - Lifecycle: who creates, owns and closes the part? Say it in the docstring. Shared parts mutated by two owners cause bugs.
# - Mutable default part: def __init__(self, engine=Engine()) shares ONE engine between all hosts.
# - Too many tiny parts is its own mess: split only along real axes of change.
# - Law of Demeter: call self.engine.start(), avoid reaching through a.b.c.d.do() chains.
class Host2:
    def __init__(self, part=Printer()):         # one Printer shared by every Host2 - the bug
        self.part = part

print("\n# 17. Composition Gotchas")
print("wrapper is a list?", isinstance(Logged([]), list))
print("default part shared between hosts:", Host2().part is Host2().part)

class Host3:
    def __init__(self, part=None):
        self.part = part if part is not None else Printer()   # fresh part per host
print("fixed with None default:", Host3().part is Host3().part)

# 18. When Inheritance IS Right
# ------------------------------------
# - True is-a with the Liskov rule (08-SOLID-Principles.py): a child can be used anywhere the parent is used, no surprises.
# - Good cases:
#   * Real taxonomy with shared data AND behavior that is stable (Shape -> Circle, Square).
#   * Frameworks that expect you to subclass (Exception, unittest.TestCase, Thread, ABCs like Mapping - see 07-...py).
#   * Custom exceptions: always inherit, so `except Base` catches the family (see 03-Inheritance.py).
#   * Extending a type to add a little: class Celsius(float).
#   * Interface-only hierarchies (ABC/Protocol) with no shared state.
# - Inheritance in one line of advice: shallow (1-2 levels), stable parent, you control the parent, real is-a.
class AppError(Exception):
    pass
class DbError(AppError):
    pass

class Shape(ABC):
    def describe(self):                    # shared, stable behavior
        return f"{type(self).__name__} with area {self.area():.1f}"
    @abstractmethod
    def area(self): ...
class Square(Shape):
    def __init__(self, s): self.s = s
    def area(self): return self.s ** 2
class Circle(Shape):
    def __init__(self, r): self.r = r
    def area(self): return 3.14159 * self.r ** 2

print("\n# 18. When Inheritance IS Right")
try:
    raise DbError("connection lost")
except AppError as e:
    print("caught family via base class:", type(e).__name__, "-", e)
for sh in (Square(2), Circle(1)):
    print(sh.describe())

# 19. Decision Guide and Summary
# ------------------------------------
# - Ask in this order:
#   1. Is it truly is-a, always, and does the child obey every promise of the parent (Liskov)? No -> composition.
#   2. Do I only want to reuse code? -> composition or a plain function.
#   3. Does the behavior vary along independent axes? -> strategy parts (sections 6, 13).
#   4. Need to change behavior at runtime? -> composition (section 7).
#   5. Do I own the parent, and is it stable and small? Yes -> inheritance is fine.
#   6. Same capability on unrelated classes, stateless? -> a mixin (section 10).
#   7. Depending on a thing I do not control? -> Protocol + injection (sections 8, 9).
# - The aim is not "never inherit". It is: use the loosest coupling that does the job.
print("\n# 19. Decision Guide and Summary")
print("Rule of thumb: inherit for a true is-a with a stable parent, compose for everything else.")
