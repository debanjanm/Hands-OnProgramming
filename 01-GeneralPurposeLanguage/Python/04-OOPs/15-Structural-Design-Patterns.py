import functools
import sys
import weakref
from abc import ABC, abstractmethod

# 01. Structural Design Patterns - Introduction
# ------------------------------------
# - Structural patterns are about HOW classes and objects are put together
#   into bigger structures, while keeping the pieces flexible.
# - Covered here: Adapter, Bridge, Composite, Decorator (pattern),
#   Facade, Flyweight, Proxy.
# - Each section says what problem it solves, when NOT to use it, and a demo.
# - Python note: duck typing, first-class functions and __getattr__ make
#   several of these much lighter than in Java/C++.

print("Structural patterns: how to assemble objects")
print("Most of them are 'wrap something' in a smart way")

# 02. Adapter - What and Why
# ------------------------------------
# - Problem: you have a class with the WRONG interface (third-party or old
#   code you cannot edit) but your code expects a different one.
# - Fix: a small wrapper that translates calls from one to the other.
# - When NOT to use: if you own the class, just change it. Do not stack
#   adapters on adapters; that is a sign the design needs a rethink.

class OldPrinter:                       # cannot edit this
    def print_text_upper(self, s):
        return s.upper()

class Printer(ABC):                     # the interface our code expects
    @abstractmethod
    def show(self, s): ...

class PrinterAdapter(Printer):
    def __init__(self, old):
        self._old = old
    def show(self, s):
        return self._old.print_text_upper(s)

def client(printer: Printer):
    return printer.show("hello")

print("adapter:", client(PrinterAdapter(OldPrinter())))

# 03. Adapter - Python Idioms
# ------------------------------------
# - Because of duck typing, an adapter is often just a function or a
#   lambda; no interface class needed.
# - Another trick: a thin subclass that adds the missing method name.
# - Stdlib example: functools.partial and operator.attrgetter adapt calls.

old = OldPrinter()
show = lambda s: old.print_text_upper(s)         # function adapter

class AliasedPrinter(OldPrinter):                # subclass adapter
    show = OldPrinter.print_text_upper

print("function adapter:", show("abc"), "| subclass adapter:", AliasedPrinter().show("xyz"))

# 04. Bridge - What and Why
# ------------------------------------
# - Problem: two things vary independently (shape x color, remote x device).
#   With inheritance you get a class explosion: RedCircle, BlueCircle,
#   RedSquare, BlueSquare ... (N x M classes).
# - Fix: keep the two hierarchies apart, and let one HOLD the other
#   (composition). Now it is N + M classes.
# - When NOT to use: only one dimension varies. A plain subclass is fine.

class Color(ABC):
    @abstractmethod
    def fill(self): ...

class Red(Color):
    def fill(self): return "red"

class Blue(Color):
    def fill(self): return "blue"

class ShapeBase:
    def __init__(self, color: Color):       # the bridge
        self.color = color

class Circle(ShapeBase):
    def draw(self): return f"{self.color.fill()} circle"

class Square(ShapeBase):
    def draw(self): return f"{self.color.fill()} square"

for shape in (Circle(Red()), Circle(Blue()), Square(Red())):
    print("bridge:", shape.draw())

# 05. Bridge - Remote and Device Example
# ------------------------------------
# - Same idea with "abstraction" (what the user does) and "implementation"
#   (the device doing the work). New remotes and new devices combine freely.

class Device(ABC):
    @abstractmethod
    def power(self, on): ...

class Tv(Device):
    def power(self, on): return "TV " + ("on" if on else "off")

class Radio(Device):
    def power(self, on): return "Radio " + ("on" if on else "off")

class Remote:
    def __init__(self, device: Device):
        self.device = device
    def toggle(self):
        self.on = not getattr(self, "on", False)
        return self.device.power(self.on)

class SleepRemote(Remote):             # extends the remote side only
    def sleep(self):
        return self.device.power(False)

print(Remote(Tv()).toggle(), "|", Remote(Radio()).toggle(), "|", SleepRemote(Tv()).sleep())

# 06. Composite - What and Why
# ------------------------------------
# - Problem: you have a tree (folders and files, menus and items) and want
#   to treat one item and a group of items the SAME way.
# - Fix: leaf and group share one interface; a group holds children and
#   forwards the call to each of them.
# - When NOT to use: flat data. Also be careful with leaf-only operations
#   like add(); they make no sense on a leaf.

class Node(ABC):
    @abstractmethod
    def size(self): ...

class File(Node):
    def __init__(self, name, kb):
        self.name, self.kb = name, kb
    def size(self):
        return self.kb

class Folder(Node):
    def __init__(self, name):
        self.name = name
        self.children = []
    def add(self, node):
        self.children.append(node)
        return self
    def size(self):
        return sum(child.size() for child in self.children)

root = Folder("root").add(File("a.txt", 10)).add(
    Folder("docs").add(File("b.pdf", 200)).add(File("c.pdf", 300)))
print("composite total size:", root.size(), "KB")

# 07. Composite - Printing the Tree and Iterating
# ------------------------------------
# - A recursive method walks any depth. A generator keeps it lazy.

def walk(node, depth=0):
    yield "  " * depth + node.name
    for child in getattr(node, "children", []):
        yield from walk(child, depth + 1)

print("\n".join(walk(root)))

# 08. Decorator Pattern - What and Why
# ------------------------------------
# - Problem: add extra behavior to an object at RUNTIME, without changing
#   its class and without a subclass for every combination.
# - Fix: wrap the object in another object with the SAME interface. Wrappers
#   can be stacked in any order.
# - When NOT to use: if the extras are fixed, just write one class. Deep
#   stacks are hard to debug (which layer did what?).

class Coffee(ABC):
    @abstractmethod
    def cost(self): ...
    @abstractmethod
    def label(self): ...

class Espresso(Coffee):
    def cost(self): return 3
    def label(self): return "espresso"

class AddOn(Coffee):                      # base wrapper, same interface
    def __init__(self, inner: Coffee):
        self.inner = inner

class Milk(AddOn):
    def cost(self): return self.inner.cost() + 1
    def label(self): return self.inner.label() + " + milk"

class Sugar(AddOn):
    def cost(self): return self.inner.cost() + 0.5
    def label(self): return self.inner.label() + " + sugar"

order = Sugar(Milk(Espresso()))
print("decorator pattern:", order.label(), "=", order.cost())

# 09. Decorator Pattern vs Python @decorator
# ------------------------------------
# - The GoF Decorator pattern wraps OBJECTS to add behavior at runtime.
# - Python's @decorator syntax wraps FUNCTIONS or CLASSES at definition time.
# - They share the "wrap to add behavior" idea, but they are not the same
#   thing. @decorator is a language feature; the pattern is a design idea.
# - Always use functools.wraps so the wrapped function keeps its name/docs.

def shout(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs).upper() + "!"
    return wrapper

@shout
def greet(name):
    """Say hi."""
    return f"hi {name}"

print("@decorator:", greet("sam"), "| name kept:", greet.__name__, "| doc:", greet.__doc__)

# 10. Facade
# ------------------------------------
# - Problem: a subsystem has many classes and a fussy call order. Callers
#   only need a few common tasks.
# - Fix: one simple class with a few easy methods that call the messy parts.
# - It does NOT hide the subsystem; advanced users can still use it directly.
# - When NOT to use: if the subsystem is already simple. A facade that
#   grows into a "god class" doing everything is a smell.

class Amplifier:
    def on(self): return "amp on"
class Projector:
    def on(self): return "projector on"
class Lights:
    def dim(self): return "lights dim"

class HomeTheater:
    def __init__(self):
        self.amp, self.proj, self.lights = Amplifier(), Projector(), Lights()
    def watch_movie(self):
        return [self.lights.dim(), self.proj.on(), self.amp.on()]

print("facade:", HomeTheater().watch_movie())

# 11. Facade - Python Idioms
# ------------------------------------
# - In Python a facade is often just a module whose functions hide a few
#   internal modules, or one friendly function.
# - Real examples: requests.get() hides sockets/TLS/HTTP; shutil.copytree()
#   hides directory walking; json.dumps() hides the encoder setup.

def quick_report(data):
    """Facade function: three internal steps, one call."""
    cleaned = [x for x in data if x is not None]
    total = sum(cleaned)
    return f"n={len(cleaned)} total={total}"

print("function facade:", quick_report([1, None, 2, 3]))

# 12. Flyweight - What and Why
# ------------------------------------
# - Problem: you need MANY objects that mostly hold the same data (the
#   letters in a text editor, trees in a game), and memory runs out.
# - Fix: split state. Intrinsic (shared, never changes) lives in a shared
#   flyweight. Extrinsic (differs per use, like position) is passed in.
# - A factory returns the same flyweight for the same key.
# - When NOT to use: few objects, or little shared data. Complexity for
#   nothing.

class TreeType:                          # intrinsic: shared
    def __init__(self, name, color):
        self.name, self.color = name, color
    def draw(self, x, y):                # extrinsic: passed in
        return f"{self.color} {self.name} at ({x},{y})"

class TreeFactory:
    _types = {}
    @classmethod
    def get(cls, name, color):
        key = (name, color)
        if key not in cls._types:
            cls._types[key] = TreeType(name, color)
        return cls._types[key]

forest = [(TreeFactory.get("oak", "green"), x, 0) for x in range(1000)]
forest.append((TreeFactory.get("pine", "dark green"), 5, 5))
print("trees:", len(forest), "| shared types:", len(TreeFactory._types))
print(forest[3][0].draw(forest[3][1], forest[3][2]))

# 13. Flyweight - __slots__
# ------------------------------------
# - Normal objects keep attributes in a per-object __dict__ (extra memory).
# - __slots__ replaces that dict with fixed slots: smaller objects, and
#   typos like p.zz = 1 raise AttributeError.
# - Trade-off: no new attributes, no default __weakref__ unless you list it.
# - Sizes below are compared with sys.getsizeof; we print only the booleans
#   so output stays the same on every machine.

class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y

class SlotPoint:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

pp, sp = PlainPoint(1, 2), SlotPoint(1, 2)
plain_total = sys.getsizeof(pp) + sys.getsizeof(pp.__dict__)
print("slots object smaller:", sys.getsizeof(sp) < plain_total)
print("plain has __dict__:", hasattr(pp, "__dict__"), "| slots has __dict__:", hasattr(sp, "__dict__"))
try:
    sp.z = 3
except AttributeError:
    print("slots blocks new attributes")

# 14. Flyweight - weakref Cache
# ------------------------------------
# - A plain dict cache keeps flyweights alive forever.
# - WeakValueDictionary drops an entry once nobody else uses the object, so
#   the cache cleans itself. (Needs a class that supports weak references;
#   normal classes do, __slots__ classes need "__weakref__" in slots.)

class Glyph:
    __slots__ = ("char", "__weakref__")
    _cache = weakref.WeakValueDictionary()

    def __init__(self, char):
        self.char = char

    @classmethod
    def get(cls, char):
        g = cls._cache.get(char)
        if g is None:
            g = cls(char)
            cls._cache[char] = g
        return g

g1, g2 = Glyph.get("a"), Glyph.get("a")
print("same flyweight:", g1 is g2, "| cached:", len(Glyph._cache))
del g1, g2
print("cached after release:", len(Glyph._cache))

# 15. Proxy - What and Why
# ------------------------------------
# - Problem: you want to control ACCESS to an object: delay creating it,
#   check permissions, cache results, log calls.
# - Fix: a stand-in with the SAME interface that decides when and how to
#   forward to the real object.
# - Difference from Decorator: a decorator ADDS behavior; a proxy CONTROLS
#   access. The code looks alike; the intent differs.
# - When NOT to use: no real access concern. Then it is just a wrapper.

class Image(ABC):
    @abstractmethod
    def show(self): ...

class RealImage(Image):
    def __init__(self, path):
        print("  loading", path, "(slow)")
        self.path = path
    def show(self):
        return f"showing {self.path}"

print("proxy ideas: virtual, protection, caching - next three sections")

# 16. Virtual Proxy (lazy loading)
# ------------------------------------
# - Delay creating the expensive object until the first real use.

class LazyImage(Image):
    def __init__(self, path):
        self.path, self._real = path, None
    def show(self):
        if self._real is None:
            self._real = RealImage(self.path)
        return self._real.show()

img = LazyImage("cat.png")
print("created proxy, nothing loaded yet")
print(img.show())
print(img.show())                       # second call: no reload

# 17. Protection Proxy
# ------------------------------------
# - Check permission before letting the call through.

class Vault:
    def open(self):
        return "vault opened"

class VaultProxy:
    def __init__(self, vault, user_role):
        self._vault, self._role = vault, user_role
    def open(self):
        if self._role != "admin":
            raise PermissionError(f"role '{self._role}' cannot open vault")
        return self._vault.open()

print(VaultProxy(Vault(), "admin").open())
try:
    VaultProxy(Vault(), "guest").open()
except PermissionError as e:
    print("denied:", e)

# 18. Caching Proxy
# ------------------------------------
# - Remember results of slow calls, return the saved one for the same input.
# - Python shortcut: functools.lru_cache does exactly this for functions.
# - Gotcha: only cache pure results. If the answer changes over time, the
#   cache serves stale data.

class SlowService:
    def __init__(self):
        self.calls = 0
    def fetch(self, key):
        self.calls += 1
        return key * 2

class CachingProxy:
    def __init__(self, service):
        self._service, self._cache = service, {}
    def fetch(self, key):
        if key not in self._cache:
            self._cache[key] = self._service.fetch(key)
        return self._cache[key]

svc = SlowService()
proxy = CachingProxy(svc)
print(proxy.fetch(5), proxy.fetch(5), proxy.fetch(6), "| real calls:", svc.calls)

# 19. Proxy with __getattr__ (dynamic forwarding)
# ------------------------------------
# - Writing every method by hand is tedious. __getattr__ runs only when a
#   normal lookup FAILS, so it can forward unknown names to the real object.
# - Great for logging proxies that must mimic any class.
# - Gotchas: special methods like __len__ or __str__ are looked up on the
#   TYPE, so __getattr__ does not catch them. Also set self._target via
#   object.__setattr__ style care if you also override __setattr__.

class LoggingProxy:
    def __init__(self, target):
        self._target = target
        self.log = []

    def __getattr__(self, name):
        attr = getattr(self._target, name)       # AttributeError if missing
        if callable(attr):
            def wrapper(*args, **kwargs):
                self.log.append(f"call {name}{args}")
                return attr(*args, **kwargs)
            return wrapper
        return attr

lp = LoggingProxy([3, 1, 2])
lp.append(0)
lp.sort()
print("proxied list:", lp._target, "| log:", lp.log)
try:
    len(lp)
except TypeError:
    print("len() not forwarded: dunder methods skip __getattr__")

# 20. Decorator vs Proxy vs Adapter vs Facade
# ------------------------------------
# - All four "wrap" something. The difference is INTENT:
#   Adapter : change the interface to one you need.
#   Decorator: keep the interface, add behavior.
#   Proxy   : keep the interface, control access.
#   Facade  : new, simpler interface over MANY objects.
# - Composite and Bridge are about shape (tree / two hierarchies), and
#   Flyweight is about memory sharing.

print("Adapter: new interface | Decorator: add | Proxy: control | Facade: simplify")

# 21. Python-Idiomatic Alternatives
# ------------------------------------
# - Adapter    -> a function, lambda, or small subclass (duck typing).
# - Bridge     -> pass a strategy/callable in as an argument.
# - Composite  -> nested lists/dicts, or one recursive function.
# - Decorator  -> @decorator on functions, contextlib, functools.wraps.
# - Facade     -> a module with a few friendly functions.
# - Flyweight  -> interning, __slots__, functools.lru_cache on a factory.
# - Proxy      -> __getattr__, properties, functools.cached_property.
# - Rule: reach for the pattern when it removes real pain, not by habit.

class Report:
    def __init__(self):
        self.builds = 0

    @functools.cached_property          # lazy + cached, a mini virtual proxy
    def data(self):
        self.builds += 1
        return [1, 2, 3]

rep = Report()
rep.data
rep.data
print("cached_property built once:", rep.builds)

@functools.lru_cache(maxsize=None)      # a flyweight/caching factory in one line
def make_key(n):
    return ("key", n)

print("lru_cache flyweight:", make_key(1) is make_key(1))
