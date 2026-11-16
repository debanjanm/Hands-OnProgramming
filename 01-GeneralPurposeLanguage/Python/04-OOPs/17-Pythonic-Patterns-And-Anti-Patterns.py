from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from enum import Enum
from typing import Callable, Generic, Optional, Protocol, TypeVar

# 01. Pythonic Patterns And Anti-Patterns - Introduction
# ----------------------------
# - Good Python code uses the language's own tools (decorators, context
#   managers, dataclasses, duck typing) instead of copying Java-style designs.
# - Part 1 (sections 02-10): patterns that fit Python well.
# - Part 2 (sections 11-17): anti-patterns - common habits that cause pain.
# - Part 3 (sections 18-19): a code smell cheat sheet and a before/after refactor.
# - Each section: the problem, when NOT to use it, and a small demo.

# 02. Registry via decorators
# ----------------------------
# - Problem: you have a growing list of handlers/commands and a big
#   if/elif that must be edited for every new one.
# - Idea: a decorator adds each function to a dict at definition time.
# - New handler = new function with a decorator. Nothing else changes.
# - When NOT to use: two or three fixed handlers - a plain dict is fine.
#   Also note a registry only fills when its module is imported.
print("\n# Registry via decorators")

COMMANDS = {}

def command(name):
    def register(fn):
        COMMANDS[name] = fn
        return fn                      # return fn so it stays usable
    return register

@command("greet")
def greet(who):
    return f"hello {who}"

@command("shout")
def shout(who):
    return f"HEY {who.upper()}"

def run(name, arg):
    fn = COMMANDS.get(name)
    if fn is None:
        return f"unknown command: {name}"
    return fn(arg)

print(run("greet", "ana"), "|", run("shout", "ana"), "|", run("nope", "ana"))
print(sorted(COMMANDS))

# 03. Plugin registry via __init_subclass__
# ----------------------------
# - Problem: you want every subclass of a base to register itself
#   automatically, with no decorator and no metaclass.
# - Idea: __init_subclass__ runs once whenever a subclass is defined.
# - Class keyword arguments (class X(Base, kind="x")) pass config in.
# - When NOT to use: if registering explicitly is clearer. Magic that runs
#   at import time surprises readers.
print("\n# Plugin registry with __init_subclass__")

class Exporter:
    registry = {}
    def __init_subclass__(cls, fmt=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if fmt:
            Exporter.registry[fmt] = cls
    def export(self, data):
        raise NotImplementedError

class CsvExporter(Exporter, fmt="csv"):
    def export(self, data):
        return ",".join(map(str, data))

class PipeExporter(Exporter, fmt="pipe"):
    def export(self, data):
        return "|".join(map(str, data))

def export(fmt, data):
    return Exporter.registry[fmt]().export(data)

print(export("csv", [1, 2, 3]), export("pipe", [1, 2, 3]))
print(sorted(Exporter.registry))

# 04. Dependency injection without frameworks
# ----------------------------
# - Problem: a class creates its own helpers (database, mailer), so you
#   can't swap them or test without the real thing.
# - Idea: pass the helpers in (constructor or function argument).
# - No framework needed. Use a Protocol to describe what you need.
# - When NOT to use: tiny scripts, or objects that are never swapped.
#   Don't inject every little thing.
print("\n# Dependency injection")

class Mailer(Protocol):
    def send(self, to: str, body: str) -> None: ...

class SmtpMailer:
    def send(self, to, body):
        print(f"SMTP -> {to}: {body}")

class FakeMailer:                      # test double
    def __init__(self):
        self.sent = []
    def send(self, to, body):
        self.sent.append((to, body))

class SignupService:
    def __init__(self, mailer: Mailer):
        self.mailer = mailer           # injected, not created here
    def register(self, email):
        self.mailer.send(email, "welcome!")
        return f"registered {email}"

print(SignupService(SmtpMailer()).register("a@x.com"))
fake = FakeMailer()
SignupService(fake).register("b@x.com")
print(fake.sent)

# Functions can be injected too
def greet_user(name, formatter=str.title):
    return formatter(name)

print(greet_user("ana bo"), greet_user("ana bo", str.upper))

# 05. Context manager pattern
# ----------------------------
# - Problem: setup and cleanup must always happen as a pair
#   (open/close, lock/unlock, begin/rollback), even on errors.
# - Idea: "with" guarantees cleanup. Write one with @contextmanager
#   (generator) or with __enter__/__exit__.
# - When NOT to use: no cleanup needed, or cleanup is not tied to a block.
print("\n# Context manager pattern")

@contextmanager
def tag(name):
    print(f"<{name}>")
    try:
        yield name
    finally:
        print(f"</{name}>")           # always runs, even on error

with tag("div"):
    print("inside")

try:
    with tag("p"):
        raise ValueError("boom")
except ValueError as e:
    print("caught:", e)

class Timer:                           # class form; no real clock for stable output
    def __enter__(self):
        print("enter")
        return self
    def __exit__(self, exc_type, exc, tb):
        print("exit, error:", exc_type.__name__ if exc_type else None)
        return False                   # False = do not swallow the error

with Timer():
    pass

# 06. EAFP vs LBYP
# ----------------------------
# - LBYP = Look Before You Leap: check first, then act.
# - EAFP = Easier to Ask Forgiveness than Permission: act, handle errors.
# - Python prefers EAFP: shorter, and avoids the gap between "check" and
#   "use" (race conditions on files, for example).
# - When NOT to use EAFP: when failure is the common case and exceptions
#   are slow, or when the failing step has side effects you can't undo.
#   Also never use a bare "except:" - catch the specific error.
print("\n# EAFP vs LBYP")

data = {"name": "ana"}

# LBYP
if "age" in data:
    age = data["age"]
else:
    age = "unknown"
print("LBYP:", age)

# EAFP
try:
    age = data["age"]
except KeyError:
    age = "unknown"
print("EAFP:", age)

# Often there's an even shorter way
print("get:", data.get("age", "unknown"))

def to_int(text):
    try:
        return int(text)
    except ValueError:
        return None

print(to_int("42"), to_int("4x2"))

class Duck:
    def quack(self):
        return "quack"

def make_noise(thing):
    try:
        return thing.quack()           # duck typing: just try it
    except AttributeError:
        return "(silence)"

print(make_noise(Duck()), make_noise(42))

# 07. Repository (lite)
# ----------------------------
# - Problem: business code is mixed with storage code (SQL, files), so it
#   can't be tested or moved to another store.
# - Idea: a repository looks like a collection (add, get, list) and hides
#   where the data lives.
# - Here: in-memory version. A SQL version would have the same methods.
# - When NOT to use: a small script or CRUD app where the ORM already is
#   the abstraction. Don't wrap an ORM in a second ORM.
print("\n# Repository")

@dataclass
class User:
    id: int
    name: str

class InMemoryUserRepo:
    def __init__(self):
        self._rows = {}
    def add(self, user):
        self._rows[user.id] = user
    def get(self, user_id):
        return self._rows.get(user_id)
    def all(self):
        return [self._rows[k] for k in sorted(self._rows)]

def rename(repo, user_id, new_name):  # business code only knows the repo API
    user = repo.get(user_id)
    if user is None:
        return "no such user"
    user.name = new_name
    return "renamed"

repo = InMemoryUserRepo()
repo.add(User(2, "bo"))
repo.add(User(1, "ana"))
print(rename(repo, 1, "anna"), rename(repo, 9, "x"))
print(repo.all())

# 08. Unit of Work (lite)
# ----------------------------
# - Problem: several changes must succeed together or not at all.
# - Idea: collect changes, then commit once; on error roll back.
# - Python: a context manager is a natural Unit of Work.
# - When NOT to use: a real database transaction already gives you this.
#   This is just the idea in miniature.
print("\n# Unit of Work")

class UnitOfWork:
    def __init__(self, store):
        self.store = store             # a plain dict
        self._pending = {}
    def set(self, key, value):
        self._pending[key] = value
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.store.update(self._pending)   # commit
            print("committed", sorted(self._pending))
        else:
            print("rolled back", sorted(self._pending))
        return False

db = {}
with UnitOfWork(db) as uow:
    uow.set("a", 1)
    uow.set("b", 2)
print(db)

try:
    with UnitOfWork(db) as uow:
        uow.set("c", 3)
        raise RuntimeError("fail midway")
except RuntimeError:
    pass
print(db)                              # "c" never saved

# 09. Result / Option-style returns
# ----------------------------
# - Problem: functions that fail either raise (surprise!) or return None
#   or -1 (easy to forget to check).
# - Idea: return a small object that says "ok with value" or "error with
#   reason", so the caller must look at it.
# - Optional[T] (value or None) is the "Option" half.
# - When NOT to use: Python's normal answer is exceptions. Use Result only
#   at boundaries where failure is expected (parsing user input, validation).
print("\n# Result / Option returns")

T = TypeVar("T")

@dataclass(frozen=True)
class Ok(Generic[T]):
    value: T

@dataclass(frozen=True)
class Err:
    reason: str

def parse_age(text) -> "Ok[int] | Err":
    if not text.isdigit():
        return Err(f"not a number: {text!r}")
    age = int(text)
    if age > 150:
        return Err("too old")
    return Ok(age)

for raw in ["30", "abc", "200"]:
    match parse_age(raw):
        case Ok(value=v):
            print("ok", v)
        case Err(reason=r):
            print("error:", r)

def find_user(users, name) -> Optional[str]:
    return next((u for u in users if u == name), None)

found = find_user(["ana", "bo"], "cy")
print("found:", found if found is not None else "nobody")

# 10. Dataclass value objects
# ----------------------------
# - Problem: passing around loose tuples/dicts (x, y) or ("USD", 5) is
#   unclear and easy to mix up.
# - Idea: a small frozen dataclass: named fields, equality by value,
#   hashable, cannot be changed by accident.
# - Change = make a new copy with dataclasses.replace.
# - When NOT to use: objects with identity and a changing life (a User,
#   an Order) - those are entities, not value objects.
print("\n# Dataclass value objects")

@dataclass(frozen=True, order=True)
class Money:
    amount: int                        # cents, to avoid float errors
    currency: str = "USD"
    def __add__(self, other):
        if self.currency != other.currency:
            raise ValueError("currency mismatch")
        return Money(self.amount + other.amount, self.currency)

a, b = Money(500), Money(250)
print(a + b)
print(a == Money(500), a < Money(600))
print({a: "five dollars"}[Money(500)])      # hashable, usable as dict key
bigger = replace(a, amount=900)
print(a, bigger)
try:
    a.amount = 1
except Exception as e:
    print(type(e).__name__)
try:
    a + Money(1, "EUR")
except ValueError as e:
    print("ValueError:", e)

# 11. Anti-pattern: God Object
# ----------------------------
# - Problem: one huge class knows and does everything (users, emails,
#   reports, storage). Every change touches it; nothing can be tested alone.
# - Fix: split by responsibility (see SOLID: Single Responsibility).
# - Smell: class name ends in Manager/Handler/Utils and has 20+ methods.
# - When it's OK: a short script. Don't split what is only 15 lines.
print("\n# Anti-pattern: God Object")

class AppManagerBad:                   # does too much
    def __init__(self):
        self.users = []
    def add_user(self, name):
        self.users.append(name)
    def send_email(self, name):
        return f"mail to {name}"
    def build_report(self):
        return f"{len(self.users)} users"
    def save_to_disk(self):
        return "saved"

class UserBook:
    def __init__(self):
        self.users = []
    def add(self, name):
        self.users.append(name)

class EmailService:
    def send(self, name):
        return f"mail to {name}"

def user_report(book):
    return f"{len(book.users)} users"

book = UserBook()
book.add("ana")
print(EmailService().send("ana"), "|", user_report(book))

# 12. Anti-pattern: Mutable default arguments
# ----------------------------
# - Problem: a default value like [] or {} is created ONCE when the
#   function is defined, then shared by every call.
# - Fix: default to None and create the new object inside.
# - When it's OK: immutable defaults (numbers, strings, tuples, None).
print("\n# Anti-pattern: mutable default argument")

def add_item_bad(item, bucket=[]):
    bucket.append(item)
    return bucket

print(add_item_bad("a"))
print(add_item_bad("b"))               # surprise: still has "a"

def add_item(item, bucket=None):
    if bucket is None:
        bucket = []
    bucket.append(item)
    return bucket

print(add_item("a"))
print(add_item("b"))

@dataclass
class Cart:
    items: list = field(default_factory=list)   # dataclass guards this for you

c1, c2 = Cart(), Cart()
c1.items.append("x")
print(c1.items, c2.items)

# 13. Anti-pattern: Over-using inheritance
# ----------------------------
# - Problem: inheriting just to reuse code creates tight coupling and
#   weird "is-a" lies (a Stack is not a list).
# - Fix: composition ("has-a"): hold the helper as an attribute and
#   expose only what you want.
# - Test: can you say "X is a kind of Y" truthfully in every case?
# - When inheritance IS fine: real is-a relationships, ABCs, mixins with a
#   clear single job.
print("\n# Anti-pattern: inheritance for reuse")

class StackBad(list):                  # exposes insert(), sort(), etc.
    def push(self, x):
        self.append(x)

s_bad = StackBad()
s_bad.push(1)
s_bad.push(2)
s_bad.insert(0, 99)                    # breaks stack rules!
print(list(s_bad))

class Stack:                           # composition: small, honest API
    def __init__(self):
        self._items = []
    def push(self, x):
        self._items.append(x)
    def pop(self):
        return self._items.pop()
    def __len__(self):
        return len(self._items)

s = Stack()
s.push(1)
s.push(2)
print(s.pop(), len(s), hasattr(s, "insert"))

# 14. Anti-pattern: Java-style getters and setters
# ----------------------------
# - Problem: get_x()/set_x() for every field is noise. Python attributes
#   are public by default and can be upgraded later.
# - Fix: use a plain attribute. If you later need validation, switch to
#   @property - callers don't change.
# - When NOT to avoid: a property is right when you must validate,
#   compute, or keep two fields in sync.
print("\n# Anti-pattern: getters and setters")

class PersonBad:
    def __init__(self, name):
        self._name = name
    def get_name(self):
        return self._name
    def set_name(self, v):
        self._name = v

class Person:
    def __init__(self, name):
        self.name = name               # plain attribute

class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius         # goes through the setter below
    @property
    def celsius(self):
        return self._celsius
    @celsius.setter
    def celsius(self, value):
        if value < -273.15:
            raise ValueError("below absolute zero")
        self._celsius = value
    @property
    def fahrenheit(self):              # computed, read-only
        return self._celsius * 9 / 5 + 32

p = Person("ana")
p.name = "anna"
print(p.name)
t = Temperature(100)
print(t.celsius, t.fahrenheit)
try:
    t.celsius = -500
except ValueError as e:
    print("ValueError:", e)

# 15. Anti-pattern: Singleton abuse
# ----------------------------
# - Problem: singletons are global state in disguise: hidden dependencies,
#   tests that affect each other, hard to replace.
# - Python already gives you one: a module is created once per process.
#   So a module-level object IS a singleton, with no class tricks.
# - Better still: create one object and inject it (section 04).
# - When it's OK: truly process-wide resources (a logger, a config loaded once).
print("\n# Anti-pattern: singleton abuse")

class SettingsBad:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.debug = False
        return cls._instance

x, y = SettingsBad(), SettingsBad()
x.debug = True
print("y.debug:", y.debug, "(changed through x!)")

# Module-level object style: create one, pass it around
@dataclass
class Settings:
    debug: bool = False

def run_app(settings):
    return "debug mode" if settings.debug else "normal mode"

print(run_app(Settings()), "|", run_app(Settings(debug=True)))   # each test gets its own

# 16. Anti-pattern: Premature abstraction
# ----------------------------
# - Problem: building interfaces, factories, and layers for variations that
#   do not exist yet. More code, more places for bugs, harder to read.
# - Rule of three: copy once, copy twice, abstract on the third.
#   Wrong abstraction costs more than duplication.
# - YAGNI = You Aren't Gonna Need It.
# - When abstraction IS right: you already have 2-3 real variants, or the
#   boundary is an external system you must be able to swap or fake.
print("\n# Anti-pattern: premature abstraction")

class GreeterFactoryBad:               # 3 classes to say hello
    def create(self):
        return GreeterBad()

class GreeterBad:
    def greet(self, name):
        return f"hello {name}"

print(GreeterFactoryBad().create().greet("ana"))

def hello(name):                       # same result
    return f"hello {name}"

print(hello("ana"))

# 17. Anti-pattern: Stringly-typed code
# ----------------------------
# - Problem: using raw strings ("pending", "shipped") for fixed choices.
#   One typo ("shiped") silently breaks logic; tools can't help.
# - Fix: Enum for fixed choices; dataclass or TypedDict for records
#   instead of dicts with magic keys.
# - When strings are fine: free text, or data crossing a boundary
#   (JSON) - convert to Enum at the edge.
print("\n# Anti-pattern: stringly-typed code")

def can_cancel_bad(status):
    return status == "pending" or status == "paid"

print(can_cancel_bad("shiped"), "<- typo, no error, wrong answer")

class Status(Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"

def can_cancel(status: Status):
    return status in (Status.PENDING, Status.PAID)

print(can_cancel(Status.SHIPPED), can_cancel(Status("pending")))
try:
    Status("shiped")                   # typo fails loudly at the edge
except ValueError as e:
    print("ValueError:", e)

# 18. Code smell cheat sheet
# ----------------------------
# - A smell is a hint, not a bug: look closer, don't panic.
# - Long function ........ split into small named functions
# - Big class ............ split by responsibility (god object)
# - Deep nesting ......... early return / guard clauses
# - Duplicate code ....... extract a function (after the 3rd copy)
# - Many parameters ...... group into a dataclass
# - Magic numbers ........ named constants / Enum
# - Boolean flag params .. two functions, or an Enum
# - Bare except .......... catch the specific error
# - Mutable defaults ..... None + create inside
# - Comments explaining bad names .. rename instead
# - isinstance chains .... polymorphism, singledispatch, match
# - Global state ......... pass it in (dependency injection)
print("\n# Code smell cheat sheet")

SMELLS = [
    ("Long function", "split into named helpers"),
    ("Deep nesting", "guard clauses / early return"),
    ("Many parameters", "group into a dataclass"),
    ("Magic numbers", "named constants or Enum"),
    ("Boolean flag argument", "two functions or an Enum"),
    ("Bare except", "catch the specific error"),
    ("isinstance chain", "singledispatch / match / polymorphism"),
    ("Global state", "inject it"),
]
for smell, fix in SMELLS:
    print(f"{smell:22} => {fix}")

# 19. Refactor: before and after
# ----------------------------
# - Take one messy function and apply the smells above step by step.
# - Behavior stays the same; only the shape improves.
# - Always keep a quick check (here: assert) so you know nothing broke.
print("\n# Refactor before / after")

def process_bad(o, t):                 # unclear names, magic numbers, nesting
    if o is not None:
        if len(o) > 0:
            tot = 0
            for i in o:
                tot = tot + i["p"] * i["q"]
            if t == "vip":
                tot = tot * 0.8
            elif t == "new":
                tot = tot * 0.95
            if tot > 100:
                tot = tot - 10
            return tot
        else:
            return 0
    else:
        return 0

class Tier(Enum):
    VIP = 0.80
    NEW = 0.95
    REGULAR = 1.0

BULK_THRESHOLD = 100
BULK_BONUS = 10

@dataclass(frozen=True)
class Line:
    price: float
    qty: int

def subtotal(lines):
    return sum(line.price * line.qty for line in lines)

def order_total(lines, tier=Tier.REGULAR):
    if not lines:                      # guard clause replaces nesting
        return 0
    total = subtotal(lines) * tier.value
    if total > BULK_THRESHOLD:
        total -= BULK_BONUS
    return total

old_items = [{"p": 50, "q": 2}, {"p": 20, "q": 1}]
new_items = [Line(50, 2), Line(20, 1)]
before = process_bad(old_items, "vip")
after = order_total(new_items, Tier.VIP)
print("before:", before, "| after:", after)
assert abs(before - after) < 1e-9
assert process_bad([], "vip") == order_total([], Tier.VIP) == 0
print("same behavior, clearer code")
