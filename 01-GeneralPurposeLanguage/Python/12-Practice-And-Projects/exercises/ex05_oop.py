"""Exercise set 05: object-oriented programming.

Replace each `raise NotImplementedError` with working code. Run the tests with:
    pytest tests/test_ex05_oop.py
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class Rectangle:
    """A Rectangle with width and height.
    area(), perimeter(), is_square(); repr like `Rectangle(3, 4)`;
    two rectangles are equal when width and height match (compare with other types -> False, no crash).

    Rectangle(3, 4).area() -> 12
    Rectangle(3, 4) == Rectangle(3, 4) -> True
    Rectangle(2, 2).is_square() -> True
    Rectangle(1, 1) == 5 -> False

    Level: easy
    Hint: Return NotImplemented from __eq__ when `other` is not a Rectangle.
    """
    def __init__(self, width, height): raise NotImplementedError
    def area(self): raise NotImplementedError
    def perimeter(self): raise NotImplementedError
    def is_square(self): raise NotImplementedError
    def __repr__(self): raise NotImplementedError
    def __eq__(self, other): raise NotImplementedError


class Temperature:
    """Store a temperature. `celsius` is a property: setting a value below -273.15
    raises ValueError (also in the constructor). `fahrenheit` is a computed property
    that can be read AND set.

    t = Temperature(100); t.fahrenheit -> 212.0
    t.fahrenheit = 32; t.celsius -> 0.0
    Temperature(-300) -> ValueError

    Level: easy
    Hint: Store in `self._celsius`; call the setter from __init__ via `self.celsius = ...`.
    """
    def __init__(self, celsius=0): raise NotImplementedError
    @property
    def celsius(self): raise NotImplementedError
    @celsius.setter
    def celsius(self, value): raise NotImplementedError
    @property
    def fahrenheit(self): raise NotImplementedError
    @fahrenheit.setter
    def fahrenheit(self, value): raise NotImplementedError


class Vector:
    """A 2D vector with operator overloading: v+w, v-w, v*number, number*v, -v,
    abs(v) (length), ==, bool(v) (False only for the zero vector), repr `Vector(1, 2)`.
    Adding a non-Vector must raise TypeError (return NotImplemented).

    Vector(1, 2) + Vector(3, 4) -> Vector(4, 6)
    2 * Vector(1, 2) -> Vector(2, 4)
    abs(Vector(3, 4)) -> 5.0
    bool(Vector(0, 0)) -> False

    Level: medium
    Hint: Binary dunders get (self, other). Define __rmul__ for `2 * v`.
    """
    def __init__(self, x, y): raise NotImplementedError
    def __add__(self, other): raise NotImplementedError
    def __sub__(self, other): raise NotImplementedError
    def __mul__(self, k): raise NotImplementedError
    def __rmul__(self, k): raise NotImplementedError
    def __neg__(self): raise NotImplementedError
    def __abs__(self): raise NotImplementedError
    def __eq__(self, other): raise NotImplementedError
    def __bool__(self): raise NotImplementedError
    def __repr__(self): raise NotImplementedError


class BankAccount:
    """A bank account. Class attributes: bank_name = "PyBank" and `count` (number of
    accounts created). deposit/withdraw return the new balance and raise ValueError for
    non-positive amounts; withdraw also raises ValueError if funds are too low.
    classmethod from_string("Asha:100") builds an account; staticmethod
    is_valid_amount(x) is True for numbers > 0.

    a = BankAccount("Asha", 50); a.deposit(25) -> 75
    BankAccount.from_string("Ravi: 10").balance -> 10.0
    BankAccount.is_valid_amount(-5) -> False

    Level: easy
    Hint: Count with `BankAccount.count += 1` in __init__ (the class, not self).
    """
    bank_name = "PyBank"
    count = 0
    def __init__(self, owner, balance=0): raise NotImplementedError
    def deposit(self, amount): raise NotImplementedError
    def withdraw(self, amount): raise NotImplementedError
    @classmethod
    def from_string(cls, text): raise NotImplementedError
    @staticmethod
    def is_valid_amount(amount): raise NotImplementedError


class Employee:
    """Employee(name, salary): monthly_pay() = salary / 12; describe() -> "Asha (Employee)"
    (use the real class name). Manager extends Employee with a list `reports`
    (not shared between managers), add_report(emp), and monthly_pay() = normal pay
    plus 100 per report. Use super().

    Employee("Asha", 1200).monthly_pay() -> 100.0
    m = Manager("Ravi", 1200); m.add_report(e); m.monthly_pay() -> 200.0
    m.describe() -> "Ravi (Manager)"

    Level: medium
    Hint: Call super().__init__(...) and super().monthly_pay(). Use type(self).__name__.
    """
    def __init__(self, name, salary): raise NotImplementedError
    def monthly_pay(self): raise NotImplementedError
    def describe(self): raise NotImplementedError

class Manager(Employee):
    def __init__(self, name, salary, reports=None): raise NotImplementedError
    def add_report(self, employee): raise NotImplementedError
    def monthly_pay(self): raise NotImplementedError


class Shape(ABC):
    """Shape is an abstract base class with abstract area() and a normal method
    describe() -> "Circle with area 3.14" (2 decimals). Shape() and subclasses
    that forget area() cannot be created (TypeError). Circle(radius) and Square(side)
    implement area(). total_area(shapes) adds them up (use math.pi).

    Circle(1).describe() -> "Circle with area 3.14"
    Square(2).area() -> 4
    total_area([Square(2), Square(3)]) -> 13
    Shape() -> TypeError

    Level: medium
    Hint: Subclass ABC and decorate area with @abstractmethod. `import math` at the top.
    """
    def __init__(self): raise NotImplementedError
    def area(self): raise NotImplementedError
    def describe(self): raise NotImplementedError

class Circle(Shape):
    def __init__(self, radius): raise NotImplementedError
    def area(self): raise NotImplementedError

class Square(Shape):
    def __init__(self, side): raise NotImplementedError
    def area(self): raise NotImplementedError

def total_area(shapes): raise NotImplementedError


class Item:
    """Write two dataclasses (the stub is a plain class; turn it into a real
    @dataclass with fields and remove the __init__ stub).
    Item(price, name, qty=1): frozen (cannot change after creation), sortable by
    (price, name, qty), property `total` = price * qty.
    Cart(items=[]): items defaults to a NEW empty list each time; add(item); total().

    Item(2.5, "pen", 4).total -> 10.0
    Item(1, "a") < Item(2, "a") -> True
    Cart().items is Cart().items -> False
    item.qty = 3 -> FrozenInstanceError

    Level: medium
    Hint: Use field(default_factory=list) for the list. @dataclass(frozen=True, order=True) for Item.
    """
    def __init__(self, *args, **kwargs): raise NotImplementedError
    @property
    def total(self): raise NotImplementedError

class Cart:
    def __init__(self, *args, **kwargs): raise NotImplementedError
    def add(self, item): raise NotImplementedError
    def total(self): raise NotImplementedError


class Playlist:
    """A container of songs. Playlist("a", "b") ; add(song); len(p); p[0], p[-1],
    p[0:2] (slice gives a plain list); `for s in p`; `"a" in p`; repr `Playlist('a', 'b')`.
    reversed(p) and list(p) should work too.

    p = Playlist("a", "b"); len(p) -> 2; p[-1] -> "b"
    list(reversed(p)) -> ["b", "a"]

    Level: medium
    Hint: Delegate to a private list. __len__ + __getitem__ also make reversed() work.
    """
    def __init__(self, *songs): raise NotImplementedError
    def add(self, song): raise NotImplementedError
    def __len__(self): raise NotImplementedError
    def __getitem__(self, index): raise NotImplementedError
    def __iter__(self): raise NotImplementedError
    def __contains__(self, song): raise NotImplementedError
    def __repr__(self): raise NotImplementedError


class Countdown:
    """An iterator that counts down from `start` to 1, then stops.
    It is used up after one pass (a second loop over the same object gives nothing).

    list(Countdown(3)) -> [3, 2, 1]
    list(Countdown(0)) -> []
    c = Countdown(2); list(c); list(c) -> []

    Level: medium
    Hint: __iter__ returns self; __next__ raises StopIteration at the end.
    """
    def __init__(self, start): raise NotImplementedError
    def __iter__(self): raise NotImplementedError
    def __next__(self): raise NotImplementedError


class Engine:
    """Composition. Engine(horsepower) has `running` (False at first); start() sets it
    True and returns True if it was off, False if already on; stop() turns it off.
    Car(model, engine) HAS an engine (any object with start/stop/running works):
    start() -> "Mini started" or "Mini already running"; stop(); property is_running.

    car = Car("Mini", Engine(90)); car.start() -> "Mini started"
    car.start() -> "Mini already running"
    car.is_running -> True

    Level: medium
    Hint: Car keeps `self.engine` and delegates to it. Do not subclass Engine.
    """
    def __init__(self, horsepower): raise NotImplementedError
    def start(self): raise NotImplementedError
    def stop(self): raise NotImplementedError

class Car:
    def __init__(self, model, engine): raise NotImplementedError
    def start(self): raise NotImplementedError
    def stop(self): raise NotImplementedError
    @property
    def is_running(self): raise NotImplementedError


def no_discount(subtotal):
    """Strategy helper: return the subtotal unchanged.

    no_discount(100) -> 100

    Level: medium
    Hint: One line.
    """
    raise NotImplementedError


def percent_off(percent):
    """Strategy factory: return a function that takes off `percent` percent.

    percent_off(10)(200) -> 180.0

    Level: medium
    Hint: Return an inner function.
    """
    raise NotImplementedError


def flat_off(amount):
    """Strategy factory: return a function that subtracts `amount` but never
    goes below 0.

    flat_off(50)(200) -> 150
    flat_off(50)(30) -> 0

    Level: medium
    Hint: max(0, ...)
    """
    raise NotImplementedError


class Checkout:
    """Strategy pattern. (Do the three helpers above first.) Checkout(prices,
    strategy=no_discount); total() applies the current strategy to sum(prices);
    set_strategy(f) swaps it later.

    c = Checkout([100, 100]); c.total() -> 200
    c.set_strategy(percent_off(50)); c.total() -> 100.0

    Level: medium
    Hint: total() = self.strategy(sum(self.prices)).
    """
    def __init__(self, prices, strategy=no_discount): raise NotImplementedError
    def set_strategy(self, strategy): raise NotImplementedError
    def total(self): raise NotImplementedError


class EventEmitter:
    """Observer pattern. on(event, callback) registers (and returns the callback); off(event, callback) removes it (unknown -> ignore);
    emit(event, *args, **kwargs) calls every callback for that event in the order
    registered and returns how many were called (0 for an unknown event).
    A callback may remove itself during emit without breaking the loop.

    e = EventEmitter(); e.on("hi", print); e.emit("hi", "x") -> prints x, returns 1
    e.emit("nothing") -> 0

    Level: hard
    Hint: Keep {event: [callbacks]}. Loop over a copy of the list.
    """
    def __init__(self): raise NotImplementedError
    def on(self, event, callback): raise NotImplementedError
    def off(self, event, callback): raise NotImplementedError
    def emit(self, event, *args, **kwargs): raise NotImplementedError
