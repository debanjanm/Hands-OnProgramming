from abc import ABC, abstractmethod

# 01. Abstraction - Introduction
# ------------------------------------
# - Abstraction hides implementation details and exposes only what's
#   necessary - a simplified interface for using an object.
# - Distinct from encapsulation (hiding data) - abstraction is about
#   hiding complexity of HOW something works, exposing only WHAT it does.

print("# 01. Abstraction - Introduction")
print("# ------------------------------------")

# 02. Real-World Analogy
# ------------------------------------
print("\n# 02. Real-World Analogy")
print("# - Driving a car: you use steering wheel/pedals (the interface).")
print("# - You don't need to know how the engine/transmission works internally.")

# 03. Abstraction via Regular Classes (informal)
# ------------------------------------
class Car:
    def start(self):
        self._ignite_engine()  # internal detail, hidden behind start()
        print("Car started")

    def _ignite_engine(self):
        print("(internal) igniting engine, checking fuel injection...")

print("\n# 03. Abstraction via Regular Classes")
car = Car()
car.start()  # simple interface - complexity hidden inside

# 04. The Problem: Nothing Forces Subclasses to Implement Anything
# ------------------------------------
class PaymentMethod:
    def pay(self, amount):
        pass  # subclasses SHOULD override this, but nothing enforces it

class BrokenPayment(PaymentMethod):
    pass  # forgot to implement pay() - no error until you call it and fail silently

print("\n# 04. The Problem Without Enforcement")
broken = BrokenPayment()
print("pay() returns:", broken.pay(100))  # silently does nothing - a real bug risk

# 05. Abstract Base Classes (ABC) - Enforcing an Interface
# ------------------------------------
# - ABC + @abstractmethod makes a class impossible to instantiate directly,
#   and forces subclasses to implement the marked methods.
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

    @abstractmethod
    def perimeter(self):
        pass

print("\n# 05. Abstract Base Classes (ABC)")
try:
    Shape()  # cannot instantiate an abstract class directly
except TypeError as e:
    print("Caught:", e)

# 06. Implementing an Abstract Class
# ------------------------------------
class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return 3.14159 * self.radius ** 2

    def perimeter(self):
        return 2 * 3.14159 * self.radius

print("\n# 06. Implementing an Abstract Class")
shapes = [Rectangle(4, 5), Circle(3)]
for shape in shapes:
    print(f"{shape.__class__.__name__}: area={shape.area():.2f}, perimeter={shape.perimeter():.2f}")

# 07. Forgetting to Implement an Abstract Method - Caught Immediately
# ------------------------------------
class IncompleteShape(Shape):
    def area(self):
        return 0
    # perimeter() not implemented

print("\n# 07. Forgetting to Implement an Abstract Method")
try:
    IncompleteShape()
except TypeError as e:
    print("Caught:", e)  # error at instantiation, not silently ignored

# 08. Abstract Classes Can Still Have Concrete (shared) Methods
# ------------------------------------
class Employee(ABC):
    def __init__(self, name):
        self.name = name

    @abstractmethod
    def calculate_pay(self):
        pass

    def describe(self):  # concrete method - shared by all subclasses
        return f"{self.name} earns {self.calculate_pay()}"

class SalariedEmployee(Employee):
    def calculate_pay(self):
        return 5000

print("\n# 08. Abstract Classes with Concrete Methods")
emp = SalariedEmployee("Debanjan")
print(emp.describe())

# 09. Abstraction vs Encapsulation (recap)
# ------------------------------------
print("\n# 09. Abstraction vs Encapsulation (recap)")
print("# - Encapsulation: hides DATA (private attributes, getters/setters).")
print("# - Abstraction:   hides IMPLEMENTATION (expose interface, hide 'how').")
print("# - See 02-Encapsulation.py for the encapsulation side.")

# 10. Virtual Subclass Registration (ABC.register())
# ------------------------------------
# - `SomeABC.register(SomeClass)` makes SomeClass "count as" a subclass of
#   SomeABC for isinstance()/issubclass() checks, WITHOUT actually inheriting
#   from it - no shared code, no MRO change, just a registered relationship.
# - Useful for retrofitting an interface onto a class you don't control (e.g.
#   a third-party class) or don't want to touch.
class Flyer(ABC):
    @abstractmethod
    def fly(self):
        pass

class Airplane: # does NOT inherit from Flyer at all
    def fly(self):
        return "Airplane flying"

Flyer.register(Airplane) # registers Airplane as a "virtual" subclass of Flyer

print("\n# 10. Virtual Subclass Registration (ABC.register())")
plane = Airplane()
print("isinstance(plane, Flyer):", isinstance(plane, Flyer)) # True, despite no inheritance
print("issubclass(Airplane, Flyer):", issubclass(Airplane, Flyer))
print("Flyer in Airplane.__mro__:", Flyer in Airplane.__mro__) # False - no real inheritance link

# 11. @abstractmethod Combined with @property (Abstract Property)
# ------------------------------------
# - Stacking @property above @abstractmethod forces subclasses to provide a
#   PROPERTY (not a regular method) with that name - enforces both "must
#   implement this" and "must expose it as an attribute, not a method call".
class Vehicle(ABC):
    @property
    @abstractmethod
    def max_speed(self):
        pass

class SportsCar(Vehicle):
    @property
    def max_speed(self): # must also be a property, not a plain method
        return 300

print("\n# 11. Abstract Property")
car = SportsCar()
print("car.max_speed (accessed like an attribute, no parentheses):", car.max_speed)
try:
    Vehicle() # still can't instantiate the abstract class itself
except TypeError as e:
    print("Caught:", e)

# 12. Protocol vs ABC - Structural vs Nominal Typing
# ------------------------------------
# - ABC (nominal typing): a class must explicitly inherit from the ABC (or be
#   registered) to "count" - the relationship is declared by name.
# - typing.Protocol (structural typing): ANY class with matching methods
#   automatically satisfies the protocol, no inheritance or registration
#   needed - "if it has the right shape, it counts" (duck typing, checkable
#   by type checkers). Full depth on typing lives in the standard library file.
from typing import Protocol

class Flappable(Protocol):
    def flap(self) -> str: ...

class Bird: # never inherits from Flappable, never registers - just has the method
    def flap(self):
        return "Bird flapping wings"

print("\n# 12. Protocol vs ABC (structural vs nominal typing)")
print("# - ABC: needs explicit inheritance/registration (nominal).")
print("# - Protocol: matching methods are enough, no inheritance needed (structural).")
bird = Bird()
print("isinstance(bird, Flappable) works only if Protocol is @runtime_checkable - see typing docs.")
print("bird.flap():", bird.flap())

# 13. Why You Can't Instantiate a Class with Missing Abstract Methods
# ------------------------------------
# - This is deliberate fail-fast design: the error happens the moment you try
#   to CREATE the incomplete object, not later when the missing method
#   happens to get called (which might be much later, in production).
# - Catching the mistake at instantiation is far cheaper than debugging a
#   silent no-op or an AttributeError deep inside unrelated code.
class Task(ABC):
    @abstractmethod
    def run(self):
        pass

class BrokenTask(Task):
    pass # never implements run() - and never will, as written

print("\n# 13. Fail-Fast: Can't Instantiate with Unimplemented Abstract Methods")
try:
    BrokenTask() # fails HERE, even though run() is never called
except TypeError as e:
    print("Caught immediately at instantiation, before run() would ever be called:", e)
