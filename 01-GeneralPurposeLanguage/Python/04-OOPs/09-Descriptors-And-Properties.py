import weakref

# 01. What Is a Descriptor?
# ------------------------------------
# - A descriptor is an object, stored as a CLASS attribute, that defines any of
#   __get__, __set__, __delete__. Python calls those methods when the attribute is
#   read, assigned or deleted on an instance.
# - It is the machinery behind property, classmethod, staticmethod, and even
#   ordinary methods. (Plain @property basics: see 02-Encapsulation.py.)
# - Signatures:
#     __get__(self, obj, objtype=None)   obj is None when accessed on the class itself
#     __set__(self, obj, value)
#     __delete__(self, obj)
#     __set_name__(self, owner, name)    called once at class creation (Python 3.6+)
class Loud:
    def __get__(self, obj, objtype=None):
        print(f"      -> __get__(obj={type(obj).__name__ if obj is not None else None}, objtype={objtype.__name__})")
        return 42

class Demo01:
    x = Loud()          # descriptor lives on the CLASS

d = Demo01()
print("d.x (access through an instance):")
print("   result:", d.x)
print("Demo01.x (access through the class, obj is None):")
print("   result:", Demo01.x)

# 02. Data vs Non-Data Descriptors
# ------------------------------------
# - DATA descriptor     = defines __set__ and/or __delete__ (usually with __get__ too).
# - NON-DATA descriptor = defines ONLY __get__ (functions/methods are the classic case).
# - Why it matters: the type decides who wins when the instance __dict__ also has
#   the same name (next section).
class NonData:
    def __get__(self, obj, objtype=None):
        return "from non-data descriptor"

class Data:
    def __get__(self, obj, objtype=None):
        return "from data descriptor"
    def __set__(self, obj, value):
        print("      -> __set__ intercepted", value)

def kind(desc):
    t = type(desc)
    return "data" if hasattr(t, "__set__") or hasattr(t, "__delete__") else "non-data"

print("NonData is:", kind(NonData()))
print("Data is   :", kind(Data()))
print("function is:", kind(lambda: 0), "| property is:", kind(property()))

# 03. Attribute Lookup Order (Why Data Descriptors Win)
# ------------------------------------
# - For obj.name Python (object.__getattribute__) does, in order:
#     1. Look up `name` on type(obj) through the MRO.
#     2. If found AND it is a DATA descriptor  -> call its __get__. Stop.
#     3. Else, if `name` is in obj.__dict__    -> return that.
#     4. Else, if step 1 found a non-data descriptor -> call its __get__.
#     5. Else, if step 1 found a plain class attribute -> return it.
#     6. Else raise AttributeError (after trying __getattr__ if defined, see 10).
# - So: data descriptor > instance dict > non-data descriptor > plain class attribute.
class Mixed:
    nd = NonData()
    dd = Data()

m = Mixed()
m.__dict__["nd"] = "instance value for nd"
m.__dict__["dd"] = "instance value for dd"     # sneaks into the dict, bypassing __set__
print("m.nd (instance dict beats non-data):", m.nd)
print("m.dd (data descriptor beats instance dict):", m.dd)
m.dd = 99                                        # assignment is routed to __set__
print("m.__dict__ now:", m.__dict__)

# 04. Functions Are Descriptors: How Methods Get Bound
# ------------------------------------
# - Every def inside a class makes a function object. Functions have __get__, so
#   they are NON-data descriptors.
# - obj.method -> function.__get__(obj, type(obj)) -> a BOUND method holding obj.
# - That is the whole secret behind `self`. (Basics: 01-Class-Object.py)
class Dog:
    def speak(self):
        return "woof"

dog = Dog()
print("Dog.speak (via class)   :", type(Dog.speak).__name__)
print("dog.speak (via instance):", type(dog.speak).__name__)
print("bound method __self__ is dog:", dog.speak.__self__ is dog)
manual = Dog.__dict__["speak"].__get__(dog, Dog)
print("manual __get__ call works:", manual(), "| equal to dog.speak:", manual == dog.speak)
print("Dog.speak(dog) is the same call written out:", Dog.speak(dog))

# 05. classmethod and staticmethod Are Descriptors Too
# ------------------------------------
# - classmethod.__get__ binds the CLASS (not the instance) as the first argument.
# - staticmethod.__get__ returns the raw function with nothing bound.
# - Below are tiny pure-Python re-creations of both.
class MyClassMethod:
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        if objtype is None:
            objtype = type(obj)
        return lambda *a, **k: self.func(objtype, *a, **k)

class MyStaticMethod:
    def __init__(self, func):
        self.func = func
    def __get__(self, obj, objtype=None):
        return self.func

class Tool:
    @MyClassMethod
    def who(cls):
        return f"classmethod got {cls.__name__}"
    @MyStaticMethod
    def add(a, b):
        return a + b
    @classmethod
    def real_who(cls):
        return f"builtin classmethod got {cls.__name__}"

print(Tool.who(), "|", Tool().who())
print("static add:", Tool.add(2, 3), "|", Tool().add(4, 5))
print(Tool.real_who())

# 06. property Is a Data Descriptor (And We Can Prove It)
# ------------------------------------
# - property defines __get__, __set__ and __delete__ - so it is a data descriptor.
# - Even a read-only property (no setter) still defines __set__; it just raises
#   AttributeError. That is why you cannot shadow it via the instance.
class Circle:
    def __init__(self, r):
        self._r = r
    @property
    def radius(self):
        return self._r
    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius must be >= 0")
        self._r = value
    @property
    def diameter(self):          # read-only
        return self._r * 2

c = Circle(2)
print("type of Circle.radius:", type(Circle.radius).__name__)
print("has __set__ / __delete__:", hasattr(property, "__set__"), hasattr(property, "__delete__"))
print("fget / fset / fdel on radius:", Circle.radius.fget.__name__, Circle.radius.fset.__name__, Circle.radius.fdel)
c.radius = 5
print("radius:", c.radius, "| diameter:", c.diameter)
for label, action in [("negative radius", lambda: setattr(c, "radius", -1)),
                      ("assign read-only diameter", lambda: setattr(c, "diameter", 1))]:
    try:
        action()
    except (ValueError, AttributeError) as e:
        print(f"{label}: {type(e).__name__}: {e}")

# 07. Build Your Own property
# ------------------------------------
# - A simplified property in ~20 lines. Note the decorator chain: each .setter
#   returns a NEW descriptor copy that keeps the old getter.
class MyProperty:
    def __init__(self, fget=None, fset=None, fdel=None):
        self.fget, self.fset, self.fdel = fget, fset, fdel
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self                      # access via class returns the descriptor
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)
    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)
    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)
    def setter(self, fset):
        return MyProperty(self.fget, fset, self.fdel)
    def deleter(self, fdel):
        return MyProperty(self.fget, self.fset, fdel)

class Temperature:
    def __init__(self):
        self._c = 0
    @MyProperty
    def celsius(self):
        return self._c
    @celsius.setter
    def celsius(self, v):
        print("      -> setter called")
        self._c = v
    @MyProperty
    def fahrenheit(self):
        return self._c * 9 / 5 + 32

t = Temperature()
t.celsius = 100
print("celsius:", t.celsius, "| fahrenheit:", t.fahrenheit)
try:
    t.fahrenheit = 1
except AttributeError as e:
    print("read-only fahrenheit:", e)

# 08. A Reusable Validated-Field Descriptor
# ------------------------------------
# - One property per attribute means copy-paste. A descriptor writes the rule ONCE
#   and reuses it for every field - the big practical win of descriptors.
# - __set_name__ tells the descriptor which attribute name it was assigned to, so
#   it can store the value in the instance __dict__ under a private key.
class Typed:
    def __init__(self, expected_type):
        self.expected_type = expected_type
    def __set_name__(self, owner, name):
        print(f"      -> __set_name__(owner={owner.__name__}, name={name!r})")
        self.public = name
        self.private = "_" + name
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private)
    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(f"{self.public} must be {self.expected_type.__name__}, got {type(value).__name__}")
        setattr(obj, self.private, value)

class PositiveNumber:
    def __set_name__(self, owner, name):
        self.public, self.private = name, "_" + name
    def __get__(self, obj, objtype=None):
        return self if obj is None else getattr(obj, self.private)
    def __set__(self, obj, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise TypeError(f"{self.public} must be a number")
        if value <= 0:
            raise ValueError(f"{self.public} must be positive, got {value}")
        setattr(obj, self.private, value)

print("Creating class Product (watch __set_name__ fire at class-creation time):")
class Product:
    name = Typed(str)
    price = PositiveNumber()
    qty = PositiveNumber()
    def __init__(self, name, price, qty):
        self.name, self.price, self.qty = name, price, qty

p = Product("pen", 2.5, 10)
print("valid:", p.name, p.price, p.qty)
for args in [(123, 1, 1), ("pen", -1, 1), ("pen", 1, "many")]:
    try:
        Product(*args)
    except (TypeError, ValueError) as e:
        print(f"Product{args} -> {type(e).__name__}: {e}")
print("stored under private keys:", sorted(p.__dict__))

# 09. Gotcha: Descriptor State Is Shared Across Instances
# ------------------------------------
# - The descriptor object exists ONCE per class, not once per instance.
# - Storing the value on the descriptor itself (self.value = ...) makes every
#   instance share it - a classic bug.
class BadField:
    def __get__(self, obj, objtype=None):
        return self if obj is None else self.value
    def __set__(self, obj, value):
        self.value = value                  # BUG: stored on the shared descriptor

class Shared:
    n = BadField()

a, b = Shared(), Shared()
a.n = 1
b.n = 2
print("a.n after setting b.n (should be 1):", a.n)

# 10. Storage Choices: instance __dict__ vs WeakKeyDictionary
# ------------------------------------
# - Correct per-instance storage options:
#     (a) instance __dict__ under a private/own key (section 8) - simple, best default
#     (b) a dict inside the descriptor keyed by the instance - fails (see below)
#     (c) a WeakKeyDictionary keyed by the instance - works, but has requirements
# - Gotcha 1: a plain dict {obj: value} keeps every instance ALIVE forever (memory leak)
#   and needs obj to be hashable.
# - Gotcha 2: WeakKeyDictionary needs the instance to be hashable AND weak-referenceable.
#   Classes with __slots__ and no '__weakref__' slot cannot be weak-referenced; classes
#   defining __eq__ without __hash__ are unhashable.
class WeakField:
    def __init__(self):
        self.data = weakref.WeakKeyDictionary()
    def __get__(self, obj, objtype=None):
        return self if obj is None else self.data.get(obj)
    def __set__(self, obj, value):
        self.data[obj] = value

class Normal:
    w = WeakField()

n1, n2 = Normal(), Normal()
n1.w, n2.w = "one", "two"
print("per-instance values:", n1.w, n2.w, "| entries:", len(Normal.w.data))
del n2
import gc; gc.collect()
print("after deleting n2, entries left (entry vanished with the object):", len(Normal.w.data))

class Slotted:
    __slots__ = ("x",)                      # no __weakref__ slot
    w = WeakField()

try:
    Slotted().w = 1
except TypeError as e:
    print("__slots__ without __weakref__:", e)

class Unhashable:
    w = WeakField()
    def __eq__(self, other):
        return True                         # defining __eq__ alone sets __hash__ = None

try:
    Unhashable().w = 1
except TypeError as e:
    print("unhashable instance:", e)

# 11. Gotcha: Descriptors Only Work as CLASS Attributes
# ------------------------------------
# - Python looks for descriptors on type(obj), never inside obj.__dict__.
# - A descriptor placed on an instance, or assigned after the fact to a different
#   object, is just an ordinary value - __get__/__set__ never fire.
class Holder:
    pass

h = Holder()
h.x = Loud()
print("descriptor stored on the instance is NOT called:", type(h.x).__name__)
Holder.y = Loud()                           # adding to the CLASS later does work
print("added to the class afterwards:", h.y)

# 12. Descriptor Called on the Class: obj Is None
# ------------------------------------
# - Always handle obj is None in __get__. Convention: return self, so that
#   Class.attr gives back the descriptor (that is how help() and docs find it).
# - Gotcha: class-level ASSIGNMENT (Class.attr = 5) does NOT call __set__; it
#   simply replaces the descriptor. __set__ is for instances only (a metaclass
#   descriptor would be needed otherwise, see 11-Metaclasses-And-Class-Creation.py).
class Always7:
    def __get__(self, obj, objtype=None):
        return 7
    def __set__(self, obj, value):
        raise AttributeError("read-only")

class UsesIt:
    v = Always7()

u = UsesIt()
try:
    u.v = 1
except AttributeError as e:
    print("instance assignment -> __set__:", e)
UsesIt.v = 1                                # silently destroys the descriptor
print("after UsesIt.v = 1 ->", UsesIt.v, "| type:", type(UsesIt.__dict__["v"]).__name__)

# 13. Lazy Descriptor: Compute Once, Then Cache (cached_property Idea)
# ------------------------------------
# - A NON-data descriptor (only __get__) can cache by writing the result into
#   obj.__dict__ under the SAME name. Next lookup finds the instance dict first
#   (see section 3) and never calls __get__ again.
# - This is exactly how functools.cached_property works.
class Lazy:
    def __init__(self, func):
        self.func = func
    def __set_name__(self, owner, name):
        self.name = name
    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        value = self.func(obj)
        obj.__dict__[self.name] = value     # shadows the descriptor from now on
        return value

class Report:
    @Lazy
    def data(self):
        print("      -> computing (expensive)...")
        return [1, 2, 3]

r = Report()
print("first access :", r.data)
print("second access:", r.data, "(no compute message = cached)")
del r.__dict__["data"]
print("after clearing the cache it recomputes:", r.data)

# 14. functools.cached_property and Its Gotchas
# ------------------------------------
# - The stdlib version of section 13: from functools import cached_property.
# - Needs a writable instance __dict__ -> fails on classes with __slots__ (no __dict__).
# - It is a non-data descriptor, so you CAN assign over it, and `del obj.attr`
#   clears the cache (unlike @property + lru_cache).
# - The value never updates when the inputs change - it is computed once. If the
#   inputs are mutable, consider a plain @property instead.
from functools import cached_property

class Stats:
    def __init__(self, nums):
        self.nums = nums
    @cached_property
    def total(self):
        print("      -> summing")
        return sum(self.nums)

s = Stats([1, 2, 3])
print(s.total, s.total)
s.nums.append(100)
print("stale after mutation (still cached):", s.total)
del s.total
print("after del (cache cleared):", s.total)

class SlottedStats:
    __slots__ = ("nums",)
    def __init__(self, nums):
        self.nums = nums
    @cached_property
    def total(self):
        return sum(self.nums)

try:
    SlottedStats([1]).total
except TypeError as e:
    print("cached_property + __slots__:", e)

# 15. A Read-Only (Non-Data) vs Truly Read-Only (Data) Descriptor
# ------------------------------------
# - A non-data descriptor can be shadowed by assignment: obj.attr = x writes
#   to the instance dict and the descriptor is bypassed.
# - To make something truly read-only, define __set__ that raises.
class ReadOnlyWeak:
    def __get__(self, obj, objtype=None):
        return "constant"

class ReadOnlyStrong(ReadOnlyWeak):
    def __set__(self, obj, value):
        raise AttributeError("read-only")

class Box:
    weak = ReadOnlyWeak()
    strong = ReadOnlyStrong()

bx = Box()
bx.weak = "oops"
print("weak read-only got overwritten:", bx.weak)
try:
    bx.strong = "oops"
except AttributeError as e:
    print("strong read-only protected:", e)

# 16. __delete__ and del obj.attr
# ------------------------------------
# - del obj.attr calls type(obj).attr.__delete__(obj) for data descriptors.
# - property takes it from @attr.deleter. Without one: AttributeError.
class Account:
    def __init__(self):
        self._pin = "1234"
    @property
    def pin(self):
        return self._pin
    @pin.deleter
    def pin(self):
        print("      -> wiping pin")
        self._pin = None

acc = Account()
del acc.pin
print("pin after del:", acc.pin)
try:
    del Circle(1).diameter
except AttributeError as e:
    print("del without deleter:", e)

# 17. Real-World Uses of the Descriptor Protocol
# ------------------------------------
# - property, classmethod, staticmethod, functions-as-methods, functools.cached_property
# - __slots__ members: each slot is a "member descriptor" on the class
# - dataclasses.field defaults, and ORMs (Django models fields, SQLAlchemy columns)
# - typing helpers, validation libraries
# - Quick proof for __slots__ below.
class Point:
    __slots__ = ("x", "y")

print("slot is a descriptor:", type(Point.__dict__["x"]).__name__)
print("slot descriptor has __get__/__set__:",
      hasattr(Point.__dict__["x"], "__get__"), hasattr(Point.__dict__["x"], "__set__"))

# 18. Summary: Which One Should I Reach For?
# ------------------------------------
# - One attribute needing a check/compute      -> @property (see 02-Encapsulation.py)
# - Same rule repeated on many attributes      -> a custom descriptor class
# - Expensive value computed once per instance -> functools.cached_property
# - Need access to the attribute NAME          -> descriptor with __set_name__
# - Control ANY missing attribute dynamically  -> __getattr__ (see 10-Attribute-Access-Hooks.py)
# - Control how CLASSES are built              -> see 11-Metaclasses-And-Class-Creation.py
print("Done: descriptors power property, methods, slots and cached_property.")
