from abc import ABC, abstractmethod
from functools import singledispatch
from dataclasses import dataclass, field
from typing import Callable, Iterator

# 01. Behavioral Design Patterns - Introduction
# ----------------------------
# - Behavioral patterns are about HOW objects talk to each other and share work.
# - Creational = how objects get made. Structural = how objects are glued together.
#   Behavioral = how objects behave and communicate at run time.
# - Python has first-class functions, generators, and duck typing, so many classic
#   (Java-style) patterns shrink to a function, a dict, or a generator.
# - Each section below has: the problem, when NOT to use it, and a small demo.
# - Rule of thumb: reach for the pattern only when the simple version hurts.

# 02. Strategy (class version)
# ----------------------------
# - Problem: you have several ways to do one job (pricing, sorting, shipping)
#   and want to swap them without a giant if/elif chain.
# - Idea: put each way in its own object with the same method name.
# - When NOT to use: only one or two variants that never change. A plain
#   if/else is clearer.
print("\n# Strategy - class version")

class PriceRule(ABC):
    @abstractmethod
    def apply(self, amount):
        ...

class NoDiscount(PriceRule):
    def apply(self, amount):
        return amount

class PercentOff(PriceRule):
    def __init__(self, percent):
        self.percent = percent
    def apply(self, amount):
        return amount * (100 - self.percent) / 100

class FlatOff(PriceRule):
    def __init__(self, flat):
        self.flat = flat
    def apply(self, amount):
        return max(0, amount - self.flat)

class Checkout:
    def __init__(self, rule: PriceRule):
        self.rule = rule
    def total(self, amount):
        return self.rule.apply(amount)

for rule in (NoDiscount(), PercentOff(10), FlatOff(30)):
    print(type(rule).__name__, "->", Checkout(rule).total(200))

# 03. Strategy (plain function version - the Pythonic way)
# ----------------------------
# - Problem: the class version is a lot of ceremony when each strategy is
#   one tiny method.
# - Python: functions are objects. Pass the function itself.
# - Use a class only when the strategy needs its own state or several methods.
# - When NOT to use: if strategies must remember config, use a class or
#   functools.partial / closure instead of globals.
print("\n# Strategy - plain functions")

def no_discount(amount):
    return amount

def percent_off(percent):          # a closure builds a configured strategy
    return lambda amount: amount * (100 - percent) / 100

def checkout(amount, rule=no_discount):
    return rule(amount)

print(checkout(200))
print(checkout(200, percent_off(25)))
print(checkout(200, lambda a: a - 5))

# Built-ins use this pattern everywhere: key= is a strategy
words = ["pear", "fig", "banana"]
print(sorted(words, key=len))
print(sorted(words, key=lambda w: w[-1]))

# A dict of strategies replaces if/elif and is easy to extend
STRATEGIES = {"none": no_discount, "ten": percent_off(10)}
print(STRATEGIES["ten"](100))

# 04. Observer / Event Emitter
# ----------------------------
# - Problem: when one thing changes, several other things must react,
#   but you don't want the source to know about each of them.
# - Idea: the source keeps a list of callbacks; subscribers register.
# - Pythonic: callbacks are just callables (functions, bound methods).
# - When NOT to use: one listener only (call it directly), or when order
#   and error handling between listeners really matter - hidden control flow
#   gets hard to debug.
print("\n# Observer / event emitter")

class EventEmitter:
    def __init__(self):
        self._handlers = {}
    def on(self, event, handler=None):
        if handler is None:                  # used as @bus.on("event")
            return lambda fn: self.on(event, fn)
        self._handlers.setdefault(event, []).append(handler)
        return handler
    def off(self, event, handler):
        self._handlers[event].remove(handler)
    def emit(self, event, *args):
        for handler in list(self._handlers.get(event, [])):  # copy: safe if a handler unsubscribes
            handler(*args)

bus = EventEmitter()

@bus.on("order_placed")
def send_email(order_id):
    print("email sent for order", order_id)

def update_stock(order_id):
    print("stock updated for order", order_id)

bus.on("order_placed", update_stock)
bus.emit("order_placed", 101)
bus.off("order_placed", send_email)
bus.emit("order_placed", 102)
bus.emit("nobody_listens")                    # no handlers: silently fine
print("done")

# 05. Command (with undo)
# ----------------------------
# - Problem: you want to treat an action as data - queue it, log it, undo it.
# - Idea: wrap each action as an object with execute() and undo().
# - Keep a history stack; undo pops the last command.
# - Pythonic: for fire-and-forget actions a function or functools.partial is
#   enough. You only need a class when you need undo or extra state.
# - When NOT to use: simple actions that never need undo or queuing.
print("\n# Command with undo")

class Editor:
    def __init__(self):
        self.text = ""

class Append:
    def __init__(self, editor, chunk):
        self.editor, self.chunk = editor, chunk
    def execute(self):
        self.editor.text += self.chunk
    def undo(self):
        self.editor.text = self.editor.text[:-len(self.chunk)]

class History:
    def __init__(self):
        self._done = []
    def run(self, command):
        command.execute()
        self._done.append(command)
    def undo(self):
        if self._done:
            self._done.pop().undo()

ed, hist = Editor(), History()
hist.run(Append(ed, "Hello"))
hist.run(Append(ed, ", world"))
print(repr(ed.text))
hist.undo()
print(repr(ed.text))
hist.undo()
hist.undo()                                    # extra undo is harmless
print(repr(ed.text))

# Without undo, a command is just a callable:
from functools import partial
queue = [partial(print, "task", 1), partial(print, "task", 2)]
for job in queue:
    job()

# 06. State
# ----------------------------
# - Problem: an object behaves differently depending on its mode, and the
#   code is full of "if self.state == ..." checks.
# - Idea: each state is its own object that knows what the next step is.
# - Pythonic: for simple machines a dict of {(state, event): next_state} is
#   shorter and easy to read.
# - When NOT to use: two or three states with trivial rules - a dict or
#   Enum is enough.
print("\n# State")

class Door:
    def __init__(self):
        self.state = ClosedState()
    def push(self):
        self.state = self.state.push()
        print("door is now", self.state.name)

class ClosedState:
    name = "closed"
    def push(self):
        return OpenState()

class OpenState:
    name = "open"
    def push(self):
        return ClosedState()

door = Door()
door.push()
door.push()

# Table-driven alternative
TRANSITIONS = {
    ("idle", "start"): "running",
    ("running", "pause"): "paused",
    ("paused", "start"): "running",
    ("running", "stop"): "idle",
}

def step(state, event):
    # invalid events keep the same state instead of crashing
    return TRANSITIONS.get((state, event), state)

s = "idle"
for ev in ["start", "pause", "stop", "start", "stop"]:
    s = step(s, ev)
    print(f"after {ev:5} -> {s}")

# 07. Template Method
# ----------------------------
# - Problem: several workflows share the same steps in the same order, but
#   a few steps differ.
# - Idea: the base class fixes the skeleton in one method; subclasses fill
#   in the blanks (hooks).
# - Pythonic: if only one step differs, pass a function instead of
#   subclassing.
# - When NOT to use: deep inheritance chains; prefer passing callables
#   (composition) so you don't get locked into a hierarchy.
print("\n# Template Method")

class Report(ABC):
    def build(self):                   # the template: do NOT override
        lines = [self.header()]
        lines += [self.format_row(r) for r in self.rows()]
        lines.append(self.footer())
        return "\n".join(lines)
    @abstractmethod
    def rows(self):
        ...
    @abstractmethod
    def format_row(self, row):
        ...
    def header(self):                  # optional hook with a default
        return "== report =="
    def footer(self):
        return "== end =="

class SalesReport(Report):
    def rows(self):
        return [("tea", 3), ("jam", 5)]
    def format_row(self, row):
        return f"{row[0]}: {row[1]} sold"

print(SalesReport().build())

# Function version: pass the one varying step
def build_report(rows, fmt):
    return "\n".join(fmt(r) for r in rows)

print(build_report([1, 2, 3], lambda n: f"item #{n}"))

# 08. Iterator
# ----------------------------
# - Problem: loop over a collection without exposing how it is stored.
# - Python already has the pattern built in: __iter__ / __next__, and for loops.
# - Pythonic: write a generator (yield) instead of a class with __next__.
# - When NOT to use: if a list already does the job, just return the list.
#   Use generators for big or endless data (lazy, low memory).
print("\n# Iterator")

class Countdown:                       # the long way: explicit iterator
    def __init__(self, start):
        self.current = start
    def __iter__(self):
        return self
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

print(list(Countdown(3)))

def countdown(start):                  # the Pythonic way
    while start > 0:
        yield start
        start -= 1

print(list(countdown(3)))

class Playlist:                        # container with a generator __iter__
    def __init__(self, *songs):
        self.songs = songs
    def __iter__(self) -> Iterator[str]:
        yield from self.songs
    def reversed_songs(self):
        yield from reversed(self.songs)

pl = Playlist("a", "b", "c")
print(list(pl), list(pl.reversed_songs()))   # can loop many times

gen = countdown(2)
print(list(gen), list(gen))                   # a generator is used up after one pass

# 09. Chain of Responsibility
# ----------------------------
# - Problem: a request must pass through several checks/handlers, and each
#   decides to handle it or pass it on.
# - Idea: link handlers; each either answers or forwards.
# - Pythonic: a plain list of functions and a loop (like middleware).
# - When NOT to use: when every step must always run (that is a pipeline),
#   or the order is fixed and short - just call them in sequence.
print("\n# Chain of Responsibility")

def check_auth(req):
    if not req.get("user"):
        return "401 login required"

def check_admin(req):
    if req.get("path", "").startswith("/admin") and not req.get("is_admin"):
        return "403 admins only"

def serve(req):
    return f"200 page {req['path']}"

CHAIN = [check_auth, check_admin]

def handle(req):
    for step_fn in CHAIN:
        result = step_fn(req)          # a non-None result stops the chain
        if result is not None:
            return result
    return serve(req)

print(handle({"path": "/home"}))
print(handle({"path": "/admin", "user": "ana"}))
print(handle({"path": "/admin", "user": "ana", "is_admin": True}))

# 10. Visitor (classic double dispatch)
# ----------------------------
# - Problem: you want to add new operations to a family of classes without
#   editing each class every time.
# - Idea: classes have accept(visitor); the visitor has one method per class.
# - Cost: every new class means touching every visitor. Fine when the
#   classes are stable and operations keep growing.
# - When NOT to use: if the class family changes often, or isinstance/
#   match is enough.
print("\n# Visitor - classic")

class Num:
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        return visitor.visit_num(self)

class Add:
    def __init__(self, left, right):
        self.left, self.right = left, right
    def accept(self, visitor):
        return visitor.visit_add(self)

class Evaluator:
    def visit_num(self, node):
        return node.value
    def visit_add(self, node):
        return node.left.accept(self) + node.right.accept(self)

class Printer:
    def visit_num(self, node):
        return str(node.value)
    def visit_add(self, node):
        return f"({node.left.accept(self)} + {node.right.accept(self)})"

tree = Add(Num(1), Add(Num(2), Num(3)))
print(tree.accept(Printer()), "=", tree.accept(Evaluator()))

# 11. Visitor with functools.singledispatch
# ----------------------------
# - Pythonic: singledispatch picks the function by the type of the first
#   argument. No accept() methods needed, and you can add support for
#   classes you do not own.
# - Register new types from anywhere (even another module).
# - When NOT to use: dispatch on more than one argument (singledispatch
#   only looks at the first), or when a normal method does the job.
print("\n# Visitor - singledispatch")

@dataclass
class Circle:
    r: float

@dataclass
class Rect:
    w: float
    h: float

@singledispatch
def area(shape):
    raise TypeError(f"no area for {type(shape).__name__}")

@area.register
def _(shape: Circle):
    return round(3.14159 * shape.r ** 2, 2)

@area.register
def _(shape: Rect):
    return shape.w * shape.h

print(area(Circle(2)), area(Rect(3, 4)))
try:
    area("not a shape")
except TypeError as e:
    print("TypeError:", e)

# Python 3.10+ match is another lightweight option
def describe(shape):
    match shape:
        case Circle(r=r):
            return f"circle radius {r}"
        case Rect(w=w, h=h):
            return f"rect {w}x{h}"
        case _:
            return "unknown"

print(describe(Circle(1)), "|", describe(Rect(2, 5)))

# 12. Mediator
# ----------------------------
# - Problem: many objects talk to each other directly, so everyone knows
#   everyone (a tangled web).
# - Idea: objects only talk to one hub; the hub routes messages.
# - Observer vs Mediator: Observer = one source, many listeners.
#   Mediator = many-to-many through a central coordinator.
# - When NOT to use: two objects only, or when the hub becomes a god object
#   that holds all the logic.
print("\n# Mediator")

class ChatRoom:
    def __init__(self):
        self.users = {}
    def join(self, user):
        self.users[user.name] = user
        user.room = self
    def send(self, sender, text):
        for name, user in self.users.items():
            if name != sender.name:
                user.receive(sender.name, text)

class User:
    def __init__(self, name):
        self.name, self.room = name, None
    def say(self, text):
        self.room.send(self, text)
    def receive(self, from_name, text):
        print(f"[{self.name} got] {from_name}: {text}")

room = ChatRoom()
ana, bo, cy = User("ana"), User("bo"), User("cy")
for u in (ana, bo, cy):
    room.join(u)
ana.say("hi all")

# 13. Memento (snapshot and restore)
# ----------------------------
# - Problem: you want to save an object's state and roll back later,
#   without breaking encapsulation.
# - Idea: the object produces an opaque snapshot; a caretaker stores them.
# - Pythonic: a frozen dataclass as the snapshot, or copy.deepcopy.
# - When NOT to use: huge state (snapshots cost memory) - store diffs
#   (Command + undo) instead.
print("\n# Memento")

@dataclass(frozen=True)
class Snapshot:
    text: str
    cursor: int

class Doc:
    def __init__(self):
        self.text, self.cursor = "", 0
    def type(self, chunk):
        self.text += chunk
        self.cursor = len(self.text)
    def save(self):
        return Snapshot(self.text, self.cursor)
    def restore(self, snap):
        self.text, self.cursor = snap.text, snap.cursor

doc, saves = Doc(), []
doc.type("one")
saves.append(doc.save())
doc.type(" two")
saves.append(doc.save())
doc.type(" three")
print(doc.text)
doc.restore(saves[-1])
print(doc.text)
doc.restore(saves[0])
print(doc.text, doc.cursor)

# Snapshots must not share mutable inner objects with the live object
import copy
state = {"items": [1, 2]}
shallow = dict(state)
deep = copy.deepcopy(state)
state["items"].append(3)
print("shallow sees change:", shallow["items"], "| deep is safe:", deep["items"])

# 14. Null Object
# ----------------------------
# - Problem: code is littered with "if logger is not None:" checks.
# - Idea: pass an object that has the same methods but does nothing.
# - The caller never checks; it just calls.
# - When NOT to use: when "nothing here" is an error you must notice.
#   A silent do-nothing object can hide bugs - fail loudly instead.
print("\n# Null Object")

class ConsoleLogger:
    def log(self, msg):
        print("LOG:", msg)

class NullLogger:
    def log(self, msg):
        pass

def work(logger):
    logger.log("starting")
    result = 6 * 7
    logger.log(f"result {result}")
    return result

print(work(ConsoleLogger()))
print(work(NullLogger()))              # no checks inside work()

# Stdlib has null objects too
from contextlib import nullcontext
with nullcontext():
    print("nullcontext does nothing, still a valid 'with'")

# 15. Pythonic alternatives - cheat sheet
# ----------------------------
# - Strategy              -> pass a function (key=, callbacks, dict of funcs)
# - Observer              -> list of callables, or signals/event libs
# - Command               -> callable / functools.partial (class only for undo)
# - State                 -> dict transition table or Enum
# - Template Method       -> pass the varying step as a function
# - Iterator              -> generator function with yield
# - Chain of Responsib.   -> list of functions + loop (middleware)
# - Visitor               -> functools.singledispatch or match
# - Mediator              -> small event bus or a coordinator object
# - Memento               -> frozen dataclass / copy.deepcopy
# - Null Object           -> nullcontext, empty list, no-op function
print("\n# Cheat sheet in code")

ALTERNATIVES = {
    "Strategy": "function",
    "Observer": "list of callables",
    "Command": "partial / callable",
    "State": "dict table",
    "Template Method": "function argument",
    "Iterator": "generator",
    "Chain of Responsibility": "list of functions",
    "Visitor": "singledispatch",
    "Memento": "frozen dataclass",
    "Null Object": "no-op object",
}
for name, alt in ALTERNATIVES.items():
    print(f"{name:24}-> {alt}")

# 16. Choosing a pattern (and when to skip all of them)
# ----------------------------
# - Start with the simplest code: a function, a dict, a loop.
# - Add a pattern when you feel real pain: repeated if/elif, tangled calls,
#   need for undo, need to extend without editing old code.
# - Patterns are a shared vocabulary. Saying "this is an Observer" saves
#   a paragraph of explanation.
# - Too many patterns = too many tiny classes = harder to read.
print("\n# Quick decision guide")

GUIDE = [
    ("Many ways to do one job", "Strategy"),
    ("Tell many parties something happened", "Observer"),
    ("Need undo / queue of actions", "Command"),
    ("Behavior changes with mode", "State"),
    ("Same steps, one step differs", "Template Method"),
    ("Walk through data lazily", "Iterator"),
    ("Request passes several handlers", "Chain of Responsibility"),
    ("New operations on stable classes", "Visitor"),
    ("Many objects talk to many", "Mediator"),
    ("Save and restore state", "Memento"),
    ("Avoid None checks", "Null Object"),
]
for need, pattern in GUIDE:
    print(f"{need:38} -> {pattern}")
