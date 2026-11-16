import sys
import gc
import copy
import pickle
import weakref
import contextlib

# 01. The Object Lifecycle at a Glance
# ------------------------------------
# - Birth:  Class(...) calls type.__call__, which runs __new__ (create) then __init__ (fill in).
# - Life:   the object lives while at least one reference points to it.
# - Death:  when the last reference goes away, Python frees it; __del__ runs just before.
# - Copying and pickling are "birth by other means": they build a new object from an old one
#   and they SKIP __init__ by default (see sections 11-13).
# - Basics of classes and __init__: see 01-Class-Object.py. Dunder basics: 06-Dataclasses-And-Operator-Overloading.py.
class Trace:
    def __new__(cls, name):
        print(f"   __new__({name!r}) -> make the empty object")
        return super().__new__(cls)
    def __init__(self, name):
        print(f"   __init__({name!r}) -> fill in the fields")
        self.name = name
    def __del__(self):
        print(f"   __del__ -> {self.name} is going away")

print("create:")
t = Trace("alpha")
print("delete the only reference:")
del t
print("done")

# 02. __new__ vs __init__
# ------------------------------------
# - __new__(cls, ...) is a static-like method that RETURNS the new object. __init__(self, ...) just fills it.
# - Use __new__ only when you must control creation: singletons, caching/interning, immutable subclasses
#   (int, str, tuple - they are fixed at creation so __init__ is too late).
# - If __new__ returns an object that is NOT an instance of cls, __init__ is skipped.
class Celsius(float):
    """Immutable subclass: the value must be set in __new__, __init__ is too late."""
    def __new__(cls, degrees):
        if degrees < -273.15:
            raise ValueError("below absolute zero")
        return super().__new__(cls, degrees)

print("\n# 02. __new__ vs __init__")
c = Celsius(36.6)
print("Celsius(36.6) + 1 =", c + 1, "| type of c:", type(c).__name__)
try:
    Celsius(-300)
except ValueError as e:
    print("Celsius(-300) ->", e)

class Weird:
    def __new__(cls):
        return 42            # not a Weird instance
    def __init__(self):
        print("never printed")
print("Weird() returns:", Weird(), "(__init__ was skipped)")

# 03. Singleton and Instance Cache with __new__
# ------------------------------------
# - Classic uses of __new__: hand back an existing object instead of making a new one.
# - GOTCHA: __init__ still runs on EVERY call, even when __new__ returns the old object, so it
#   re-initialises the shared state. Guard it or keep __init__ empty.
class Config:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.loaded = 0
        return cls._instance
    def __init__(self):
        self.loaded += 1       # runs on every Config() call

print("\n# 03. Singleton and Instance Cache with __new__")
a, b = Config(), Config()
print("a is b:", a is b, "| __init__ ran", a.loaded, "times on the one object")

class Color:
    """Flyweight: one object per distinct name."""
    _cache = {}
    def __new__(cls, name):
        if name not in cls._cache:
            obj = super().__new__(cls)
            obj.name = name
            cls._cache[name] = obj
        return cls._cache[name]

print("Color('red') is Color('red'):", Color("red") is Color("red"))
print("Color('red') is Color('blue'):", Color("red") is Color("blue"))

# 04. Reference Counting
# ------------------------------------
# - CPython counts how many references each object has. At 0 it is freed immediately and
#   predictably. This is why __del__ above fired right at `del t`.
# - sys.getrefcount(x) is always 1 higher than you expect, because passing x as the argument
#   is itself a temporary reference.
# - Other Pythons (PyPy, etc.) do NOT free instantly, so never depend on timing for correctness.
class Box:
    pass

print("\n# 04. Reference Counting")
x = Box()
base = sys.getrefcount(x)
y = x
print("after y = x          : +", sys.getrefcount(x) - base)
holder = [x]
print("after holder = [x]   : +", sys.getrefcount(x) - base)
del y
print("after del y          : +", sys.getrefcount(x) - base)
holder.clear()
print("after holder.clear() : +", sys.getrefcount(x) - base)

# 05. Cycles and the Garbage Collector
# ------------------------------------
# - Two objects pointing at each other never reach refcount 0, even after you drop your names.
# - The cyclic garbage collector (module gc) finds and frees these unreachable cycles.
# - Since Python 3.4 (PEP 442) objects with __del__ in a cycle are collected fine too; before that they leaked.
# - gc.collect() forces a run and returns how many unreachable objects it found.
class Node:
    def __init__(self, name):
        self.name = name
        self.other = None
    def __del__(self):
        print(f"   __del__ {self.name}")

print("\n# 05. Cycles and the Garbage Collector")
gc.disable()                      # keep the demo deterministic
n1, n2 = Node("n1"), Node("n2")
n1.other, n2.other = n2, n1
del n1, n2
print("names deleted, but nothing freed yet (cycle keeps them alive)")
found = gc.collect()
print("gc.collect() found something:", found > 0)
gc.enable()

# 06. weakref - Reference Without Keeping Alive
# ------------------------------------
# - weakref.ref(obj) does not raise the refcount. Call it to get the object, or None if it died.
# - Perfect for caches, observers and parent back-pointers (avoids cycles from section 5).
# - GOTCHA: plain int, str, tuple, list, dict cannot be weak-referenced. Your own classes can,
#   unless they define __slots__ without a '__weakref__' slot (see section 16).
print("\n# 06. weakref - Reference Without Keeping Alive")
class Thing:
    def __init__(self, name):
        self.name = name

obj = Thing("thing")
r = weakref.ref(obj)
print("alive      ->", r().name)
del obj
print("after del  ->", r())
try:
    weakref.ref([1, 2])
except TypeError as e:
    print("weakref.ref(list) ->", e)

# 07. WeakValueDictionary, WeakSet and finalize
# ------------------------------------
# - WeakValueDictionary: a cache whose entries vanish automatically once nobody else holds the value.
# - WeakKeyDictionary / WeakSet: same idea for keys / set members.
# - weakref.finalize(obj, func, *args): run a cleanup callback when obj dies. It is the safe
#   replacement for __del__ (section 9): it does not touch obj, runs at most once, and also
#   fires at interpreter exit unless you set .atexit = False.
print("\n# 07. WeakValueDictionary, WeakSet and finalize")
cache = weakref.WeakValueDictionary()
img = Thing("big-image")
cache["img"] = img
print("cached      :", "img" in cache, "| size", len(cache))
del img
print("after del   :", "img" in cache, "| size", len(cache))

seen = weakref.WeakSet()
w = Thing("w")
seen.add(w)
print("WeakSet size:", len(seen))
del w
print("WeakSet size after del:", len(seen))

res = Thing("socket")
fin = weakref.finalize(res, print, "   finalize callback: closing the socket")
print("fin.alive:", fin.alive)
del res
print("fin.alive:", fin.alive)
keep = Thing("x")
fin2 = weakref.finalize(keep, print, "never shown")
fin2.detach()
print("detach() cancels a finalizer; fin2.alive:", fin2.alive)

# 08. Copy: Assignment vs Shallow vs Deep
# ------------------------------------
# - b = a              -> NOT a copy, just a second name for the same object.
# - copy.copy(a)       -> shallow: new outer object, SAME inner objects.
# - copy.deepcopy(a)   -> deep: new outer AND new inner objects, all the way down.
# - Mutating a shared inner object through one copy shows up in the other. Classic bug.
# - Containers' own copies (list.copy(), d.copy(), a[:]) are shallow too.
class Team:
    def __init__(self, name, members):
        self.name = name
        self.members = members

print("\n# 08. Copy: Assignment vs Shallow vs Deep")
orig = Team("core", ["ann", "bob"])
alias = orig
shallow = copy.copy(orig)
deep = copy.deepcopy(orig)
orig.members.append("cy")
orig.name = "renamed"
print("orig     :", orig.name, orig.members)
print("alias    :", alias.name, alias.members, "| same object:", alias is orig)
print("shallow  :", shallow.name, shallow.members, "| shares list:", shallow.members is orig.members)
print("deep     :", deep.name, deep.members, "| shares list:", deep.members is orig.members)

# 09. __del__ - What It Is and Why to Be Careful
# ------------------------------------
# - __del__ is a finalizer: called once when the object is about to be destroyed. It is NOT a destructor in the C++ sense.
# - `del obj` does NOT call __del__. It only removes a name; __del__ runs when the LAST reference is gone.
# - Gotchas:
#   * Timing is not guaranteed (cycles, other interpreters, exit time). Never use it for must-happen cleanup.
#   * Exceptions inside __del__ are printed to stderr and IGNORED. They never reach your code.
#   * If __init__ raised, __del__ still runs on the half-built object, so attributes may be missing.
#   * It can "resurrect" the object by storing self somewhere (legal but a bad idea).
#   * At interpreter shutdown, globals may already be None, so __del__ can fail with odd errors.
# - Prefer: context managers (section 15) or weakref.finalize (section 7).
class Fragile:
    def __init__(self, fail):
        if fail:
            raise RuntimeError("init failed before self.handle was set")
        self.handle = "open"
    def __del__(self):
        # safe version: tolerate a half-built object
        print("   __del__ has handle:", hasattr(self, "handle"))

print("\n# 09. __del__ - What It Is and Why to Be Careful")
f1 = Fragile(False)
f2 = f1
del f1
print("del f1 did not call __del__ (f2 still refers to the object)")
del f2
try:
    Fragile(True)
except RuntimeError as e:
    print("Fragile(True) ->", e)

# 10. __repr__, __str__, __format__ Recap
# ------------------------------------
# - __repr__: for developers, unambiguous, ideally looks like code that rebuilds the object. Used in the REPL, lists, debugging.
# - __str__: for users, readable. print() and str() use it. If missing, Python falls back to __repr__ (not the reverse).
# - __format__(spec): used by f"{obj:spec}" and format(obj, spec). Default accepts only an empty spec.
# - !r / !s / !a in an f-string force repr / str / ascii. Containers always show their items with repr.
# - Rule of thumb: always write __repr__; add __str__ only when the friendly form differs.
# - More operator dunders: see 06-Dataclasses-And-Operator-Overloading.py.
class Money:
    def __init__(self, amount, cur="USD"):
        self.amount, self.cur = amount, cur
    def __repr__(self):
        return f"Money({self.amount!r}, {self.cur!r})"
    def __str__(self):
        return f"{self.amount:.2f} {self.cur}"
    def __format__(self, spec):
        if spec == "short":
            return f"{self.cur}{self.amount:g}"
        return format(str(self), spec)      # delegate other specs to the string

print("\n# 10. __repr__, __str__, __format__ Recap")
m = Money(5)
print("str      :", m)
print("repr     :", repr(m))
print("in a list:", [m])
print("f'{m:short}'  :", f"{m:short}")
print("f'{m:>12}'    :", f"{m:>12}|")
print("f'{m!r}'      :", f"{m!r}")

class OnlyRepr:
    def __repr__(self):
        return "OnlyRepr()"
print("str() falls back to repr:", str(OnlyRepr()))
try:
    f"{Thing('t'):>5}"
except TypeError as e:
    print("default __format__ with a spec ->", e)

# 11. Customising Copies: __copy__ and __deepcopy__
# ------------------------------------
# - copy.copy calls obj.__copy__() if it exists; copy.deepcopy calls obj.__deepcopy__(memo).
# - Use them to SKIP things that must not be copied (locks, connections, caches) or to share on purpose.
# - memo is a dict of already-copied objects (keyed by id). Pass it on when you deepcopy children,
#   so shared references and cycles are copied once and stay shared.
# - Neither __init__ is called by the default copy: the copy is rebuilt from the instance dict directly.
class Doc:
    def __init__(self, text, tags):
        self.text = text
        self.tags = tags
        self.cache = {"words": len(text.split())}      # derived data, not worth copying
    def __copy__(self):
        print("   __copy__ called")
        new = Doc(self.text, self.tags)                # shares tags on purpose
        return new
    def __deepcopy__(self, memo):
        print("   __deepcopy__ called")
        return Doc(self.text, copy.deepcopy(self.tags, memo))

print("\n# 11. Customising Copies: __copy__ and __deepcopy__")
d = Doc("hello big world", ["a"])
s = copy.copy(d)
dd = copy.deepcopy(d)
print("shallow shares tags:", s.tags is d.tags, "| deep shares tags:", dd.tags is d.tags)
print("derived cache shared with the original:", s.cache is d.cache)

# deepcopy keeps shared structure and survives cycles thanks to memo
shared = [1, 2]
pair = [shared, shared]
pair2 = copy.deepcopy(pair)
print("deepcopy keeps sharing:", pair2[0] is pair2[1], "| but not with original:", pair2[0] is shared)
loop = []
loop.append(loop)
loop2 = copy.deepcopy(loop)
print("cycle copied fine:", loop2[0] is loop2)

# 12. Copy Gotchas
# ------------------------------------
# - Immutable atoms (int, str, tuple of atoms, None) are returned as-is: copy.copy(n) is n. That is fine, they cannot change.
# - A tuple that CONTAINS a mutable is still shared by a shallow copy.
# - [[0]*3]*3 builds 3 references to ONE row. Use a comprehension for independent rows.
# - deepcopy of a huge graph is slow and can copy things you meant to share (a database handle).
# - Some objects refuse copying (locks, open files, generators): TypeError or pickling error.
# - Dataclasses (see 06-...py) can use dataclasses.replace(obj, field=...) to make a modified copy.
print("\n# 12. Copy Gotchas")
num = 12345
print("copy.copy(12345) is the same object:", copy.copy(num) is num)
tup = ([1], 2)
tup_copy = copy.copy(tup)
tup_copy[0].append(99)
print("tuple holding a list, shallow copied:", tup)
grid = [[0] * 2] * 2
grid[0][0] = 1
print("[[0]*2]*2 then grid[0][0]=1 ->", grid, "(rows are the same list!)")
grid = [[0] * 2 for _ in range(2)]
grid[0][0] = 1
print("comprehension version        ->", grid)
import threading
try:
    copy.deepcopy(threading.Lock())
except TypeError as e:
    print("deepcopy(Lock) ->", e)

# 13. Pickle Basics
# ------------------------------------
# - pickle turns (almost) any Python object into bytes, and back. dumps/loads work on bytes; dump/load on files.
# - Unpickling does NOT call __init__. It creates the object with __new__ and restores __dict__ directly.
# - Pickle stores the CLASS BY NAME (module + qualname), not its code. The class must be importable when loading.
# - Works: numbers, str, list, dict, set, your classes, functions/classes defined at module top level.
# - Fails: lambdas, nested/local functions and classes, open files, locks, generators.
# - SECURITY: never unpickle data you do not trust. Loading can run arbitrary code. For data exchange use json
#   (see 07-Custom-Containers-And-ABCs.py for json use).
class Player:
    def __init__(self, name, score):
        print("   Player.__init__ called")
        self.name, self.score = name, score
    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"

print("\n# 13. Pickle Basics")
p = Player("zed", 10)
blob = pickle.dumps(p)
print("pickled to bytes:", isinstance(blob, bytes))
p2 = pickle.loads(blob)
print("loaded:", p2, "| equal object?", p2 is p, "(no __init__ ran on load)")
try:
    pickle.dumps(lambda: 1)
except (pickle.PicklingError, AttributeError) as e:
    print("pickle lambda ->", type(e).__name__)
try:
    pickle.dumps(threading.Lock())
except TypeError as e:
    print("pickle Lock ->", e)

# 14. __getstate__ and __setstate__
# ------------------------------------
# - __getstate__() returns what to pickle (default: the instance __dict__). Drop unpicklable or derived fields here.
# - __setstate__(state) receives that value on load and rebuilds the object. Re-create dropped fields here.
# - The SAME pair is used by copy.copy / copy.deepcopy when you do not define __copy__/__deepcopy__.
# - Great for versioning: store a "version" in the state and upgrade old data in __setstate__.
# - GOTCHA: __setstate__ is skipped when __getstate__ returns a falsy value (like {}) before Python 3.11.
#   Return a non-empty dict to be safe on older versions.
class Connection:
    def __init__(self, host):
        self.host = host
        self.lock = threading.Lock()      # cannot be pickled
        self.opened = 0
    def __getstate__(self):
        state = self.__dict__.copy()
        del state["lock"]
        state["_v"] = 2
        return state
    def __setstate__(self, state):
        version = state.pop("_v", 1)
        if version < 2:
            state["opened"] = 0           # upgrade path for old data
        self.__dict__.update(state)
        self.lock = threading.Lock()      # rebuild what we dropped

print("\n# 14. __getstate__ and __setstate__")
cn = Connection("db.local")
cn.opened = 3
cn2 = pickle.loads(pickle.dumps(cn))
print("round trip:", cn2.host, cn2.opened, "| fresh lock:", cn2.lock is not cn.lock)
cn3 = copy.deepcopy(cn)
print("deepcopy uses the same hooks:", cn3.host, cn3.opened)

# 15. __reduce__ - Full Control of Pickling
# ------------------------------------
# - __reduce__() returns (callable, args) or (callable, args, state, ...). On load Python calls callable(*args)
#   to build the object. This is the lowest-level hook; __getstate__ is the friendly one.
# - Use it when the object must be rebuilt through a constructor (so __init__ DOES run), or for custom factories.
# - Prefer __reduce_ex__(protocol) only if you need protocol-specific behaviour.
# - SECURITY link: a malicious __reduce__ can return (os.system, ("cmd",)). That is exactly why untrusted pickles are dangerous.
class Point:
    def __init__(self, x, y):
        print(f"   Point.__init__({x}, {y})")
        self.x, self.y = x, y
    def __reduce__(self):
        return (Point, (self.x, self.y))      # rebuild via the constructor

print("\n# 15. __reduce__ - Full Control of Pickling")
pt = Point(1, 2)
pt2 = pickle.loads(pickle.dumps(pt))
print("restored:", pt2.x, pt2.y)
print("__reduce__ output:", pt.__reduce__()[1])

# 16. __slots__ with Pickle and Copy
# ------------------------------------
# - __slots__ removes the per-instance __dict__ to save memory and block stray attributes (see 02-Encapsulation.py).
# - Pickle protocol 2+ and copy handle slots automatically: the state becomes (None, {slot: value}).
# - Add '__weakref__' to __slots__ if you want weak references to instances (section 6).
# - GOTCHA: with very old protocols 0 and 1, slotted classes without __getstate__ fail to pickle.
# - GOTCHA: if the parent has __dict__ and the child adds __slots__, you still get a __dict__.
class Slim:
    __slots__ = ("a", "b", "__weakref__")
    def __init__(self, a, b):
        self.a, self.b = a, b
    def __repr__(self):
        return f"Slim({self.a}, {self.b})"

print("\n# 16. __slots__ with Pickle and Copy")
sl = Slim(1, [2])
print("has __dict__:", hasattr(sl, "__dict__"))
print("pickle round trip:", pickle.loads(pickle.dumps(sl)))
sl_copy = copy.copy(sl)
sl_deep = copy.deepcopy(sl)
print("copy shares list:", sl_copy.b is sl.b, "| deepcopy shares list:", sl_deep.b is sl.b)
print("weakref works:", weakref.ref(sl)() is sl)
print("state shape:", sl.__reduce_ex__(2)[2])

# 17. The Hashing and Equality Contract
# ------------------------------------
# - Rule: if a == b then hash(a) == hash(b). (The reverse need not hold: collisions are allowed.)
# - Defining __eq__ WITHOUT __hash__ sets __hash__ to None: the class becomes unhashable (cannot go in a set or be a dict key).
# - Only hash on fields that never change. If a hashed field changes while the object sits in a set/dict,
#   the object is "lost" in the wrong bucket.
# - Use the same fields in __eq__ and __hash__. Dataclasses: eq=True + frozen=True gives a safe hash (see 06-...py).
# - Copies and unpickled objects are NEW objects: they are == to the original if your __eq__ says so, but `is` is False.
class Key:
    def __init__(self, k):
        self.k = k
    def __eq__(self, other):
        return isinstance(other, Key) and self.k == other.k

class GoodKey(Key):
    def __hash__(self):
        return hash(self.k)

print("\n# 17. The Hashing and Equality Contract")
print("Key.__hash__ is None:", Key.__hash__ is None)
try:
    {Key(1)}
except TypeError as e:
    print("set of Key ->", e)
gk = GoodKey(1)
print("GoodKey(1) in {GoodKey(1)}:", GoodKey(1) in {gk})
print("copy and unpickled are == but not identical:",
      copy.deepcopy(gk) == gk, pickle.loads(pickle.dumps(gk)) is gk)

gk.k = 2                                  # mutate a hashed field
bucket = {gk}
gk.k = 3
print("after mutating a stored key, lookup fails:", gk in bucket, "| yet it is still inside:", len(bucket) == 1)

# 18. Context-Managed Lifecycle
# ------------------------------------
# - `with` gives GUARANTEED cleanup at a known moment (even on exceptions), unlike __del__.
# - Implement __enter__ / __exit__ or use contextlib.contextmanager.
# - __exit__(exc_type, exc, tb): return True to swallow the error; return None/False to let it propagate.
# - contextlib.ExitStack closes a dynamic number of resources in reverse order.
# - Rule: acquire in __enter__ (not in __init__) when the object can be created without being used.
class Resource:
    def __init__(self, name):
        self.name = name
        print(f"   {name}: created")
    def __enter__(self):
        print(f"   {self.name}: opened")
        return self
    def __exit__(self, exc_type, exc, tb):
        print(f"   {self.name}: closed (error: {exc_type.__name__ if exc_type else None})")
        return False                       # do not swallow

@contextlib.contextmanager
def temp_resource(name):
    print(f"   {name}: setup")
    try:
        yield name
    finally:
        print(f"   {name}: teardown")

print("\n# 18. Context-Managed Lifecycle")
with Resource("r1") as r:
    print("   working with", r.name)
try:
    with Resource("r2"):
        raise ValueError("boom")
except ValueError:
    print("   error still propagated, but cleanup ran")
with temp_resource("gen") as nm:
    print("   inside", nm)
with contextlib.ExitStack() as stack:
    for n in ("s1", "s2"):
        stack.enter_context(Resource(n))
    print("   all open; they close in reverse order")

# 19. Putting It Together: a Safe, Copyable, Picklable Class
# ------------------------------------
# - Checklist for a class that owns a resource:
#   1. Do the real cleanup in close()/__exit__, make close() idempotent (safe to call twice).
#   2. Add weakref.finalize as a safety net, not as the main plan.
#   3. Drop the live resource in __getstate__, reopen lazily or in __setstate__.
#   4. __eq__ and __hash__ on immutable identity fields only.
#   5. Always provide __repr__.
class Logger:
    def __init__(self, label):
        self.label = label
        self._open()
    def _open(self):
        self.lines = []                                  # stands in for a real file handle
        self._fin = weakref.finalize(self, print, f"   safety net: {self.label} was never closed")
    def close(self):
        if self._fin.alive:
            self._fin.detach()
            print(f"   {self.label}: closed properly")
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        self.close()
    def __getstate__(self):
        return {"label": self.label}                     # lines + finalizer are runtime-only
    def __setstate__(self, state):
        self.label = state["label"]
        self._open()
    def __repr__(self):
        return f"Logger({self.label!r})"

print("\n# 19. Putting It Together: a Safe, Copyable, Picklable Class")
with Logger("good") as lg:
    lg.lines.append("hi")
lg.close()                                  # second close is harmless
clone = pickle.loads(pickle.dumps(lg))
print("pickled clone:", clone, "| fresh lines:", clone.lines)
clone.close()
leaky = Logger("leaky")
del leaky                                   # never closed -> the safety net speaks
print("end of lifecycle demo")
