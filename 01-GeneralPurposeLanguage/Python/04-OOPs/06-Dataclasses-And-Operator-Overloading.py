from dataclasses import dataclass, field

# 01. Dataclasses - Introduction
# ------------------------------------
# - @dataclass auto-generates boilerplate like __init__, __repr__, __eq__
#   for classes that mainly hold data.
# - Reduces repetitive code compared to writing these methods by hand.

print("# 01. Dataclasses - Introduction")
print("# ------------------------------------")

# 02. Basic Dataclass
# ------------------------------------
@dataclass
class Point:
    x: int
    y: int

p1 = Point(2, 3)
p2 = Point(2, 3)
print("\n# 02. Basic Dataclass")
print(p1)                 # auto __repr__ -> Point(x=2, y=3)
print(p1 == p2)            # auto __eq__ -> True (compares field values)

# 03. Default Values and default_factory
# ------------------------------------
@dataclass
class Student:
    name: str
    grades: list = field(default_factory=list)  # mutable defaults need default_factory
    passed: bool = False

s = Student("Debanjan")
s.grades.append(90)
print("\n# 03. Default Values and default_factory")
print(s)

# 04. Immutable Dataclass (frozen=True)
# ------------------------------------
@dataclass(frozen=True)
class ImmutablePoint:
    x: int
    y: int

ip = ImmutablePoint(1, 1)
print("\n# 04. Immutable Dataclass (frozen=True)")
print(ip)
try:
    ip.x = 5
except Exception as e:
    print(f"Error modifying frozen instance: {e}")

# 05. Operator Overloading - Introduction
# ------------------------------------
# - Python lets custom classes define behavior for built-in operators
#   (+, -, ==, <, etc.) by implementing special/dunder methods.
print("\n# 05. Operator Overloading - Introduction")
print("# - Implement __add__, __eq__, __lt__, etc. to support operators.")

# 06. Overloading Arithmetic Operators
# ------------------------------------
class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"

v1 = Vector(2, 3)
v2 = Vector(4, 1)
print("\n# 06. Overloading Arithmetic Operators")
print("v1 + v2 =", v1 + v2)
print("v1 - v2 =", v1 - v2)
print("v1 * 3 =", v1 * 3)

# 07. Overloading Comparison Operators
# ------------------------------------
class Money:
    def __init__(self, amount):
        self.amount = amount

    def __eq__(self, other):
        return self.amount == other.amount

    def __lt__(self, other):
        return self.amount < other.amount

    def __le__(self, other):
        return self.amount <= other.amount

    def __repr__(self):
        return f"Money({self.amount})"

m1 = Money(100)
m2 = Money(200)
print("\n# 07. Overloading Comparison Operators")
print("m1 == m2:", m1 == m2)
print("m1 < m2:", m1 < m2)
print("sorted:", sorted([m2, m1]))  # uses __lt__

# 08. Other Common Dunder Methods
# ------------------------------------
class Cart:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def __contains__(self, item):
        return item in self.items

    def __getitem__(self, index):
        return self.items[index]

    def __iter__(self):
        return iter(self.items)

    def add(self, item):
        self.items.append(item)

cart = Cart()
cart.add("apple")
cart.add("bread")
print("\n# 08. Other Common Dunder Methods")
print("len(cart):", len(cart))            # __len__
print("'apple' in cart:", "apple" in cart)  # __contains__
print("cart[0]:", cart[0])                  # __getitem__
for item in cart:                           # __iter__
    print("item:", item)

# 09. __post_init__ for Derived/Validated Fields
# ------------------------------------
# - __post_init__ runs automatically right after the generated __init__
#   finishes - the place to validate input or compute fields derived from
#   other fields, without hand-writing a custom __init__.
@dataclass
class Rectangle:
    width: float
    height: float
    area: float = field(init=False) # not passed in, computed in __post_init__
    def __post_init__(self):
        if self.width <= 0 or self.height <= 0:
            raise ValueError("width and height must be positive")
        self.area = self.width * self.height # derived field

print("\n# 09. __post_init__ for Derived/Validated Fields")
rect = Rectangle(4, 5)
print("rect:", rect)
try:
    Rectangle(-1, 5)
except ValueError as e:
    print("Caught validation error:", e)

# 10. field(compare=False) and field(repr=False)
# ------------------------------------
# - compare=False: excludes a field from the generated __eq__ (and order
#   comparisons) - two instances can be "equal" even if this field differs.
# - repr=False: excludes a field from the generated __repr__ output entirely.
@dataclass
class User:
    name: str
    id: int = field(compare=False)          # ignored by __eq__
    password_hash: str = field(repr=False, default="") # hidden from __repr__

u1 = User("Alice", 1)
u2 = User("Alice", 2) # different id, but id is excluded from comparison
print("\n# 10. field(compare=False) and field(repr=False)")
print("u1 == u2 (id excluded from comparison):", u1 == u2)
print("repr(u1) (password_hash hidden):", repr(u1))

# 11. order=True for Auto Comparison Methods
# ------------------------------------
# - order=True generates __lt__, __le__, __gt__, __ge__ automatically, using
#   fields in declaration order (like comparing tuples of the field values).
@dataclass(order=True)
class Version:
    major: int
    minor: int
    patch: int

v1 = Version(1, 2, 0)
v2 = Version(1, 3, 0)
print("\n# 11. order=True for Auto Comparison Methods")
print("v1 < v2:", v1 < v2)   # compares (major, minor, patch) tuple-wise
print("sorted:", sorted([v2, v1]))

# 12. Dataclass Inheritance - Field Ordering Rules
# ------------------------------------
# - Fields from the base class come first, then the subclass's own fields.
# - A field WITHOUT a default cannot follow a field WITH a default in the
#   combined list - so if the base class has a defaulted field, every field
#   the subclass adds must also have a default (or use kw_only, 3.10+).
@dataclass
class Animal:
    name: str
    legs: int = 4 # has a default

@dataclass
class Dog(Animal):
    breed: str = "unknown" # must also have a default - follows a defaulted base field

print("\n# 12. Dataclass Inheritance - Field Ordering Rules")
print("Dog('Rex', 4, 'Labrador'):", Dog("Rex", 4, "Labrador"))
print("# - Animal.legs has a default, so Dog.breed is also forced to have one -")
print("#   'non-default argument follows default argument' would be a TypeError otherwise.")

# 13. slots=True Dataclass (Python 3.10+) - Memory Savings
# ------------------------------------
# - slots=True auto-generates __slots__ for the dataclass, combining
#   dataclass convenience with the memory savings covered in 01-Class-Object.py.
@dataclass(slots=True)
class LightPoint:
    x: int
    y: int

print("\n# 13. slots=True Dataclass")
lp = LightPoint(1, 2)
print("lp:", lp)
print("hasattr(lp, '__dict__'):", hasattr(lp, "__dict__")) # False - no __dict__, uses slots
try:
    lp.z = 3
except AttributeError as e:
    print("lp.z = 3 -> AttributeError:", e)

# 14. __radd__ and __iadd__ (Reflected and In-Place Operators)
# ------------------------------------
# - __add__(self, other) handles `self + other`.
# - __radd__(self, other) is the fallback for `other + self`, used when
#   `other`'s own __add__ doesn't know how to handle a Vector (e.g. int + Vector).
# - __iadd__(self, other) backs the in-place `self += other`; if omitted,
#   Python falls back to __add__ (a += b becomes a = a.__add__(b)).
class VectorOps:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __add__(self, other):
        return VectorOps(self.x + other.x, self.y + other.y)
    def __radd__(self, other):
        if other == 0: # supports sum([...]) which starts with 0 + first_element
            return self
        return self.__add__(other)
    def __iadd__(self, other):
        self.x += other.x # mutates in place instead of creating a new object
        self.y += other.y
        return self
    def __repr__(self):
        return f"VectorOps({self.x}, {self.y})"

v = VectorOps(1, 1)
print("\n# 14. __radd__ and __iadd__")
print("0 + VectorOps(1,1) (uses __radd__):", 0 + VectorOps(1, 1))
print("sum([VectorOps(1,1), VectorOps(2,2)]):", sum([VectorOps(1, 1), VectorOps(2, 2)]))
v += VectorOps(5, 5) # uses __iadd__, mutates v in place
print("v after += (uses __iadd__, mutated in place):", v)


# 15. Unary Operators - __neg__, __pos__, __abs__, __invert__ (+ __round__/__trunc__)
# ------------------------------------
# - Unary = one operand: -x, +x, abs(x), ~x. Each has its own dunder.
# - Convention: return a NEW object, don't mutate self (x.__neg__ is an expression, not a command).
# - If the method is missing you get "bad operand type for unary -: 'X'".
# - __invert__ (~) is bitwise NOT for ints; for your own class it can mean anything
#   sensible - here: swap x and y. Don't invent meanings that surprise readers.
import math

class Vec2:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __neg__(self):             # -v
        return Vec2(-self.x, -self.y)
    def __pos__(self):             # +v  (usually "return a copy"; Decimal uses it to apply rounding context)
        return Vec2(self.x, self.y)
    def __abs__(self):             # abs(v) -> magnitude (a number, NOT a Vec2)
        return math.hypot(self.x, self.y)
    def __invert__(self):          # ~v  -> swap components
        return Vec2(self.y, self.x)
    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

v = Vec2(3, 4)
print("\n# 15. Unary Operators")
print("-v      =", -v)
print("+v      =", +v, "(a copy:", (+v) is v, "is v)")
print("abs(v)  =", abs(v), "(3-4-5 triangle -> magnitude 5.0)")
print("~v      =", ~v, "(swapped - our own meaning for ~)")
try:
    -object()
except TypeError as e:
    print("-object() -> TypeError:", e)

# __round__, __trunc__ (and __floor__/__ceil__) - the numeric-function dunders:
# - round(x) calls x.__round__(); round(x, n) calls x.__round__(n).
#   Contract: with no ndigits return an int; with ndigits return the same kind of object.
# - math.trunc(x) calls __trunc__; math.floor/ceil call __floor__/__ceil__.
# - int(x) uses __int__ (don't rely on the old __trunc__ fallback; it is deprecated).
class Price:
    def __init__(self, amount):
        self.amount = amount
    def __round__(self, ndigits=None):
        if ndigits is None:
            return round(self.amount)                 # plain int, like round(2.567)
        return Price(round(self.amount, ndigits))     # same type back
    def __trunc__(self):
        return math.trunc(self.amount)
    def __repr__(self):
        return f"Price({self.amount})"

p = Price(2.567)
print("round(p)    =", round(p), "(int)")
print("round(p, 1) =", round(p, 1), "(still a Price)")
print("math.trunc(p) =", math.trunc(p), "(drops the fraction, no rounding)")

# 16. __ne__ for Free, and Returning NotImplemented (Not Raising, Not False)
# ------------------------------------
# - __ne__ (!=): Python 3 derives it from __eq__ automatically - it just inverts
#   the result. Write __eq__ only. (Python 2 needed both; old tutorials still show both.)
# - Binary dunders (__eq__, __add__, __lt__ ...) get TWO chances:
#     a + b  ->  a.__add__(b)  first; if that returns NotImplemented -> b.__radd__(a).
#     a == b ->  a.__eq__(b)   first; if NotImplemented -> b.__eq__(a) (the mirror).
#   If BOTH return NotImplemented: + raises TypeError, while == falls back to identity (a is b).
# - So when you don't understand `other`, return NotImplemented. Do NOT:
#     raise TypeError  -> kills the operation before the other side is even asked.
#     return False     -> claims "definitely not equal", so the other side never gets a vote.
# - Special case: if the right operand is a SUBCLASS of the left's type and overrides the
#   reflected method, the right operand's method is tried FIRST.
class Meters:
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        if isinstance(other, Meters):
            return self.value == other.value
        if isinstance(other, (int, float)):
            return self.value == other
        return NotImplemented              # "not my business" - let the other side try
    def __add__(self, other):
        if isinstance(other, (int, float)):
            return Meters(self.value + other)
        if isinstance(other, Meters):
            return Meters(self.value + other.value)
        return NotImplemented
    __radd__ = __add__                     # addition is commutative, so reuse it: 2 + Meters(1)
    def __repr__(self):
        return f"Meters({self.value})"

print("\n# 16. __ne__ and NotImplemented")
print("Meters(1) == Meters(1):", Meters(1) == Meters(1))
print("Meters(1) != Meters(2):", Meters(1) != Meters(2), "(no __ne__ written - derived from __eq__)")
print("Meters(1) != Meters(1):", Meters(1) != Meters(1))
print("Meters(5) == 5        :", Meters(5) == 5, "(mixed type handled)")
print("Meters(1) + 2         :", Meters(1) + 2)
print("2 + Meters(1)         :", 2 + Meters(1), "(int.__add__ gave up -> Meters.__radd__)")
print("Meters(1) == 'x'      :", Meters(1) == "x", "(both sides gave up -> identity fallback -> False)")
print("Meters(1) != 'x'      :", Meters(1) != "x", "(so != is True)")
try:
    Meters(1) + "x"
except TypeError as e:
    print("Meters(1) + 'x' -> TypeError:", e)
try:
    "x" + Meters(1)
except TypeError as e:
    print("'x' + Meters(1) -> TypeError:", e)

# Why NotImplemented beats raise/False: the reflected side may KNOW how to handle us.
class Centimeters:
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        if isinstance(other, Meters):
            return self.value == other.value * 100
        return NotImplemented
    def __radd__(self, other):
        if isinstance(other, Meters):
            return Centimeters(self.value + other.value * 100)
        return NotImplemented
    def __repr__(self):
        return f"Centimeters({self.value})"

class RudeMeters:                          # same idea as Meters but the WRONG way to say "no"
    def __init__(self, value):
        self.value = value
    def __eq__(self, other):
        if isinstance(other, RudeMeters):
            return self.value == other.value
        return False                       # wrong: other side never gets asked
    def __add__(self, other):
        if isinstance(other, RudeMeters):
            return RudeMeters(self.value + other.value)
        raise TypeError("RudeMeters can only add RudeMeters")   # wrong: blocks __radd__

print("\n# 16b. Polite (NotImplemented) vs Rude (False / raise)")
print("Meters(1) == Centimeters(100)     :", Meters(1) == Centimeters(100), "(Meters said NotImplemented -> Centimeters.__eq__ answered)")
print("RudeMeters(1) == Centimeters(100) :", RudeMeters(1) == Centimeters(100), "(Rude returned False - Centimeters was never asked)")
print("Meters(1) + Centimeters(50)       :", Meters(1) + Centimeters(50), "(reflected Centimeters.__radd__ rescued it)")
try:
    RudeMeters(1) + Centimeters(50)
except TypeError as e:
    print("RudeMeters(1) + Centimeters(50) -> TypeError:", e, "(raised early, __radd__ never tried)")

# 17. Truthiness - __bool__ vs __len__ Fallback Order
# ------------------------------------
# - `if obj:` / `not obj` / `bool(obj)` / `while obj:` all ask Python "is this truthy?".
# - Lookup order: 1) __bool__  2) __len__ (zero -> False)  3) neither -> always True.
# - __bool__ must return a real bool (not 0/1) or you get a TypeError.
# - __bool__ wins over __len__ when both exist.
class OnlyLen:
    def __init__(self, n): self.n = n
    def __len__(self): return self.n

class OnlyBool:
    def __init__(self, ok): self.ok = ok
    def __bool__(self): return self.ok

class Both:                                # __bool__ says True, __len__ says 0 - who wins?
    def __bool__(self): return True
    def __len__(self): return 0

class Neither:
    pass

class BadBool:
    def __bool__(self): return 1           # int, not bool

print("\n# 17. Truthiness - __bool__ vs __len__")
print("bool(OnlyLen(0))   :", bool(OnlyLen(0)), "(no __bool__ -> __len__() == 0 -> False)")
print("bool(OnlyLen(3))   :", bool(OnlyLen(3)))
print("bool(OnlyBool(False)):", bool(OnlyBool(False)), "(len() would not even work here)")
print("bool(Both())       :", bool(Both()), "(__bool__ wins, even though len(Both()) == 0)")
print("bool(Neither())    :", bool(Neither()), "(no hooks -> every instance is truthy)")
try:
    bool(BadBool())
except TypeError as e:
    print("bool(BadBool()) -> TypeError:", e)
print("# Gotcha: `if not items:` is True for None AND for [] - use `is None` to tell them apart.")

# 18. __format__ and Format Specs - f"{obj:spec}"
# ------------------------------------
# - f"{obj:spec}" and format(obj, "spec") call obj.__format__("spec").
# - Everything after the colon is passed to you as ONE string; YOU define its meaning.
#   Built-ins already do: f"{3.14159:.2f}", f"{42:>6}", f"{date:%Y-%m-%d}".
# - Default object.__format__ accepts ONLY an empty spec (and then returns str(obj)).
# - Conversion flags are separate and happen BEFORE __format__: {obj!r} -> repr, {obj!s} -> str.
import datetime

class Plain:
    def __str__(self):
        return "plain"

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius
    def __repr__(self):                    # for developers: unambiguous, ideally eval-able
        return f"Temperature({self.celsius})"
    def __str__(self):                     # for users: nice default text (used by print / f"{t}")
        return f"{self.celsius}C"
    def __format__(self, spec):            # for custom spec: f"{t:.1fF}", f"{t:K}" ...
        unit = spec[-1] if spec and spec[-1] in "CFK" else "C"
        number_spec = spec[:-1] if spec and spec[-1] in "CFK" else spec
        value = {"C": self.celsius,
                 "F": self.celsius * 9 / 5 + 32,
                 "K": self.celsius + 273.15}[unit]
        return f"{format(value, number_spec)}{unit}"   # delegate numbers to float's own spec

t = Temperature(36.6)
print("\n# 18. __format__ and Format Specs")
print("f'{t}'        :", f"{t}", "(empty spec -> our __format__ with '' -> 36.6C)")
print("f'{t:.0f}'    :", f"{t:.0f}")
print("f'{t:.1fF}'   :", f"{t:.1fF}")
print("f'{t:>10.2fK}':", f"[{t:>10.2fK}]")
print("format(t, 'F'):", format(t, "F"))
print("f'{t!r}'      :", f"{t!r}", "(!r -> __repr__, __format__ not called)")
print("f'{t!s:>8}'   :", f"[{t!s:>8}]", "(!s turns it into a str first, so the str width spec works)")
print("datetime built-in __format__:", f"{datetime.date(2024, 1, 5):%d %b %Y}")
try:
    f"{Plain():>10}"
except TypeError as e:
    print("f'{Plain():>10}' -> TypeError:", e)
# Tip: if you only want normal str-style alignment, a one-line __format__ does it:
#   def __format__(self, spec): return format(str(self), spec)

# __repr__ vs __str__ vs __format__ in one glance:
#   repr(x)  / {x!r} / REPL echo / inside containers -> __repr__   (for programmers; always define this one)
#   str(x)   / print(x) / {x!s}                      -> __str__    (for users; falls back to __repr__ if missing)
#   format(x, spec) / f"{x:spec}"                    -> __format__ (empty spec -> str(x); custom specs are yours)
print("print([t]) uses repr for items inside a list:", [t])

# 19. __hash__ Must Agree with __eq__ (Pointer Only)
# ------------------------------------
# - Full explanation lives in 04-Polymorphism.py (section 09). One-line rule:
#   if a == b then hash(a) == hash(b). Defining __eq__ alone sets __hash__ = None.
# - Same thing happens to the classes above (Meters has __eq__, so it is unhashable)
#   and to a plain @dataclass (eq=True, not frozen). frozen=True generates a __hash__.
print("\n# 19. __hash__ Pointer (see 04-Polymorphism.py)")
print("Meters.__hash__ is None:", Meters.__hash__ is None)
print("Point (plain dataclass) __hash__ is None:", Point.__hash__ is None)

# 20. Cheat Table - Operators -> Methods -> Reflected Versions
# ------------------------------------
#   Operator     Method (left operand)     Reflected (right operand)    In-place
#   ---------    ----------------------    -------------------------    ----------
#   a + b        __add__                   __radd__                     __iadd__
#   a - b        __sub__                   __rsub__                     __isub__
#   a * b        __mul__                   __rmul__                     __imul__
#   a / b        __truediv__               __rtruediv__                 __itruediv__
#   a // b       __floordiv__              __rfloordiv__                __ifloordiv__
#   a % b        __mod__                   __rmod__                     __imod__
#   a ** b       __pow__                   __rpow__                     __ipow__
#   a @ b        __matmul__                __rmatmul__                  __imatmul__
#   a == b       __eq__                    __eq__ (mirror)              -
#   a != b       __ne__ (derived from eq)  __ne__ (mirror)              -
#   a < b        __lt__                    __gt__  (mirror)             -
#   a <= b       __le__                    __ge__  (mirror)             -
#   a > b        __gt__                    __lt__  (mirror)             -
#   a >= b       __ge__                    __le__  (mirror)             -
#   -a / +a      __neg__ / __pos__         (unary - no reflection)
#   abs(a) ~a    __abs__ / __invert__      (unary - no reflection)
#   round(a)     __round__                 (also math.trunc/floor/ceil -> __trunc__/__floor__/__ceil__)
#   bool(a)      __bool__, else __len__, else always True
#   hash(a)      __hash__                  (must agree with __eq__)
#   str/repr/format -> __str__ / __repr__ / __format__
# - Comparisons have no "r" names: the right side's mirror method is used instead (a < b tries b > a).
# - Mixed-type rule of thumb: unknown `other` -> return NotImplemented.
print("\n# 20. Cheat table above (see comments) - operator -> method -> reflected version")
print("int.__lt__(1, 2.5):", (1).__lt__(2.5), "-> int gives up on float, Python then asks float.__gt__(2.5, 1)")
print("1 < 2.5:", 1 < 2.5, "| (1).__lt__('x'):", (1).__lt__("x"), "(NotImplemented, both give up -> 1 < 'x' is a TypeError)")
