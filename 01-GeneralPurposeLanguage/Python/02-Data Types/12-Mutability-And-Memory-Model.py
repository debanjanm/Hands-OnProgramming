## 0.  Names are labels, not boxes
## 1.  id(), `is` vs `==` (quick recap)
## 2.  Mutable vs immutable: verified by experiment
## 3.  Aliasing bugs: b = a, and [[0]*3]*3
## 4.  += : in-place (list) vs rebinding (tuple, int, str)
## 5.  The t[0] += [1] puzzle: TypeError, yet it mutates
## 6.  Argument passing = "pass by object reference"
## 7.  Mutable default arguments (recap)
## 8.  Reference counting: sys.getrefcount
## 9.  `del` removes a NAME, not an object
## 10. The cyclic garbage collector (gc)
## 11. weakref: references that don't keep objects alive
## 12. __del__ is unreliable
## 13. Copying: =, slice, .copy(), copy.copy, copy.deepcopy
## 14. Interning recap (small ints, strings)
## 15. sys.getsizeof vs deep size
## 16. tracemalloc: list of 100k ints vs a generator
## 17. __slots__ pointer
## 18. Mental model cheat sheet

# Python Mutability & Memory Model Explanation

import copy
import gc
import sys
import tracemalloc
import weakref

# 0. Names are labels, not boxes
# ------------------------------------
# - In C, `int x = 5;` is a BOX named x holding 5. `y = x` copies the contents.
# - In Python, an assignment never copies. `x = 5` means: "make the object 5
#   exist (or find it), and stick the label x on it."
# - Objects live in memory. Names (variables) are just labels pointing at them.
#   One object can wear many labels; a label can be moved to another object.
# - So the real questions are always: "which OBJECT does this name point to?"
#   and "can that object change?" (mutable) or not (immutable).

print("\n# 0. Names are labels, not boxes")
print("# ------------------------------------")

a = [1, 2, 3]
b = a                                   # NOT a copy: a second label on the same list
print("a, b                 :", a, b)
print("same object?         :", a is b)
b.append(4)                             # mutate the object through label b
print("after b.append(4)    : a =", a, "| b =", b, "<- a 'changed' too: it's ONE list")

a = [99]                                # MOVE label a to a brand-new list
print("after a = [99]       : a =", a, "| b =", b, "<- b still points at the old list")
print("# Rebinding a name (a = ...) never affects other names.")
print("# Mutating an object (a.append, a[0] = ...) is seen by EVERY name on it.")

x = 5
x = "now a string"                      # names have no type; only objects do
print("\nx moved from an int to a str:", type(x).__name__, "(the name has no type, the object does)")

# 1. id(), `is` vs `==` (quick recap)
# ------------------------------------
# - id(obj)  : a number unique to the object while it is alive. In CPython it is
#              the memory address. Never rely on its value, only on equality.
# - a is b   : True if both names point at the SAME object (id(a) == id(b)).
# - a == b   : True if the objects have equal VALUE (calls __eq__).
# - Use `is` only for singletons: `x is None`, `x is True`. Use == for values.
# - Fuller recap in ../01-Python Fundamentals/02-Fundamentals.py

print("\n# 1. id(), `is` vs `==`")
print("# ------------------------------------")

p = [1, 2]
q = [1, 2]
r = p
print("p == q               :", p == q, "(equal values)")
print("p is q               :", p is q, "(two separate lists)")
print("p is r               :", p is r, "(same list, two labels)")
print("id(p) == id(r)       :", id(p) == id(r), "| id(p) == id(q):", id(p) == id(q))
v = None
print("v is None            :", v is None, "(the one place where `is` is the right tool)")

# 2. Mutable vs immutable: verified by experiment
# ------------------------------------
# - IMMUTABLE: the object can never change after creation (int, float, str,
#   tuple, frozenset, bytes). "Changing" it really builds a NEW object.
# - MUTABLE:   the object can change in place, keeping its id (list, dict,
#   set, bytearray, most user-defined class instances).
# - Instead of memorising, test: apply a changing operation and see whether
#   (a) it is allowed and (b) the id stays the same.

print("\n# 2. Mutable vs immutable: verified by experiment")
print("# ------------------------------------")


def experiment(label, make, change):
    """Build an object, try to change it in place, report what happened."""
    obj = make()
    before_id = id(obj)
    before_repr = repr(obj)
    try:
        change(obj)
    except (TypeError, AttributeError) as e:
        print(f"{label:<10} IMMUTABLE | {type(e).__name__}: {e}")
        return
    same = id(obj) == before_id
    print(f"{label:<10} MUTABLE   | {before_repr} -> {obj!r} | same id: {same}")


def set_item(o):
    o[0] = "X"


experiment("list", lambda: [1, 2], lambda o: o.append(3))
experiment("dict", lambda: {"k": 1}, lambda o: o.update(z=2))
experiment("set", lambda: {1, 2}, lambda o: o.add(3))
experiment("bytearray", lambda: bytearray(b"ab"), lambda o: o.__setitem__(0, 99))
experiment("str", lambda: "ab", set_item)
experiment("tuple", lambda: (1, 2), set_item)
experiment("bytes", lambda: b"ab", set_item)
experiment("frozenset", lambda: frozenset({1}), lambda o: o.add(2))
experiment("int", lambda: 10, lambda o: setattr(o, "real", 5))

print("\n# 'Changing' an immutable value really rebinds the name to a NEW object:")
n = 10
before = id(n)
n = n + 1
print("   int : id changed after n = n + 1 ->", id(n) != before)
s = "ab"
before = id(s)
s = s + "c"
print("   str : id changed after s = s + 'c' ->", id(s) != before)

print("\n# Table (all verified above):")
print("#   MUTABLE   : list, dict, set, bytearray, (most) class instances")
print("#   IMMUTABLE : int, float, bool, str, tuple, frozenset, bytes, None")

# "Immutable" is SHALLOW: a tuple can't change which objects it holds, but a
# mutable object inside it can still change.
tup = ([1, 2], "fixed")
tup[0].append(3)
print("\ntuple holding a list, after tup[0].append(3):", tup, "<- the tuple never changed, its list did")
try:
    hash(tup)
except TypeError as e:
    print("hash(tup) -> TypeError:", e, "(so it can't be a dict key or set member)")
print("hash((1, 'a'))       :", type(hash((1, "a"))).__name__, "(all-immutable tuples ARE hashable)")

# 3. Aliasing bugs: b = a, and [[0]*3]*3
# ------------------------------------
# - Aliasing = two names (or two slots in a container) on the same mutable
#   object. It's behind most "why did my data change?" bugs.
# - `seq * n` repeats REFERENCES, it does not copy the elements.
#   Harmless for ints/strs, a trap for lists.

print("\n# 3. Aliasing bugs")
print("# ------------------------------------")

# Bug 1: "copying" with =
original = [10, 20, 30]
backup = original                       # BUG: not a backup, same list
original.append(40)
print("backup (supposed to be old) :", backup, "<- wrong, it moved with original")
backup = original.copy()                # fix: a real (shallow) copy
original.append(50)
print("after .copy()  backup       :", backup, "| original:", original)

# Bug 2: [[0]*3]*3
bad = [[0] * 3] * 3                     # ONE inner list, referenced 3 times
bad[0][0] = "X"
print("\nbad  = [[0]*3]*3 ; bad[0][0] = 'X' ->", bad)
print("bad[0] is bad[1] is bad[2]  :", bad[0] is bad[1] is bad[2], "(all three rows are the same list)")

good = [[0] * 3 for _ in range(3)]      # the comprehension builds a NEW list per row
good[0][0] = "X"
print("good = [[0]*3 for _ in range(3)] ->", good)
print("good[0] is good[1]          :", good[0] is good[1])
print("# Note [0]*3 is fine: the repeated item (0) is immutable, so sharing is harmless.")

# Bug 3: dict.fromkeys with a mutable value
shared = dict.fromkeys(["a", "b"], [])  # the SAME [] is used for every key
shared["a"].append(1)
print("\ndict.fromkeys(['a','b'], [])   after shared['a'].append(1):", shared)
fixed = {k: [] for k in ["a", "b"]}
fixed["a"].append(1)
print("dict comprehension (fix)                                  :", fixed)

# 4. += : in-place (list) vs rebinding (tuple, int, str)
# ------------------------------------
# - `x += y` first tries x.__iadd__(y) (in-place add).
#     * list defines __iadd__: it extends the SAME list, id stays the same.
#     * int/str/tuple have no __iadd__, so Python falls back to
#       x = x + y: a NEW object, the name is rebound, id changes.
# - `x = x + y` on a list also builds a new list (different from x += y!).

print("\n# 4. += : in-place vs rebinding")
print("# ------------------------------------")

lst = [1, 2]
id0 = id(lst)
lst += [3]
print("list  +=  : same id?", id(lst) == id0, "->", lst)

lst2 = [1, 2]
id0 = id(lst2)
lst2 = lst2 + [3]
print("list  x=x+: same id?", id(lst2) == id0, "->", lst2, "(a new list was built)")

tp = (1, 2)
id0 = id(tp)
tp += (3,)
print("tuple +=  : same id?", id(tp) == id0, "->", tp)

num = 1000
id0 = id(num)
num += 1
print("int   +=  : same id?", id(num) == id0, "->", num)

st = "ab"
id0 = id(st)
st += "c"
print("str   +=  : same id?", id(st) == id0, "->", st)

# Why it matters: with aliases, += on a list is visible to everyone.
m1 = [1]
m2 = m1
m1 += [2]                               # in place
print("\naliases: m1 += [2]     -> m2 =", m2, "(m2 sees it)")
m1 = m1 + [3]                           # new list; m1 moves, m2 stays
print("aliases: m1 = m1 + [3] -> m2 =", m2, "| m1 =", m1, "(m2 does NOT see it)")

# list += accepts ANY iterable, + needs a list:
chars = ["a"]
chars += "bc"                           # extends with each character
print("\nlist += 'bc'        :", chars)
try:
    chars + "de"
except TypeError as e:
    print("list + 'de'  -> TypeError:", e)

# 5. The t[0] += [1] puzzle: TypeError, yet it mutates
# ------------------------------------
# - t = ([1],) ; t[0] += [2]  raises TypeError... but afterwards t == ([1, 2],).
# - `t[0] += [2]` expands to three steps:
#       1. tmp = t[0]                 (get the list)       - fine
#       2. tmp = tmp.__iadd__([2])    (extend list IN PLACE) - works! the list now has 2
#       3. t[0] = tmp                 (store it back)      - tuples refuse -> TypeError
# - Step 2 already happened, and it cannot be undone. Both facts are true:
#   the exception is raised AND the list changed.
# - The tuple itself never changed (it still points to the same list).

print("\n# 5. The t[0] += [1] puzzle")
print("# ------------------------------------")

t = ([1],)
try:
    t[0] += [2]
except TypeError as e:
    print("t[0] += [2] -> TypeError:", e)
print("t is now            :", t, "<- the list inside DID change")

# Safe ways: call the method directly (no re-assignment step), or extend:
t = ([1],)
t[0].extend([2])
print("t[0].extend([2])    :", t, "(no error: no store-back into the tuple)")

# 6. Argument passing = "pass by object reference"
# ------------------------------------
# - Python is neither pass-by-value nor pass-by-reference. A parameter is a
#   NEW NAME bound to the SAME object the caller passed ("call by object
#   reference" / "call by sharing").
# - Inside the function:
#     * MUTATE the object (append, item assignment, +=-on-list)  -> caller sees it.
#     * REBIND the parameter (param = something)                 -> caller unaffected;
#       the local name just moves to another object.
# - Immutable arguments can only ever be rebound, so they feel "by value".

print("\n# 6. Argument passing = pass by object reference")
print("# ------------------------------------")


def mutate(items):
    items.append("added")               # same object as the caller's: visible outside


def rebind(items):
    items = ["brand new"]               # local name moves; caller's list untouched
    return items


def augmented(items):
    items += ["via +="]                 # list.__iadd__ is IN PLACE: visible outside


def identity(items):
    return id(items)


data = [1, 2]
print("id same inside the function  :", identity(data) == id(data), "(the parameter IS the caller's object)")
mutate(data)
print("after mutate(data)           :", data)
rebind(data)
print("after rebind(data)           :", data, "<- unchanged")
augmented(data)
print("after augmented(data) (+=)   :", data, "<- += on a list mutates")


def bump(n):
    n += 1                              # int is immutable -> rebinding the local name
    return n


count = 5
print("\nbump(count) returns          :", bump(count), "| count is still:", count)
print("# To 'change' an immutable, RETURN the new value and rebind in the caller.")

# 7. Mutable default arguments (recap)
# ------------------------------------
# - Default values are evaluated ONCE, when `def` runs, and stored on the
#   function object. A mutable default is therefore shared by every call that
#   doesn't pass its own value.
# - Fix: default to None, create the fresh object inside the function.
# - Full explanation: ../03-Functions/02-Functions.py

print("\n# 7. Mutable default arguments")
print("# ------------------------------------")


def add_item_bad(item, bag=[]):
    bag.append(item)
    return bag


def add_item_good(item, bag=None):
    if bag is None:
        bag = []
    bag.append(item)
    return bag


print("bad  first call  :", add_item_bad("a"))
print("bad  second call :", add_item_bad("b"), "<- remembers 'a'!")
print("stored default   :", add_item_bad.__defaults__, "(it lives on the function object)")
print("good first call  :", add_item_good("a"))
print("good second call :", add_item_good("b"))

# 8. Reference counting: sys.getrefcount
# ------------------------------------
# - CPython tracks, for each object, HOW MANY references point at it
#   (names, list slots, dict values, function arguments...).
# - When the count reaches 0 the object is freed IMMEDIATELY and its memory
#   reused. This is the main memory-management mechanism of CPython.
# - sys.getrefcount(obj) reports the count, but it is always 1 higher than
#   you expect: passing obj as the ARGUMENT creates a temporary extra
#   reference for the duration of the call.
# - (Other implementations such as PyPy do not use reference counting.)

print("\n# 8. Reference counting: sys.getrefcount")
print("# ------------------------------------")


class Thing:
    """A plain class instance (weak-referenceable, no __slots__)."""

    def __init__(self, label="thing"):
        self.label = label


obj = Thing()
print("one name `obj`            :", sys.getrefcount(obj), "(1 for the name + 1 for the argument)")
alias1 = obj
print("add alias1                :", sys.getrefcount(obj))
holder = [obj]
print("put it in a list          :", sys.getrefcount(obj))
holder_dict = {"k": obj}
print("put it in a dict value    :", sys.getrefcount(obj))
del alias1
print("del alias1                :", sys.getrefcount(obj))
holder.clear()
holder_dict.clear()
print("clear list and dict       :", sys.getrefcount(obj), "<- back to 2: name + argument")


def inside(o):
    return sys.getrefcount(o)


print("inside a function         :", inside(obj), "(the parameter name is one more reference)")
print("# Small ints / interned strings show huge counts (shared by the interpreter):")
print("   getrefcount(0)         :", sys.getrefcount(0) > 100, "(> 100: many internal users)")

# 9. `del` removes a NAME, not an object
# ------------------------------------
# - `del name` unbinds the label and lowers the refcount by 1.
#   The OBJECT is destroyed only if that was the last reference.
# - You cannot force an object to be deleted; you can only remove references.
# - `del lst[i]` / `del d[key]` remove a reference held by the container.

print("\n# 9. `del` removes a name, not an object")
print("# ------------------------------------")

first = Thing("shared")
second = first
freed = []                              # finalize() will record here when the object dies
weakref.finalize(first, freed.append, "object freed")

del first
print("after del first    : second.label =", second.label, "| freed:", freed, "<- object still alive")
try:
    first
except NameError as e:
    print("using `first`      -> NameError:", e)
del second
print("after del second   : freed:", freed, "<- last reference gone, CPython frees it NOW")

# 10. The cyclic garbage collector (gc)
# ------------------------------------
# - Refcounting has a blind spot: a REFERENCE CYCLE (a -> b -> a). Each object
#   keeps the other's count above 0, so neither reaches 0 even when nothing
#   else can reach them. That's a leak with refcounting alone.
# - CPython adds a cyclic garbage collector (module `gc`). It periodically
#   looks for groups of objects that only reference each other and frees them.
#   Container objects (list, dict, instances) are tracked; ints/strs can't
#   form cycles so they aren't.
# - Generations: young objects are checked often (gen 0), survivors move to
#   gen 1, then gen 2 (checked rarely). gc.get_threshold() = when to trigger;
#   gc.get_count() = how many allocations are pending in each generation.
# - gc.collect() forces a full collection and returns how many unreachable
#   objects it found.
# - PROOF below: a weakref.finalize callback tells us when an object really dies.

print("\n# 10. The cyclic garbage collector (gc)")
print("# ------------------------------------")

print("gc enabled by default    :", gc.isenabled())
print("gc.get_threshold()       :", gc.get_threshold(), "(gen0, gen1, gen2 trigger levels)")
print("gc.get_count()           :", gc.get_count(), "(live counters; values vary run to run)")


class Node:
    def __init__(self, name):
        self.name = name
        self.other = None


events = []


def make_garbage(cyclic):
    """Create two linked nodes, return only weak refs, so nothing strong survives."""
    n1, n2 = Node("n1"), Node("n2")
    n1.other = n2
    if cyclic:
        n2.other = n1                   # the cycle: n1 -> n2 -> n1
    tag = "cyclic" if cyclic else "acyclic"
    weakref.finalize(n1, events.append, f"{tag} n1 freed")
    return weakref.ref(n1)              # a weak ref does not keep n1 alive


gc.disable()                            # make the demo deterministic (no surprise automatic runs)
try:
    ref_plain = make_garbage(cyclic=False)
    print("\nacyclic pair after function returns :", events, "| weakref alive:", ref_plain() is not None)
    print("   -> freed instantly by refcounting alone; gc not needed.")

    ref_cycle = make_garbage(cyclic=True)
    print("cyclic pair after function returns  :", events, "| weakref alive:", ref_cycle() is not None)
    print("   -> NOT freed: each node's refcount is still 1 (from the other node).")

    found = gc.collect()
    print("after gc.collect()                  :", events, "| weakref alive:", ref_cycle() is not None)
    print("   gc.collect() found unreachable objects:", found > 0)
finally:
    gc.enable()                         # always restore the default

print("# gc.disable() is used only in this demo. Real programs leave it on.")
print("# Tip: break cycles yourself (set .other = None) or use weakref for back-pointers.")

# 11. weakref: references that don't keep objects alive
# ------------------------------------
# - A weak reference points at an object WITHOUT increasing its refcount.
#   When the object dies, the weakref turns into a dead link (returns None).
# - Uses: caches, observer lists, parent back-pointers in trees (avoids cycles).
# - weakref.ref(obj)()           -> the object, or None if it died.
# - WeakValueDictionary          -> dict whose values vanish when no one else
#                                   holds them (a self-cleaning cache).
# - Not everything supports it: instances of normal classes, functions, sets
#   do; int, str, tuple, list, dict (plain) do NOT. Subclass them to get it.
# - __slots__ classes need '__weakref__' in __slots__ to be weak-referenceable.

print("\n# 11. weakref")
print("# ------------------------------------")

target = Thing("target")
wr = weakref.ref(target)
print("wr() while alive       :", wr().label, "| refcount unchanged by weakref:", sys.getrefcount(target))
del target
print("wr() after del target  :", wr(), "<- dead link returns None")

for label, value in [("int", 5), ("str", "hi"), ("list", [1]), ("dict", {}), ("tuple", (1,))]:
    try:
        weakref.ref(value)
        print(f"weakref to {label:<5}: allowed")
    except TypeError as e:
        print(f"weakref to {label:<5}: TypeError: {e}")


class WeakList(list):
    """A list subclass: instances get a __weakref__ slot automatically."""


wl = WeakList([1, 2])
print("weakref to list SUBCLASS: allowed ->", weakref.ref(wl)() is wl)

# A self-cleaning cache:
cache = weakref.WeakValueDictionary()
big = Thing("expensive object")
cache["key"] = big
print("\ncache has 'key'        :", "key" in cache, "| len:", len(cache))
del big
print("after del big          :", "key" in cache, "| len:", len(cache), "<- entry vanished by itself")


class SlotsOnly:
    __slots__ = ("x",)


class SlotsWeak:
    __slots__ = ("x", "__weakref__")


try:
    weakref.ref(SlotsOnly())
except TypeError as e:
    print("\n__slots__ without '__weakref__':", e)
print("__slots__ with '__weakref__'   :", weakref.ref(SlotsWeak()) is not None)

# 12. __del__ is unreliable
# ------------------------------------
# - __del__ is a "finalizer" called when an object is about to be destroyed.
# - In CPython it often runs right when the refcount hits 0, so it LOOKS
#   deterministic. But the language does not promise it:
#     * it may run late (object in a cycle, waits for gc),
#     * may never run (interpreter shutdown, other implementations like PyPy),
#     * exceptions inside it are printed and ignored,
#     * it can resurrect the object.
# - Don't use it to release files, locks, sockets. Use `with` (context
#   managers) or try/finally, or weakref.finalize for cleanup callbacks.

print("\n# 12. __del__ is unreliable")
print("# ------------------------------------")

log = []


class Noisy:
    def __init__(self, name):
        self.name = name

    def __del__(self):
        log.append(f"{self.name} __del__ ran")


n = Noisy("first")
del n
print("refcount hit 0 in CPython :", log, "(prompt here, but only by CPython's implementation detail)")
print("# Guideline: treat __del__ as a debugging aid, never as a resource manager.")

# 13. Copying: =, slice, .copy(), copy.copy, copy.deepcopy
# ------------------------------------
# - `b = a`             : NO copy, just another name.
# - SHALLOW copies (new outer container, SAME inner objects):
#       a[:], a.copy(), list(a), dict(d), d.copy(), copy.copy(a)
# - DEEP copy: copy.deepcopy(a) recursively copies everything, so nothing is
#   shared with the original. Handles reference cycles via a memo dict.
# - Shallow is fine when the items are immutable (ints, strs, tuples of them).
#   For nested mutable data you need deepcopy (or to copy the inner parts).

print("\n# 13. Copying")
print("# ------------------------------------")

nested = [[1, 2], [3, 4]]

assigned = nested
sliced = nested[:]
dot_copy = nested.copy()
ctor = list(nested)
shallow = copy.copy(nested)
deep = copy.deepcopy(nested)

print(f"{'method':<14}{'outer new?':<12}{'inner shared?'}")
for name, c in [("b = a", assigned), ("a[:]", sliced), ("a.copy()", dot_copy),
                ("list(a)", ctor), ("copy.copy", shallow), ("deepcopy", deep)]:
    print(f"{name:<14}{str(c is not nested):<12}{c[0] is nested[0]}")

nested[0].append("!")
print("\nafter nested[0].append('!'):")
print("   nested  :", nested)
print("   sliced  :", sliced, "<- shallow copy sees the inner change")
print("   deep    :", deep, "<- deep copy is fully independent")

# Shallow copy: the OUTER list is independent...
sliced.append([9, 9])
print("\nappend to the outer shallow copy; original untouched:", nested)

# dicts behave the same:
config = {"name": "app", "opts": {"debug": False}}
config_shallow = config.copy()
config_deep = copy.deepcopy(config)
config["opts"]["debug"] = True
print("\nconfig['opts']['debug'] = True")
print("   shallow copy sees it :", config_shallow["opts"]["debug"])
print("   deep copy does not   :", config_deep["opts"]["debug"])

# deepcopy and cycles: the memo dict remembers what it already copied
cyc = [1]
cyc.append(cyc)                         # a list that contains itself
print("\ncyc = [1, cyc] prints as:", cyc)
cyc_copy = copy.deepcopy(cyc)
print("deepcopy worked (no infinite loop)     :", cyc_copy)
print("copy's cycle points to the COPY        :", cyc_copy[1] is cyc_copy, "| not the original:", cyc_copy[1] is not cyc)

# deepcopy preserves shared references INSIDE the structure (via the memo):
inner = [0]
pair = [inner, inner]
pair_copy = copy.deepcopy(pair)
print("deepcopy keeps internal sharing        :", pair_copy[0] is pair_copy[1], "| independent of original:", pair_copy[0] is not inner)

# Immutables: copying them returns the same object (nothing to protect)
pt = (1, 2)
print("copy.copy(tuple) is the same object    :", copy.copy(pt) is pt, "| deepcopy of an all-immutable tuple:", copy.deepcopy(pt) is pt)
print("# (immutable => nothing to protect, so no new object is built)")

# 14. Interning recap (small ints, strings)
# ------------------------------------
# - CPython pre-creates the ints -5..256 and reuses them; short identifier-like
#   strings are interned. `sys.intern(s)` interns any string on request.
# - Because immutables can be safely shared, this is a free optimisation.
# - It is an IMPLEMENTATION DETAIL: never use `is` to compare numbers/strings.
# - Full demo: 01-Primitive.py (and the `is` vs `==` recap in Fundamentals).

print("\n# 14. Interning recap")
print("# ------------------------------------")

small1, small2 = int("100"), int("100")
big1, big2 = int("100000"), int("100000")       # built at runtime, so no compile-time sharing
print("int('100') is int('100')       :", small1 is small2, "(cached small int)")
print("int('100000') is int('100000') :", big1 is big2, "(separate objects, but == is", big1 == big2, ")")

built1 = "".join(["py", "thon trick!"])
built2 = "".join(["py", "thon trick!"])
print("two runtime-built strings is   :", built1 is built2, "| ==:", built1 == built2)
print("after sys.intern on both       :", sys.intern(built1) is sys.intern(built2))

# 15. sys.getsizeof vs deep size
# ------------------------------------
# - sys.getsizeof(obj) is SHALLOW: it counts the container's own memory (the
#   array of pointers), NOT the objects it points to.
#   So a list of 1000 big strings and a list of 1000 ints "weigh" the same.
# - The real footprint = the container + everything it (recursively) owns.
# - We write a small recursive helper. Two rules:
#     * keep a `seen` set of ids so shared objects are counted once and
#       cycles don't recurse forever,
#     * walk dict keys AND values, and list/tuple/set/frozenset items.
# - (For real projects: pympler.asizeof does this, but it's third party.)

print("\n# 15. sys.getsizeof vs deep size")
print("# ------------------------------------")


def deep_size(obj, seen=None):
    """Approximate total bytes of obj and everything reachable inside it."""
    if seen is None:
        seen = set()
    if id(obj) in seen:                 # already counted (shared object or cycle)
        return 0
    seen.add(id(obj))
    total = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for key, value in obj.items():
            total += deep_size(key, seen) + deep_size(value, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            total += deep_size(item, seen)
    elif hasattr(obj, "__dict__"):      # plain class instance
        total += deep_size(vars(obj), seen)
    return total


words = ["a" * 100 for _ in range(5)]   # five distinct 100-char strings
numbers = [1000, 2000, 3000, 4000, 5000]
print("sys.getsizeof(words)   :", sys.getsizeof(words), "bytes (just 5 pointers)")
print("sys.getsizeof(numbers) :", sys.getsizeof(numbers), "bytes (same! only pointers counted)")
print("deep_size(words)       :", deep_size(words), "bytes")
print("deep_size(numbers)     :", deep_size(numbers), "bytes")

record = {"name": "Alice", "scores": [90, 85, 77], "tags": ("a", "b"), "meta": {"x": [1, 2]}}
print("\nrecord shallow         :", sys.getsizeof(record), "bytes")
print("record deep            :", deep_size(record), "bytes (much larger)")

# Shared objects are counted once, cycles don't loop forever:
shared_item = "z" * 1000
twice = [shared_item, shared_item]
once = [shared_item]
print("\n[s, s] vs [s] deep diff:", deep_size(twice) - deep_size(once), "bytes = one more pointer, not another 1000-char string")
loop = []
loop.append(loop)
print("deep_size of a self-containing list:", deep_size(loop), "bytes (terminates thanks to `seen`)")

# 16. tracemalloc: list of 100k ints vs a generator
# ------------------------------------
# - tracemalloc (stdlib) records every Python memory allocation, so you can
#   see HOW MUCH memory a piece of code really uses.
# - get_traced_memory() -> (current, peak) bytes since tracemalloc.start().
# - take_snapshot() lets you see which source LINES allocated the most.
# - A list holds all 100k int objects at once (~3-4 MB). A generator produces
#   one value at a time and keeps almost nothing: O(1) memory.

print("\n# 16. tracemalloc: list vs generator")
print("# ------------------------------------")

N = 100_000


def measure(builder):
    tracemalloc.start()
    result = builder()                  # keep result alive so it counts in `current`
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return result, current, peak


as_list, cur_list, peak_list = measure(lambda: list(range(N)))
total_gen, cur_gen, peak_gen = measure(lambda: sum(i for i in range(N)))      # generator expression, consumed lazily

print(f"list of {N:,} ints   : current {cur_list / 1024:9.1f} KiB | peak {peak_list / 1024:9.1f} KiB")
print(f"generator sum        : current {cur_gen / 1024:9.1f} KiB | peak {peak_gen / 1024:9.1f} KiB")
print("same answer          :", sum(as_list) == total_gen)
print("generator peak far smaller than list:", peak_gen * 100 < peak_list)

# Which line allocated the memory? (snapshot, filtered to this file)
tracemalloc.start()
kept = [i * 2 for i in range(N)]        # <- this line will dominate the report
snapshot = tracemalloc.take_snapshot().filter_traces([tracemalloc.Filter(True, __file__)])
tracemalloc.stop()
top = snapshot.statistics("lineno")[0]
print(f"\ntop allocating line in this file: line {top.traceback[0].lineno} -> {top.size / 1024:.0f} KiB in {top.count:,} blocks")

# Where does the list's memory go? 8-byte pointers + one int object per item.
print("pointer array alone  :", sys.getsizeof(as_list) // 1024, "KiB | each int object ~", sys.getsizeof(1000), "bytes")

# 17. __slots__ pointer
# ------------------------------------
# - Every normal instance carries a per-object __dict__ (a hash table) for its
#   attributes. For millions of small objects that is a lot of memory.
# - `__slots__ = ("x", "y")` replaces the dict with fixed slots: smaller
#   objects, faster attribute access, no accidental new attributes.
# - Trade-off seen in section 11: slots classes need '__weakref__' to be
#   weak-referenceable. Full explanation: ../04-OOPs/01-Class-Object.py

print("\n# 17. __slots__ pointer")
print("# ------------------------------------")


class PlainPoint:
    def __init__(self, x, y):
        self.x, self.y = x, y


class SlotPoint:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x, self.y = x, y


pp, sp = PlainPoint(1, 2), SlotPoint(1, 2)
print("PlainPoint has __dict__ :", hasattr(pp, "__dict__"), "| deep size:", deep_size(pp), "bytes")
print("SlotPoint  has __dict__ :", hasattr(sp, "__dict__"), "| size     :", sys.getsizeof(sp), "bytes")
try:
    sp.z = 3
except AttributeError as e:
    print("sp.z = 3 -> AttributeError:", e)

# 18. Mental model cheat sheet
# ------------------------------------
print("\n# 18. Mental model cheat sheet")
print("# ------------------------------------")
print("# 1. Names are labels. Assignment (b = a) puts a second label on the SAME object.")
print("# 2. Objects have id, type and value. `is` compares ids, `==` compares values.")
print("# 3. MUTABLE (list, dict, set, bytearray, instances) change in place, id stays.")
print("#    IMMUTABLE (int, str, tuple, frozenset, bytes) never change; 'changing' makes a new object.")
print("# 4. Mutate an object -> every name on it sees it. Rebind a name -> only that name moves.")
print("# 5. Containers store REFERENCES. seq * n and shallow copies share the inner objects.")
print("#    Build independent rows with a comprehension; use copy.deepcopy for nested data.")
print("# 6. x += y is in place for lists (__iadd__), rebinding for int/str/tuple.")
print("#    t[0] += [1] on a tuple mutates the list THEN fails on the store-back.")
print("# 7. Function arguments = new names for the caller's objects (pass by object reference).")
print("#    Default values are created once: never use a mutable default; use None.")
print("# 8. CPython frees an object when its refcount hits 0 (sys.getrefcount is +1 for the argument).")
print("#    `del name` removes a label, not the object.")
print("# 9. Reference cycles escape refcounting; the gc module finds them (gc.collect()).")
print("#    weakref gives non-owning references; use it for caches and back-pointers.")
print("# 10. Don't trust __del__ for cleanup: use `with`, try/finally or weakref.finalize.")
print("# 11. sys.getsizeof is shallow; measure real usage with a deep-size walk or tracemalloc.")
print("# 12. Prefer generators over lists when you only need to stream over the data.")

print("\n# End of Mutability & Memory Model Explanation")
