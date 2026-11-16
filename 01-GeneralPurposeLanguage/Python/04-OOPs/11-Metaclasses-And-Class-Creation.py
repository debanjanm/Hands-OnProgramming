import sys

# 01. Classes Are Objects Too
# ------------------------------------
# - In Python a class is itself an object (an instance of another class).
# - type(obj) gives the class of obj; type(Class) gives the class of the class,
#   called its METACLASS. By default every class is an instance of `type`.
# - So: instance --is-a--> class --is-a--> metaclass (type) --is-a--> type itself.
# - (Instances and classes basics: see 01-Class-Object.py)
class Plain:
    pass

p = Plain()
print("type(p)         :", type(p).__name__)
print("type(Plain)     :", type(Plain).__name__)
print("type(type)      :", type(type).__name__, "(type is its own metaclass)")
print("type(int)       :", type(int).__name__, "| type(len):", type(len).__name__)
print("isinstance(Plain, object):", isinstance(Plain, object), "(classes are objects)")

# 02. type(name, bases, namespace): Building a Class by Hand
# ------------------------------------
# - The `class` statement is just sugar for calling type with three arguments:
#     type(name, bases, namespace_dict)
# - Useful for generating classes at runtime (from config, from a database schema...).
def greet(self):
    return f"Hi, I am {self.name}"

def init(self, name):
    self.name = name

Person = type("Person", (object,), {"__init__": init, "greet": greet, "species": "human"})
who = Person("Asha")
print("manual class:", Person.__name__, "|", who.greet(), "|", Person.species)

class PersonSugar:                      # the exact same thing, written normally
    species = "human"
    __init__ = init
    greet = greet

print("same behaviour:", PersonSugar("Ravi").greet())
Student = type("Student", (Person,), {"school": "ABC"})      # inheritance works too
print("Student MRO:", [c.__name__ for c in Student.__mro__], "|", Student("Mia").greet())

# 03. What Really Happens When Python Runs a `class` Statement
# ------------------------------------
# - Steps for `class Foo(Base, metaclass=Meta):`
#     1. Work out the metaclass (explicit keyword, else the type of the bases, else type).
#     2. Call Meta.__prepare__(name, bases) -> returns the namespace dict (default: {}).
#     3. Execute the class body, filling that namespace.
#     4. Call Meta(name, bases, namespace) -> runs Meta.__new__ then Meta.__init__.
#        Inside type.__new__ (reached via super().__new__ in your __new__), Python:
#          4a. calls __set_name__ on every attribute that has it (see 09-Descriptors-And-Properties.py)
#          4b. calls parent.__init_subclass__(**kwargs)
#        so both happen BEFORE your Meta.__init__ runs.
#     5. Bind the name Foo to the result (class decorators run just before this).
# - The trace below prints each step in the order it really happens.
class Trace(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kw):
        print(f"   1. __prepare__({name})")
        return {}
    def __new__(mcls, name, bases, ns, **kw):
        print(f"   3. Meta.__new__({name}) ns keys: {[k for k in ns if not k.startswith('__')]}")
        return super().__new__(mcls, name, bases, ns)
    def __init__(cls, name, bases, ns, **kw):
        print(f"   4. Meta.__init__({name})")
        super().__init__(name, bases, ns)

class Marker:
    def __set_name__(self, owner, name):
        print(f"   3b. Marker.__set_name__ for {name!r}")

class TraceBase:
    def __init_subclass__(cls, **kw):
        print(f"   3c. __init_subclass__ for {cls.__name__}")
        super().__init_subclass__()

print("Defining class Traced:")
class Traced(TraceBase, metaclass=Trace):
    print("   2. class body is running")
    m = Marker()
    def method(self):
        pass
print("   done; Traced is", Traced.__name__)

# 04. A Custom Metaclass: __new__ and __init__
# ------------------------------------
# - A metaclass is just a subclass of `type`. Its __new__ CREATES the class and may change
#   the namespace first; its __init__ only sets up the already-created class.
# - Rule of thumb: change the namespace/bases -> __new__; inspect/register -> __init__.
class UpperAttrs(type):
    """Uppercases every public attribute name of classes built with it."""
    def __new__(mcls, name, bases, ns):
        new_ns = {(k.upper() if not k.startswith("__") else k): v for k, v in ns.items()}
        return super().__new__(mcls, name, bases, new_ns)

class Settings(metaclass=UpperAttrs):
    host = "localhost"
    port = 8080

print("Settings has HOST:", hasattr(Settings, "HOST"), "| has host:", hasattr(Settings, "host"), "| HOST =", Settings.HOST)
print("type(Settings):", type(Settings).__name__)

# 05. Metaclass __call__: Controlling Instance Creation
# ------------------------------------
# - Calling a class, Foo(...), is really type(Foo).__call__(Foo, ...). The default
#   __call__ runs Foo.__new__ then Foo.__init__.
# - Overriding __call__ on the METACLASS lets you hijack that: singletons, caches,
#   pools, forced validation.
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in Singleton._instances:
            print(f"      creating the one {cls.__name__}")
            Singleton._instances[cls] = super().__call__(*args, **kwargs)
        return Singleton._instances[cls]

class Database(metaclass=Singleton):
    def __init__(self, url="sqlite://"):
        self.url = url

d1, d2 = Database("first"), Database("second")
print("same object:", d1 is d2, "| url kept from first call:", d2.url)
# - Gotcha: the second argument ("second") was silently ignored. Singletons hide that.
# - Often a plain module-level instance is simpler than a Singleton metaclass.

# 06. __prepare__: Customising the Class Namespace
# ------------------------------------
# - __prepare__ returns the mapping used while the class BODY runs. Since 3.6 dicts
#   keep order, so __prepare__ is rarely needed. Still, it lets you catch bad code:
#   here we forbid defining the same name twice in a class body.
class NoDupes(dict):
    def __setitem__(self, key, value):
        if key in self and not key.startswith("__"):
            raise TypeError(f"duplicate definition of {key!r} in class body")
        super().__setitem__(key, value)

class StrictMeta(type):
    @classmethod
    def __prepare__(mcls, name, bases):
        return NoDupes()
    def __new__(mcls, name, bases, ns):
        return super().__new__(mcls, name, bases, dict(ns))   # convert back to a plain dict

try:
    class Oops(metaclass=StrictMeta):
        def run(self): return 1
        def run(self): return 2
except TypeError as e:
    print("StrictMeta stopped it:", e)

# 07. __init_subclass__: The Simple Alternative (Python 3.6+)
# ------------------------------------
# - A classmethod on a PARENT class, called every time a subclass is defined.
#   It covers most things people used metaclasses for, with far less machinery.
# - It receives class keyword arguments: class Child(Base, flag=True).
# - Gotcha: it runs for SUBCLASSES only, never for the class that defines it.
# - Gotcha: call super().__init_subclass__(**kwargs) so other mixins also run.
class Plugin:
    registry = {}
    def __init_subclass__(cls, /, name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        Plugin.registry[name or cls.__name__.lower()] = cls

class CsvPlugin(Plugin):
    pass

class JsonPlugin(Plugin, name="js"):
    pass

print("registry:", {k: v.__name__ for k, v in Plugin.registry.items()})
print("Plugin itself is not registered:", "plugin" not in Plugin.registry)

# 08. Registry Pattern: Metaclass vs __init_subclass__
# ------------------------------------
# - Same job, two tools. Prefer __init_subclass__; reach for a metaclass only if you must
#   change the namespace BEFORE the class exists or control instance creation (__call__).
class RegistryMeta(type):
    registry = {}
    def __init__(cls, name, bases, ns):
        super().__init__(name, bases, ns)
        if bases:                                  # skip the abstract root itself
            RegistryMeta.registry[name] = cls

class Handler(metaclass=RegistryMeta):
    pass

class EmailHandler(Handler):
    pass

class SmsHandler(Handler):
    pass

print("metaclass registry   :", sorted(RegistryMeta.registry))
print("__init_subclass__ one:", sorted(Plugin.registry))
print("Metaclass is inherited: type(SmsHandler) =", type(SmsHandler).__name__)

# 09. __class_getitem__: Making Cls[int] Work
# ------------------------------------
# - Class[x] normally fails (a class is not subscriptable). Defining the classmethod
#   __class_getitem__ makes it work - this is how list[int] and dict[str, int] work.
# - It runs on the class, not instances. Use it for type-hint style generics.
class Stack:
    def __class_getitem__(cls, item):
        print(f"      __class_getitem__({item!r})")
        return f"{cls.__name__}[{getattr(item, '__name__', item)}]"

print("Stack[int]      ->", Stack[int])
print("list[int]       ->", list[int], "(builtin generic alias)")
print("Stack()[0] fails (instances are not subscriptable):", end=" ")
try:
    Stack()[0]
except TypeError as e:
    print(e)
# - Gotcha: if the METACLASS defines __getitem__, it takes priority over __class_getitem__.

# 10. __set_name__: The Link Between Classes and Descriptors
# ------------------------------------
# - type.__new__ (the default class builder) calls __set_name__(owner, name) on every
#   namespace value that defines it - this is how a descriptor learns its own name.
# - It is part of class creation (step 4a of section 3), so it fires BEFORE
#   __init_subclass__ and before decorators.
# - Gotcha: attributes added to the class LATER (Cls.x = Field()) do not get
#   __set_name__ called automatically; call it yourself.
class Field:
    def __set_name__(self, owner, name):
        self.name = name
        print(f"      Field bound to {owner.__name__}.{name}")

class Model:
    id = Field()
    title = Field()

Model.late = Field()
print("late field has name?", hasattr(Model.late, "name"))
Model.late.__set_name__(Model, "late")

# 11. Metaclass That Collects Fields (Mini ORM / Form Idea)
# ------------------------------------
# - A realistic metaclass use: scan the class body for special objects and build
#   extra class-level data (like Django models do).
class Col:
    def __init__(self, kind):
        self.kind = kind

class ModelMeta(type):
    def __new__(mcls, name, bases, ns):
        cols = {k: v.kind for k, v in ns.items() if isinstance(v, Col)}
        ns = {k: v for k, v in ns.items() if k not in cols}   # remove raw Col objects
        cls = super().__new__(mcls, name, bases, ns)
        cls._columns = cols
        return cls

class User(metaclass=ModelMeta):
    id = Col("int")
    email = Col("str")
    def describe(self):
        return ", ".join(f"{k}:{v}" for k, v in self._columns.items())

print("collected columns:", User._columns)
print("describe():", User().describe())
print("raw Col removed from class:", hasattr(User, "email"))

# 12. Class Decorators: The Lighter Alternative
# ------------------------------------
# - A function that receives a finished class and returns it (modified or replaced).
# - Easiest to read and compose. Works on existing classes, no inheritance needed.
# - Limits: runs AFTER creation (cannot change __prepare__/namespace), is not inherited
#   by subclasses automatically. (dataclass in 06-Dataclasses... is a class decorator.)
def add_repr(cls):
    def __repr__(self):
        fields = ", ".join(f"{k}={v!r}" for k, v in vars(self).items())
        return f"{cls.__name__}({fields})"
    cls.__repr__ = __repr__
    return cls

def register(registry):
    def deco(cls):
        registry[cls.__name__] = cls
        return cls
    return deco

REG = {}

@register(REG)
@add_repr
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y

print(Point(1, 2), "| registered:", list(REG))

@add_repr
class Parent:
    def __init__(self):
        self.a = 1

class Child(Parent):
    def __init__(self):
        super().__init__()
        self.b = 2

print("Child inherits the decorator's __repr__ method:", Child())
print("but a decorator that REGISTERS would not auto-register Child:", "Child" not in REG)

# 13. Decision Table: Which Tool for Which Job?
# ------------------------------------
#   Need                                        Prefer
#   ------------------------------------------  ---------------------------------
#   Add/modify methods on one class             class decorator
#   Run code when a subclass is defined         __init_subclass__
#   Register subclasses / plugins               __init_subclass__
#   Per-attribute logic that knows its name     descriptor + __set_name__
#   Customise namespace, order, forbid dupes    metaclass __prepare__
#   Rewrite attributes before class exists      metaclass __new__
#   Control how instances are created           metaclass __call__ (or __new__ on the class)
#   Class-level dynamic attributes              metaclass __getattr__
# - Tim Peters: "Metaclasses are deeper magic than 99% of users should ever worry
#   about. If you wonder whether you need them, you don't."

# 14. Metaclass Methods vs Class Methods (Who Can See What)
# ------------------------------------
# - A method defined on a metaclass becomes available on the CLASS but NOT on its
#   instances. A classmethod is available on both. (Lookup rules: 10-Attribute-Access-Hooks.py)
class Meta14(type):
    def class_only(cls):
        return f"class_only on {cls.__name__}"
    @property
    def plural(cls):
        return cls.__name__ + "s"
    def __getattr__(cls, name):                # class-level fallback, see 10 section 17
        if name.startswith("find_by_"):
            return f"query by {name[8:]}"
        raise AttributeError(name)

class Thing(metaclass=Meta14):
    @classmethod
    def both(cls):
        return "both"

print(Thing.class_only(), "|", Thing.plural, "|", Thing.find_by_email)
print("instance has class_only?", hasattr(Thing(), "class_only"), "| instance has both?", hasattr(Thing(), "both"))

# 15. Gotcha: Metaclass Conflicts
# ------------------------------------
# - A class can only have ONE metaclass. When two bases have different, unrelated
#   metaclasses Python cannot pick one -> TypeError.
# - Real-life example: mixing an ABC (metaclass ABCMeta) with your own metaclass.
# - Fix: make a combined metaclass that inherits from both.
from abc import ABC, ABCMeta

class MetaA(type):
    pass

class MetaB(type):
    pass

class A(metaclass=MetaA):
    pass

class B(metaclass=MetaB):
    pass

try:
    class C(A, B):
        pass
except TypeError as e:
    print("conflict:", str(e)[:75] + "...")

class MetaAB(MetaA, MetaB):
    pass

class C2(A, B, metaclass=MetaAB):
    pass

print("fixed with a combined metaclass:", type(C2).__name__)

class MyMeta(type):
    pass

try:
    class Shape(ABC, metaclass=MyMeta):
        pass
except TypeError:
    print("ABC + your own metaclass conflicts too (ABC uses ABCMeta)")

class MyABCMeta(MyMeta, ABCMeta):
    pass

class Shape2(ABC, metaclass=MyABCMeta):
    pass

print("combined works:", type(Shape2).__name__, "| and __init_subclass__ avoids this problem entirely.")

# 16. Gotcha: Metaclass __init__ Runs for the Base Class Too
# ------------------------------------
# - Metaclass hooks fire for EVERY class using it, including the root base.
#   A registry usually needs `if bases:` (section 8) or a name check to skip the base.
# - Gotcha: super().__new__(mcls, name, bases, ns) - pass mcls, not cls. In __init__
#   the first argument IS the new class (cls), in __new__ it is the metaclass (mcls).
class Show(type):
    def __new__(mcls, name, bases, ns):
        print(f"   __new__ first arg is {mcls.__name__} (the metaclass)")
        return super().__new__(mcls, name, bases, ns)
    def __init__(cls, name, bases, ns):
        print(f"   __init__ first arg is {cls.__name__} (the new class)")
        super().__init__(name, bases, ns)

class ShowBase(metaclass=Show):
    pass

class ShowChild(ShowBase):
    pass

# 17. Metaclass with Class Keyword Arguments
# ------------------------------------
# - Extra keywords in the class line are passed to __prepare__, __new__, __init__
#   AND __init_subclass__. type.__new__ passes leftovers on to __init_subclass__,
#   and the default object.__init_subclass__ rejects unknown ones.
class KwMeta(type):
    def __new__(mcls, name, bases, ns, *, tag="none", **kw):
        cls = super().__new__(mcls, name, bases, ns, **kw)
        cls.tag = tag
        return cls
    def __init__(cls, name, bases, ns, *, tag="none", **kw):
        super().__init__(name, bases, ns)

class Tagged(metaclass=KwMeta, tag="blue"):
    pass

print("class keyword argument:", Tagged.tag)
try:
    class Bad(nope=1):
        pass
except TypeError as e:
    print("unknown class kwarg:", e)

# 18. Inspecting Classes: What type() Can Tell You
# ------------------------------------
# - Handy introspection on any class: __name__, __qualname__, __bases__, __mro__,
#   __dict__, __subclasses__(), isinstance(cls, type), issubclass().
print("Child.__name__    :", Child.__name__)
print("Child.__bases__   :", [b.__name__ for b in Child.__bases__])
print("Parent subclasses :", [s.__name__ for s in Parent.__subclasses__()])
print("isinstance(Child, type):", isinstance(Child, type), "| issubclass(Child, Parent):", issubclass(Child, Parent))
print("Python version used for this run is >= 3.9:", sys.version_info >= (3, 9))

# 19. When NOT to Use Metaclasses
# ------------------------------------
# - Try these first, in order: a plain function -> a class decorator -> __init_subclass__
#   -> a descriptor with __set_name__ -> (last) a metaclass.
# - Metaclasses make code harder to read, cause conflicts (section 15), and are
#   invisible to many readers and tools. Use them for frameworks (ORMs, ABCs, Enum),
#   not for application code.
# - Real stdlib metaclass users: abc.ABCMeta, enum.EnumMeta (EnumType), typing generics.
import enum
print("Enum is built by a metaclass:", type(enum.Enum).__name__)
print("ABC is built by a metaclass :", type(ABC).__name__)
print("Done: classes are objects, and type is the factory that builds them.")
