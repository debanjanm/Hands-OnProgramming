# 01. Polymorphism - Introduction
# ------------------------------------
# - "Poly" (many) + "morph" (forms) - the same operation/method name behaves
#   differently depending on the object it's called on.
# - Lets you write code that works with objects of different types uniformly.

print("# 01. Polymorphism - Introduction")
print("# ------------------------------------")

# 02. Built-in Polymorphism (recap)
# ------------------------------------
# - len() and + already behave differently depending on the type.
print("\n# 02. Built-in Polymorphism (recap)")
print("len('hello'):", len("hello"))
print("len([1, 2, 3]):", len([1, 2, 3]))
print("'a' + 'b':", "a" + "b")
print("[1] + [2]:", [1] + [2])

# 03. Polymorphism via Method Overriding (inheritance)
# ------------------------------------
class Animal:
    def speak(self):
        return "Some generic animal sound"

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

print("\n# 03. Polymorphism via Method Overriding")
animals = [Animal(), Dog(), Cat()]
for animal in animals:
    print(f"{animal.__class__.__name__}: {animal.speak()}")
# - Same method call `animal.speak()`, different behavior per actual type.

# 04. Duck Typing - "If it walks like a duck..."
# ------------------------------------
# - Python doesn't require a common base class for polymorphism.
# - Any object with the expected method/attribute works - type isn't checked.
class Duck:
    def speak(self):
        return "Quack!"

class Robot:
    def speak(self):
        return "Beep boop, I am speaking"

print("\n# 04. Duck Typing")
for thing in [Duck(), Robot()]:
    print(thing.speak())  # works for both - neither inherits from Animal

# 05. Polymorphism with Functions
# ------------------------------------
def make_it_speak(entity):
    # works with ANY object that has a .speak() method
    print(entity.speak())

print("\n# 05. Polymorphism with Functions")
make_it_speak(Dog())
make_it_speak(Duck())

# 06. Operator Overloading is Polymorphism Too (recap)
# ------------------------------------
# - See 06-Dataclasses-And-Operator-Overloading.py for __add__, __eq__, etc.
print("\n# 06. Operator Overloading is Polymorphism Too")
print("# - Custom __add__/__eq__/__lt__ let + / == / < 'do the right thing'")
print("#   for objects of a custom class, just like built-ins do for str/list.")

# 07. Polymorphism with Abstract Base Classes (preview)
# ------------------------------------
# - Covered fully in 05-Abstraction.py - ABCs force subclasses to implement
#   a shared method, guaranteeing polymorphism works consistently.
print("\n# 07. Polymorphism with Abstract Base Classes (preview)")
print("# - See 05-Abstraction.py for enforcing a common interface with ABC.")

# 08. Why Polymorphism Matters
# ------------------------------------
print("\n# 08. Why Polymorphism Matters")
print("# - Write one function/loop that works with many types.")
print("# - Add new types later (e.g. a Bird class) without changing existing code.")

# 09. __eq__ and __hash__ Relationship
# ------------------------------------
# - By default, objects are hashable using their id() and compared with ==
#   by identity too - that's how they end up in sets/dict keys "for free".
# - Overriding __eq__ to compare by VALUE makes Python set __hash__ to None
#   automatically - the object becomes unhashable, since equal-by-value
#   objects would need equal hashes, and the default id()-based hash can't
#   guarantee that anymore.
class PointNoHash:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    # no __hash__ defined -> Python sets it to None automatically

print("\n# 09. __eq__ and __hash__ Relationship")
p1 = PointNoHash(1, 2)
print("p1 == PointNoHash(1, 2):", p1 == PointNoHash(1, 2))
try:
    {p1} # attempting to put it in a set requires __hash__
except TypeError as e:
    print("Caught (unhashable):", e)

class PointHashable(PointNoHash):
    def __hash__(self):
        return hash((self.x, self.y)) # must be consistent with __eq__

print("With __hash__ defined, {PointHashable(1, 2)} works:", {PointHashable(1, 2)})

# 10. Full Comparison Dunders + functools.total_ordering
# ------------------------------------
# - __lt__, __le__, __gt__, __ge__ each back one comparison operator.
# - Writing all four (plus __eq__) is repetitive - @functools.total_ordering
#   fills in the rest as long as you define __eq__ and just ONE of the others.
from functools import total_ordering

@total_ordering
class Money:
    def __init__(self, amount):
        self.amount = amount
    def __eq__(self, other):
        return self.amount == other.amount
    def __lt__(self, other):
        return self.amount < other.amount
    # __le__, __gt__, __ge__ are derived automatically from __eq__ and __lt__

print("\n# 10. functools.total_ordering")
m1, m2 = Money(100), Money(200)
print("m1 < m2:", m1 < m2)
print("m1 <= m2 (derived):", m1 <= m2)
print("m1 > m2 (derived):", m1 > m2)
print("m1 >= m2 (derived):", m1 >= m2)

# 11. Polymorphism via __call__ (Callable Instances)
# ------------------------------------
# - Defining __call__ lets instances be invoked like functions: obj(...).
# - It's polymorphism because the SAME syntax (calling with parentheses)
#   works uniformly whether the callee is a function, a lambda, or an object.
class Multiplier:
    def __init__(self, factor):
        self.factor = factor
    def __call__(self, value):
        return value * self.factor

print("\n# 11. Polymorphism via __call__")
double = Multiplier(2)
triple = Multiplier(3)
print("double(5):", double(5))   # called just like a function
print("triple(5):", triple(5))
print("callable(double):", callable(double))

# 12. Single Dispatch Generic Functions (functools.singledispatch)
# ------------------------------------
# - singledispatch lets one function have different implementations chosen
#   by the TYPE of its first argument - polymorphism resolved by argument
#   type rather than by which object's method is called.
from functools import singledispatch

@singledispatch
def describe(value):
    return f"a value: {value}"

@describe.register
def _(value: int):
    return f"an integer: {value}"

@describe.register
def _(value: list):
    return f"a list with {len(value)} items"

print("\n# 12. functools.singledispatch")
print("describe(3.14):", describe(3.14))   # falls back to the generic implementation
print("describe(5):", describe(5))         # dispatches to the int implementation
print("describe([1, 2, 3]):", describe([1, 2, 3])) # dispatches to the list implementation
