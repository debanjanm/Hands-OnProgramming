"""Exercise set 05: object-oriented programming.

Replace each `raise NotImplementedError` with working code. Run the tests with:
    pytest tests/test_ex05_oop.py
"""

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field


class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)

    def is_square(self):
        return self.width == self.height

    def __repr__(self):
        # repr should look like the code that builds the object
        return f"Rectangle({self.width}, {self.height})"

    def __eq__(self, other):
        if not isinstance(other, Rectangle):
            return NotImplemented  # lets Python try the other side / fall back to False
        return (self.width, self.height) == (other.width, other.height)


class Temperature:
    MIN_C = -273.15

    def __init__(self, celsius=0):
        self.celsius = celsius  # goes through the setter, so it is validated too

    @property
    def celsius(self):
        return self._celsius

    @celsius.setter
    def celsius(self, value):
        if value < self.MIN_C:
            raise ValueError("below absolute zero")
        self._celsius = value

    @property
    def fahrenheit(self):
        return self._celsius * 9 / 5 + 32

    @fahrenheit.setter
    def fahrenheit(self, value):
        self.celsius = (value - 32) * 5 / 9  # reuse the celsius validation


class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, k):
        if not isinstance(k, (int, float)):
            return NotImplemented
        return Vector(self.x * k, self.y * k)

    __rmul__ = __mul__  # 3 * v works like v * 3

    def __neg__(self):
        return Vector(-self.x, -self.y)

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __bool__(self):
        return bool(self.x or self.y)

    def __repr__(self):
        return f"Vector({self.x}, {self.y})"


class BankAccount:
    bank_name = "PyBank"   # class attribute: shared by all accounts
    count = 0

    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance
        BankAccount.count += 1

    def deposit(self, amount):
        if not self.is_valid_amount(amount):
            raise ValueError("amount must be positive")
        self.balance += amount
        return self.balance

    def withdraw(self, amount):
        if not self.is_valid_amount(amount):
            raise ValueError("amount must be positive")
        if amount > self.balance:
            raise ValueError("insufficient funds")
        self.balance -= amount
        return self.balance

    @classmethod
    def from_string(cls, text):
        owner, balance = text.split(":")
        return cls(owner.strip(), float(balance))  # classmethod = alternative constructor

    @staticmethod
    def is_valid_amount(amount):
        return isinstance(amount, (int, float)) and amount > 0


class Employee:
    def __init__(self, name, salary):
        self.name = name
        self.salary = salary

    def monthly_pay(self):
        return self.salary / 12

    def describe(self):
        return f"{self.name} ({type(self).__name__})"  # type(self) gives the real subclass


class Manager(Employee):
    BONUS_PER_REPORT = 100

    def __init__(self, name, salary, reports=None):
        super().__init__(name, salary)  # reuse the parent setup
        self.reports = list(reports or [])

    def add_report(self, employee):
        self.reports.append(employee)

    def monthly_pay(self):
        return super().monthly_pay() + self.BONUS_PER_REPORT * len(self.reports)


class Shape(ABC):
    @abstractmethod
    def area(self):
        """Every shape must say how to compute its area."""

    def describe(self):
        return f"{type(self).__name__} with area {self.area():.2f}"  # shared behaviour


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def area(self):
        return math.pi * self.radius ** 2


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2


def total_area(shapes):
    return sum(s.area() for s in shapes)


@dataclass(frozen=True, order=True)
class Item:
    price: float          # first field => ordering compares price first
    name: str
    qty: int = 1

    @property
    def total(self):
        return self.price * self.qty


@dataclass
class Cart:
    items: list = field(default_factory=list)  # a fresh list per Cart

    def add(self, item):
        self.items.append(item)

    def total(self):
        return sum(i.total for i in self.items)


class Playlist:
    def __init__(self, *songs):
        self._songs = list(songs)

    def add(self, song):
        self._songs.append(song)

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, index):
        return self._songs[index]  # ints and slices both just work

    def __iter__(self):
        return iter(self._songs)

    def __contains__(self, song):
        return song in self._songs

    def __repr__(self):
        return f"Playlist({', '.join(map(repr, self._songs))})"


class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self  # an iterator returns itself

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Engine:
    def __init__(self, horsepower):
        self.horsepower = horsepower
        self.running = False

    def start(self):
        started = not self.running
        self.running = True
        return started

    def stop(self):
        self.running = False


class Car:
    def __init__(self, model, engine):
        self.model = model
        self.engine = engine  # "has-an" engine: composition, not inheritance

    def start(self):
        return f"{self.model} started" if self.engine.start() else f"{self.model} already running"

    def stop(self):
        self.engine.stop()

    @property
    def is_running(self):
        return self.engine.running


def no_discount(subtotal):
    # a strategy is just a function: price in, price out
    return subtotal


def percent_off(percent):
    # factory returns a strategy
    return lambda subtotal: subtotal * (100 - percent) / 100


def flat_off(amount):
    # never negative
    return lambda subtotal: max(0, subtotal - amount)


class Checkout:
    def __init__(self, prices, strategy=no_discount):
        self.prices = list(prices)
        self.strategy = strategy

    def set_strategy(self, strategy):
        self.strategy = strategy

    def total(self):
        return self.strategy(sum(self.prices))  # swap behaviour without changing this class


class EventEmitter:
    def __init__(self):
        self._handlers = {}

    def on(self, event, callback):
        self._handlers.setdefault(event, []).append(callback)
        return callback  # handy for chaining or later off()

    def off(self, event, callback):
        handlers = self._handlers.get(event, [])
        if callback in handlers:
            handlers.remove(callback)

    def emit(self, event, *args, **kwargs):
        callbacks = list(self._handlers.get(event, []))
        for callback in callbacks:  # handlers may change subscriptions
            callback(*args, **kwargs)
        return len(callbacks)
