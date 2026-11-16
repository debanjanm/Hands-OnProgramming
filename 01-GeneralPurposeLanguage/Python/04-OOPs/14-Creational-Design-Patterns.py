import copy
import threading
import weakref
from abc import ABC, abstractmethod
from queue import Queue

# 01. Creational Design Patterns - Introduction
# ------------------------------------
# - Creational patterns are about HOW objects get created, so the calling
#   code does not depend on exact classes or messy construction steps.
# - Covered here: Singleton, Factory Method, Simple Factory, Abstract Factory,
#   Builder, Prototype, Object Pool, Borg (Monostate).
# - Each section says what problem it solves, when NOT to use it, and a demo.
# - Python note: classes are objects, functions are objects, modules are
#   singletons. So many patterns from Java/C++ books shrink to a few lines here.

print("Creational patterns: control how objects are made")
print("Python often replaces a pattern with a function, a dict, or a module")

# 02. Singleton - What and Why
# ------------------------------------
# - Problem: you want exactly ONE instance of something (config, logger,
#   connection manager) and one shared access point to it.
# - When NOT to use: it is a hidden global. It makes tests hard (state leaks
#   between tests) and couples code to one instance. Prefer passing an object
#   in (dependency injection) unless "only one" is a real rule.
# - Next four sections show four Pythonic ways to build one.

print("\nSingleton: one instance, shared everywhere")

# 03. Singleton Way 1 - Module Level Object
# ------------------------------------
# - A module is imported once and cached in sys.modules. So a plain object
#   created at module level is already a singleton. This is the simplest way.
# - Here we fake a module with a tiny class instance to keep one file.

class _Settings:
    def __init__(self):
        self.debug = False

settings = _Settings()          # imagine this lives in settings.py
alias = settings                # "importing" it again gives the same object
alias.debug = True
print("module style shares state:", settings.debug, settings is alias)

# 04. Singleton Way 2 - Metaclass
# ------------------------------------
# - A metaclass controls what happens on ClassName(...) via __call__.
# - It keeps a dict of {class: instance}. The first call builds it, later
#   calls return the stored one. Works for any class that uses this metaclass.

class SingletonMeta(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        print("Config.__init__ runs once")
        self.env = "dev"

c1 = Config()
c2 = Config()
print("metaclass singleton:", c1 is c2)

# 05. Singleton Way 3 - Override __new__
# ------------------------------------
# - __new__ creates the object, __init__ only fills it. So we override __new__
#   to return the saved instance if there is one.
# - Gotcha: __init__ still runs on EVERY call, so guard it if it resets state.

class Logger:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lines = []
        return cls._instance

    def log(self, msg):
        self.lines.append(msg)

Logger().log("first")
Logger().log("second")
print("__new__ singleton:", Logger().lines, Logger() is Logger())

# 06. Singleton Way 4 - Decorator
# ------------------------------------
# - A class decorator wraps the class so calling it returns a cached instance.
# - Downside: the name now points to a function, not a class, so isinstance()
#   and subclassing break. Fine for small scripts, less nice for big code.

def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self):
        self.url = "db://local"

print("decorator singleton:", Database() is Database(), Database().url)
print("decorator downside, Database is now:", type(Database).__name__)

# 07. Singleton Thread-Safety
# ------------------------------------
# - Problem: two threads can both see "no instance yet" and both create one.
# - Fix: double-checked locking. Check, take a lock, check again, then create.
# - The first check skips the lock on the fast path (after creation).
# - Here a tiny sleep-free demo: many threads, still only one instance.

class SafeSingleton:
    _instance = None
    _lock = threading.Lock()
    count = 0

    def __new__(cls):
        if cls._instance is None:               # fast check, no lock
            with cls._lock:
                if cls._instance is None:       # re-check inside lock
                    cls._instance = super().__new__(cls)
                    SafeSingleton.count += 1
        return cls._instance

found = []
threads = [threading.Thread(target=lambda: found.append(SafeSingleton())) for _ in range(20)]
for t in threads:
    t.start()
for t in threads:
    t.join()
print("threads:", len(found), "| distinct instances:", len({id(x) for x in found}),
      "| created:", SafeSingleton.count)

# 08. Factory Method
# ------------------------------------
# - Problem: a base class wants to use an object but let SUBCLASSES decide
#   which concrete class to build. The base calls an overridable method.
# - When NOT to use: if there is only one product type, just call the class.

class Document(ABC):
    @abstractmethod
    def render(self): ...

class PdfDoc(Document):
    def render(self):
        return "PDF bytes"

class HtmlDoc(Document):
    def render(self):
        return "<html>"

class Exporter(ABC):
    @abstractmethod
    def create_document(self) -> Document:      # the factory method
        ...

    def export(self):                            # shared logic uses it
        return "exported: " + self.create_document().render()

class PdfExporter(Exporter):
    def create_document(self):
        return PdfDoc()

class HtmlExporter(Exporter):
    def create_document(self):
        return HtmlDoc()

for exporter in (PdfExporter(), HtmlExporter()):
    print(exporter.export())

# 09. Simple Factory via dict
# ------------------------------------
# - Problem: if/elif chains to pick a class by name grow ugly.
# - Python fix: a dict mapping name -> class (or any callable). Adding a new
#   type is one dict entry. Not an official GoF pattern, but very common.
# - When NOT to use: unknown names need a clear error, so handle KeyError.

class Dog:
    def speak(self): return "Woof"

class Cat:
    def speak(self): return "Meow"

ANIMALS = {"dog": Dog, "cat": Cat}

def make_animal(kind):
    try:
        return ANIMALS[kind]()
    except KeyError:
        raise ValueError(f"unknown animal: {kind}") from None

print(make_animal("dog").speak(), make_animal("cat").speak())
try:
    make_animal("fish")
except ValueError as e:
    print("error:", e)

# 10. Factory via classmethods (alternative constructors)
# ------------------------------------
# - Problem: __init__ can only have one signature, but data comes in many
#   shapes (string, dict, tuple).
# - Fix: @classmethod factories that parse input and call cls(...).
#   Using cls (not the class name) keeps subclasses working.
# - Stdlib examples: dict.fromkeys, datetime.fromisoformat, int.from_bytes.

class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

    @classmethod
    def from_string(cls, text):
        x, y = text.split(",")
        return cls(int(x), int(y))

    @classmethod
    def from_dict(cls, d):
        return cls(d["x"], d["y"])

    def __repr__(self):
        return f"{type(self).__name__}({self.x}, {self.y})"

class Point3(Point):
    pass

print(Point.from_string("3,4"), Point.from_dict({"x": 1, "y": 2}))
print("subclass friendly:", Point3.from_string("5,6"))

# 11. Abstract Factory
# ------------------------------------
# - Problem: you need a FAMILY of related objects that must match each other
#   (a dark button with a dark checkbox, never dark + light mixed).
# - Fix: one factory per family, each creating all the related products.
# - When NOT to use: one product kind or no "must match" rule. Too heavy.

class Button(ABC):
    @abstractmethod
    def draw(self): ...

class Checkbox(ABC):
    @abstractmethod
    def draw(self): ...

class DarkButton(Button):
    def draw(self): return "[dark button]"

class DarkCheckbox(Checkbox):
    def draw(self): return "[dark checkbox]"

class LightButton(Button):
    def draw(self): return "[light button]"

class LightCheckbox(Checkbox):
    def draw(self): return "[light checkbox]"

class ThemeFactory(ABC):
    @abstractmethod
    def button(self) -> Button: ...
    @abstractmethod
    def checkbox(self) -> Checkbox: ...

class DarkTheme(ThemeFactory):
    def button(self): return DarkButton()
    def checkbox(self): return DarkCheckbox()

class LightTheme(ThemeFactory):
    def button(self): return LightButton()
    def checkbox(self): return LightCheckbox()

def build_screen(theme: ThemeFactory):
    return theme.button().draw() + " " + theme.checkbox().draw()

print(build_screen(DarkTheme()))
print(build_screen(LightTheme()))

# 12. Builder
# ------------------------------------
# - Problem: an object with many optional parts makes a huge constructor
#   (Pizza("large", True, False, True, None ...)) that nobody can read.
# - Fix: a builder collects parts step by step, then build() makes the object.
# - When NOT to use: Python already has keyword args and defaults. If a
#   dataclass with defaults works, use that instead.

class Pizza:
    def __init__(self, size, toppings, extra_cheese):
        self.size, self.toppings, self.extra_cheese = size, toppings, extra_cheese

    def __repr__(self):
        return f"Pizza({self.size}, {self.toppings}, cheese={self.extra_cheese})"

class PizzaBuilder:
    def __init__(self):
        self._size = "medium"
        self._toppings = []
        self._cheese = False

    def size(self, s):
        self._size = s

    def add_topping(self, t):
        self._toppings.append(t)

    def cheese(self):
        self._cheese = True

    def build(self):
        return Pizza(self._size, list(self._toppings), self._cheese)

b = PizzaBuilder()
b.size("large")
b.add_topping("olives")
b.cheese()
print(b.build())

# 13. Builder - Fluent Interface
# ------------------------------------
# - Fluent = each step returns self, so calls chain in one readable line.
# - Same idea as the section above, just nicer to read and write.
# - Gotcha: forgetting "return self" in one method breaks the chain with
#   an AttributeError on None.

class FluentPizzaBuilder(PizzaBuilder):
    def size(self, s):
        super().size(s)
        return self

    def add_topping(self, t):
        super().add_topping(t)
        return self

    def cheese(self):
        super().cheese()
        return self

print(FluentPizzaBuilder().size("small").add_topping("corn").add_topping("onion").cheese().build())

# 14. Prototype (copy)
# ------------------------------------
# - Problem: building an object from scratch is costly or fiddly, but you
#   already have a similar one. Clone it and tweak the clone.
# - Python gives this for free with the copy module.
# - shallow copy shares inner objects; deep copy duplicates everything.
# - When NOT to use: objects holding files, sockets, or locks. These cannot
#   be copied sensibly, so build them fresh.

class Enemy:
    def __init__(self, name, hp, loot):
        self.name, self.hp, self.loot = name, hp, loot

template = Enemy("Goblin", 30, ["coin"])
shallow = copy.copy(template)
deep = copy.deepcopy(template)
shallow.loot.append("gem")           # inner list is shared with template!
deep.loot.append("sword")            # deep copy has its own list
deep.name = "Goblin King"
print("template loot:", template.loot)
print("shallow shares loot:", shallow.loot is template.loot)
print("deep copy loot:", deep.loot, "| name:", deep.name)

# 15. Prototype with a registry and __copy__
# ------------------------------------
# - A registry stores ready-made prototypes by name; clients ask for a clone.
# - Define __copy__ if you need custom copy rules (e.g. skip a cache field).

class Shape:
    def __init__(self, kind, color):
        self.kind, self.color = kind, color
        self.cache = {"expensive": 42}

    def __copy__(self):
        new = type(self)(self.kind, self.color)
        new.cache = {}                       # do not carry cache over
        return new

    def __repr__(self):
        return f"Shape({self.kind}, {self.color}, cache={self.cache})"

PROTOTYPES = {"red_circle": Shape("circle", "red")}

def clone(name, **changes):
    obj = copy.copy(PROTOTYPES[name])
    for key, value in changes.items():
        setattr(obj, key, value)
    return obj

print(clone("red_circle"), clone("red_circle", color="blue"))

# 16. Object Pool
# ------------------------------------
# - Problem: some objects are expensive to create (DB connections, threads).
#   Create a few up front, lend them out, take them back, reuse them.
# - Python note: concurrent.futures and DB libraries already ship pools.
# - When NOT to use: cheap objects. A pool adds bugs (stale state, leaks)
#   for no gain. Always return items, so use try/finally or a context manager.

class Connection:
    def __init__(self, n):
        self.name = f"conn-{n}"
        self.uses = 0

class Pool:
    def __init__(self, size):
        self._free = Queue()
        for n in range(size):
            self._free.put(Connection(n))

    def acquire(self):
        return self._free.get()              # blocks if none free

    def release(self, conn):
        self._free.put(conn)

pool = Pool(2)
a = pool.acquire()
a.uses += 1
pool.release(a)
b = pool.acquire()                           # FIFO: gets conn-1 first
c = pool.acquire()                           # then conn-0, reused
c.uses += 1
print("got:", b.name, c.name, "| reused conn uses:", c.uses)
pool.release(b)
pool.release(c)

# 17. Pool as a Context Manager
# ------------------------------------
# - contextlib.contextmanager makes sure the item goes back even on error.

from contextlib import contextmanager

@contextmanager
def borrowed(p):
    conn = p.acquire()
    try:
        yield conn
    finally:
        p.release(conn)

try:
    with borrowed(pool) as conn:
        print("using", conn.name)
        raise RuntimeError("boom")
except RuntimeError:
    print("error happened, but item was returned:", pool._free.qsize(), "free")

# 18. Borg (Monostate)
# ------------------------------------
# - Problem: you want shared STATE, not one identity. Many instances, all
#   sharing one __dict__. So they look different but behave as one.
# - Pro: works with normal subclassing and isinstance, no __new__ tricks.
# - When NOT to use: it is still hidden global state, same testing pain
#   as Singleton. Subclasses share state too unless they get their own dict.

class Borg:
    _shared = {}
    def __init__(self):
        self.__dict__ = self._shared

x = Borg()
y = Borg()
x.color = "green"
print("borg shares state:", y.color, "| same object?", x is y)

# 19. Singleton vs Borg
# ------------------------------------
# - Singleton: one object. a is b is True.
# - Borg: many objects, one shared state. a is b is False, a.x == b.x.
# - Most of the time you want neither: pass the shared object as an argument.

print("singleton identity:", Config() is Config(), "| borg identity:", Borg() is Borg())

# 20. Pythonic Note - Patterns Often Become Functions/Modules
# ------------------------------------
# - Classes are first-class objects: pass a class around and call it, and
#   you already have a factory. No Factory class needed.
# - Functions are objects: a closure or functools.partial can act as a
#   builder or factory with preset arguments.
# - Modules are singletons. dataclasses + defaults often replace Builder.
# - copy.copy / deepcopy is Prototype. A dict of classes is a Factory.
# - Rule: use a pattern when it removes real pain, not to look professional.

from functools import partial

def make_greeter(cls):
    return cls()

print("class as factory:", make_greeter(Dog).speak())
make_big_pizza = partial(Pizza, "large", extra_cheese=True)
print("partial as factory:", make_big_pizza(["ham"]))

# 21. Weak-reference Registry (bonus: avoid leaks in caches/pools)
# ------------------------------------
# - A WeakValueDictionary lets cached objects disappear once nothing else
#   uses them, so a factory cache does not keep objects alive forever.

class Heavy:
    def __init__(self, key):
        self.key = key

cache = weakref.WeakValueDictionary()

def get_heavy(key):
    obj = cache.get(key)
    if obj is None:
        obj = Heavy(key)
        cache[key] = obj
    return obj

h1 = get_heavy("a")
h2 = get_heavy("a")
print("cached same object:", h1 is h2, "| in cache:", len(cache))
del h1, h2
print("after nothing references it:", len(cache))
