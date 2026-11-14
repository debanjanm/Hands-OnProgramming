import sys
import json
import types
from collections import OrderedDict, UserDict, UserList, UserString
from collections.abc import (
    Callable, Collection, Container, Hashable, Iterable, Iterator, Mapping,
    MutableMapping, MutableSequence, MutableSet, Reversible, Sequence, Set, Sized,
)

# 01. The Container Protocol in Plain Words
# ------------------------------------
# - A "container" is any object that supports some of: len(), obj[i], `in`, for-loops.
# - Python never asks "are you a list?". It just calls a dunder method if you have it
#   (duck typing - see 04-Polymorphism.py). Implement the dunder, get the feature.
# - Subscripting collections.abc classes like Sequence[int] needs Python 3.9+
#   (this file uses it in section 12), so older Pythons stop here with a message.
if sys.version_info < (3, 9):
    print("Skipped: this file needs Python 3.9+ (Sequence[int] style hints).")
    sys.exit(0)

#   Dunder           What calls it
#   --------------   --------------------------------------------------------------
#   __len__          len(obj); also bool(obj) if there is no __bool__ (see 06 section 17)
#   __getitem__      obj[i], obj[a:b] (gets a slice object), and the OLD for-loop fallback
#   __contains__     x in obj
#   __iter__         for x in obj, list(obj), a, b = obj, sum/min/max/sorted(obj)
#   __reversed__     reversed(obj)  (else Python falls back to __len__ + __getitem__)
#   __setitem__      obj[i] = v, obj[a:b] = values
#   __delitem__      del obj[i], del obj[a:b]
class Spy:
    """Logs which dunder each language feature really calls."""
    def __init__(self):
        self.data = ["a", "b", "c"]
    def __len__(self):
        print("      -> __len__")
        return len(self.data)
    def __getitem__(self, index):
        print(f"      -> __getitem__({index!r})")
        return self.data[index]
    def __setitem__(self, index, value):
        print(f"      -> __setitem__({index!r}, {value!r})")
        self.data[index] = value
    def __delitem__(self, index):
        print(f"      -> __delitem__({index!r})")
        del self.data[index]
    def __contains__(self, item):
        print(f"      -> __contains__({item!r})")
        return item in self.data
    def __iter__(self):
        print("      -> __iter__")
        return iter(self.data)
    def __reversed__(self):
        print("      -> __reversed__")
        return iter(self.data[::-1])

spy = Spy()
print("# 01. The Container Protocol in Plain Words")
print("len(spy):");              len(spy)
print("spy[1]:");                spy[1]
print("spy[0:2] (note the slice object):"); spy[0:2]
print("'b' in spy:");            "b" in spy
print("for x in spy: break:");
for x in spy:
    break
print("reversed(spy):");         reversed(spy)
print("spy[0] = 'z':");          spy[0] = "z"
print("del spy[0]:");            del spy[0]
print("a, b = spy:");            a, b = spy
print("bool(spy) (no __bool__ -> falls back to __len__):"); bool(spy)

# 02. The collections.abc Hierarchy - Printed From Real Objects
# ------------------------------------
# - collections.abc holds Abstract Base Classes (ABC basics: see 05-Abstraction.py)
#   describing the standard container "shapes".
# - Each ABC has ABSTRACT methods (you must write them) and MIXIN methods (you get
#   them free, built on top of the abstract ones).
# - Printed below straight from the classes, so it cannot drift from reality.
ALL_ABCS = [Hashable, Callable, Sized, Container, Iterable, Iterator, Reversible,
            Collection, Sequence, MutableSequence, Mapping, MutableMapping, Set, MutableSet]
print("\n# 02. The collections.abc Hierarchy (bases | abstract methods you must write)")
for abc in ALL_ABCS:
    bases = [b.__name__ for b in abc.__bases__ if b is not object]
    print(f"{abc.__name__:<16} bases={str(bases):<34} abstract={sorted(abc.__abstractmethods__)}")
print("# - Collection = Sized + Iterable + Container (the 'has len, can loop, supports in' trio).")
print("# - Sequence / Set / Mapping all extend Collection; the Mutable* versions add mutators.")

# 03. Which Builtin Is Which? isinstance Against Each ABC
# ------------------------------------
# - ABCs can recognise types WITHOUT inheritance: Sized/Iterable/Container/Hashable/Callable
#   just check for the method (structural). Sequence/Mapping/Set rely on registration
#   (list is registered as MutableSequence, dict as MutableMapping...) - so a class that merely
#   has the right methods is NOT automatically a Sequence; you have to subclass or register it.
samples = {
    "list": [1],
    "tuple": (1,),
    "str": "hi",
    "dict": {"a": 1},
    "set": {1},
    "frozenset": frozenset({1}),
    "range": range(3),
    "dict.keys()": {"a": 1}.keys(),
    "generator": (i for i in range(3)),
    "list_iterator": iter([1]),
    "len (function)": len,
}
print("\n# 03. isinstance(obj, ABC) for builtins (only ABCs that match are listed)")
for label, obj in samples.items():
    hits = [abc.__name__ for abc in ALL_ABCS if isinstance(obj, abc)]
    print(f"{label:<15}: {', '.join(hits)}")
print("# - tuple/str/range are Sequence but NOT MutableSequence (read-only).")
print("# - generator is an Iterator (one pass only), but has no len() and no `in` support")
print("#   beyond consuming it -> not a Collection.")
print("# - set is a MutableSet; frozenset is a Set and Hashable; list/dict/set are NOT Hashable.")

# 04. Mixin Methods - What You Get FREE
# ------------------------------------
# - Printed from the ABCs themselves: everything the ABC defines that is NOT abstract.
# - This is the whole point: write ~2-5 core methods, inherit 10+ more.
def mixins(abc):
    skip = {"__subclasshook__", "__class_getitem__", "_abc_impl"}
    out = []
    for name, value in vars(abc).items():
        if name in abc.__abstractmethods__ or name in skip or value is None:
            continue
        if callable(value) or isinstance(value, (classmethod, staticmethod)):
            out.append(name)
    return sorted(out)

print("\n# 04. Mixin methods (own, non-abstract) per ABC")
for abc in (Sequence, MutableSequence, Mapping, MutableMapping, Set, MutableSet):
    print(f"{abc.__name__:<16} abstract={sorted(abc.__abstractmethods__)}")
    print(f"{'':<16} free    ={mixins(abc)}")
print("# - MutableSequence ALSO inherits all of Sequence's free methods; same for the others.")
print("# - Mapping.__reversed__ is deliberately None (dict order is a detail the ABC doesn't promise).")

# 05. A Minimal Read-Only Sequence - Only __getitem__ + __len__
# ------------------------------------
# - Subclass Sequence, write just those two, and you get: __contains__, __iter__,
#   __reversed__, index(), count() for free.
# - __getitem__ must handle: ints, negative ints, slices, and raise IndexError out of range.
#   IndexError is not optional: the free __iter__ keeps calling self[0], self[1], ...
#   and uses IndexError as its "stop" signal.
class Squares(Sequence):
    """Virtual sequence 0, 1, 4, 9, ... : nothing is stored, values are computed on demand."""
    def __init__(self, n):
        self._n = n
    def __len__(self):
        return self._n
    def __getitem__(self, index):
        if isinstance(index, slice):
            # slice.indices(len) resolves None / negative / too-large bounds for us
            return [self[i] for i in range(*index.indices(len(self)))]
        if not isinstance(index, int):
            raise TypeError(f"Squares indices must be int or slice, not {type(index).__name__}")
        if index < 0:
            index += len(self)                  # -1 means "last"
        if not 0 <= index < len(self):
            raise IndexError("Squares index out of range")
        return index * index
    def __repr__(self):
        return f"Squares({self._n})"

sq = Squares(6)
print("\n# 05. Minimal Read-Only Sequence (only __getitem__ + __len__ written)")
print("len(sq)      :", len(sq))
print("sq[3]        :", sq[3])
print("sq[-1]       :", sq[-1], "(negative index normalised by us)")
print("sq[1:4]      :", sq[1:4])
print("sq[::-1]     :", sq[::-1])
print("list(sq)     :", list(sq), "(free __iter__)")
print("16 in sq     :", 16 in sq, "| 17 in sq:", 17 in sq, "(free __contains__)")
print("sq.index(9)  :", sq.index(9), "(free)")
print("sq.count(4)  :", sq.count(4), "(free)")
print("list(reversed(sq)):", list(reversed(sq)), "(free __reversed__)")
def assign():
    sq[0] = 1
for bad, label in ((lambda: sq[99], "sq[99]"), (lambda: sq["a"], "sq['a']"),
                   (lambda: sq.index(7), "sq.index(7)"), (assign, "sq[0] = 1")):
    try:
        bad()
    except (IndexError, TypeError, ValueError) as e:
        print(f"{label:<11} -> {type(e).__name__}: {e or '(no message)'}")
print("# - There is no __setitem__, so it is read-only - exactly like tuple and range.")

# 06. The Old Sequence-Iteration Fallback (Only __getitem__)
# ------------------------------------
# - Before __iter__ existed, `for` worked by calling obj[0], obj[1], ... until IndexError.
#   Python STILL does this if your class has __getitem__ but no __iter__.
# - Gotcha 1: isinstance(obj, Iterable) is False (it only looks for __iter__) even though
#   iter(obj) works. The only reliable test for "can I loop over it" is calling iter().
# - Gotcha 2: the fallback needs IndexError. A dict-style __getitem__ raising KeyError breaks it.
class OldStyle:
    def __getitem__(self, i):
        if i >= 3:
            raise IndexError
        return i * 10

class LooksLikeDict:
    def __getitem__(self, key):
        return {"a": 1}[key]                   # KeyError for any missing key, e.g. 0

old = OldStyle()
print("\n# 06. The Old Sequence-Iteration Fallback")
print("list(old)        :", list(old))
print("20 in old        :", 20 in old, "(`in` also falls back to looping)")
print("isinstance(old, Iterable):", isinstance(old, Iterable), "<- False, yet it loops")
print("type(iter(old))  :", type(iter(old)).__name__, "(Python wraps it in a sequence iterator)")
try:
    reversed(old)
except TypeError as e:
    print("reversed(old)    -> TypeError:", e, "(needs __len__ + __getitem__, or __reversed__)")
try:
    list(LooksLikeDict())
except KeyError as e:
    print("list(LooksLikeDict()) -> KeyError:", e, "(starts at 0, wanted IndexError to stop)")

# 07. A MutableSequence Subclass - insert + __setitem__ + __delitem__
# ------------------------------------
# - Abstract: __getitem__, __setitem__, __delitem__, __len__, insert.
# - Free: everything from Sequence PLUS append, extend, pop, remove, reverse, clear, +=.
#   Notice append(x) is just insert(len(self), x) - so insert is the one real mutator.
class Tape(MutableSequence):
    def __init__(self, items=()):
        self._items = list(items)
        self.inserts = 0                       # counts how often the free methods call insert
    def __getitem__(self, index):
        return self._items[index]              # delegating handles int, negative, slice, IndexError
    def __setitem__(self, index, value):
        self._items[index] = value
    def __delitem__(self, index):
        del self._items[index]
    def __len__(self):
        return len(self._items)
    def insert(self, index, value):
        self.inserts += 1
        self._items.insert(index, value)
    def __repr__(self):
        return f"Tape({self._items})"

t = Tape([1, 2, 3])
print("\n# 07. MutableSequence Subclass")
print("start          :", t)
t.append(4);            print("t.append(4)     :", t, "| insert calls so far:", t.inserts)
t.extend([5, 6]);       print("t.extend([5,6]):", t, "| insert calls so far:", t.inserts, "(extend -> append -> insert)")
print("t.pop()        :", t.pop(), "->", t)
print("t.pop(0)       :", t.pop(0), "->", t)
t.remove(3);            print("t.remove(3)    :", t)
t.reverse();            print("t.reverse()    :", t)
t += [7, 8];            print("t += [7, 8]    :", t, "(__iadd__ is free and mutates in place)")
print("t.index(7)     :", t.index(7), "| t.count(7):", t.count(7), "| 7 in t:", 7 in t)
t.clear();              print("t.clear()      :", t)
# What MutableSequence does NOT give you (list has these, the ABC doesn't):
tt = Tape([3, 1, 2])
print("hasattr(tt, 'sort')  :", hasattr(tt, "sort"), "| hasattr(tt, 'copy'):", hasattr(tt, "copy"))
print("Tape([1]) == Tape([1]):", Tape([1]) == Tape([1]), "(Sequence defines no __eq__ -> identity)")
try:
    tt + tt
except TypeError as e:
    print("tt + tt -> TypeError:", e, "(no __add__ either)")
print("sorted(tt)     :", sorted(tt), "(works via __iter__, returns a plain list)")
print("# - Need sort/copy/==/+? Add them yourself, or build on UserList (section 11).")

# 08. A Case-Insensitive MutableMapping
# ------------------------------------
# - Abstract: __getitem__, __setitem__, __delitem__, __iter__, __len__.
# - Free: get, setdefault, pop, popitem, clear, update, keys, values, items, in, ==, !=.
# - Every free method is built ON the five you wrote, so putting .lower() in just
#   __getitem__/__setitem__/__delitem__ makes get/pop/update/setdefault/in case-insensitive too.
class CIDict(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._data = {}
        self.update(*args, **kwargs)           # free update() calls OUR __setitem__ for each pair
    def __getitem__(self, key):
        return self._data[key.lower()]
    def __setitem__(self, key, value):
        self._data[key.lower()] = value
    def __delitem__(self, key):
        del self._data[key.lower()]
    def __iter__(self):
        return iter(self._data)
    def __len__(self):
        return len(self._data)
    def __repr__(self):
        return f"CIDict({self._data})"

headers = CIDict({"Content-Type": "text/html"}, Accept="*/*")   # dict AND kwargs both route via __setitem__
print("\n# 08. Case-Insensitive MutableMapping")
print("headers              :", headers, "(keys stored lowercase)")
print("headers['CONTENT-TYPE']:", headers["CONTENT-TYPE"])
print("'ACCEPT' in headers  :", "ACCEPT" in headers, "(free __contains__ built on __getitem__)")
print("headers.get('accept'):", headers.get("accept"), "| .get('x', 'dflt'):", headers.get("x", "dflt"))
print("setdefault('X-Id', 7):", headers.setdefault("X-Id", 7), "->", headers)
headers.update({"ACCEPT": "application/json"})
print("update({'ACCEPT': ..}):", headers, "(overwrote 'accept', no duplicate)")
print("pop('x-ID')          :", headers.pop("x-ID"), "->", headers)
print("keys / values / items:", list(headers.keys()), list(headers.values()), list(headers.items()))
print("len(headers)         :", len(headers))
print("== plain dict (lowercase keys):", headers == {"content-type": "text/html", "accept": "application/json"})
print("== plain dict (Mixed case)    :", headers == {"Content-Type": "text/html", "Accept": "application/json"},
      "(the OTHER side is a plain dict and compares exactly)")
print("popitem()            :", headers.popitem(), "->", headers)
try:
    headers[42] = "x"
except AttributeError as e:
    print("headers[42] = 'x' -> AttributeError:", e, "(ints have no .lower(); validate/convert if keys may vary)")

# 09. A Small Ordered Set - Set ABC and the Set-Operator Mixins
# ------------------------------------
# - Abstract: __contains__, __iter__, __len__. That's all.
# - Free: <, <=, >, >=, ==, !=, &, |, -, ^, isdisjoint (and reflected versions).
# - Results are built with cls._from_iterable(...), which defaults to cls(iterable),
#   so your constructor MUST accept an iterable (or override _from_iterable).
# - Set is the READ-ONLY set shape (like frozenset). add/discard come from MutableSet.
class OrderedSet(Set):
    def __init__(self, iterable=()):
        self._items = dict.fromkeys(iterable)  # dict keeps insertion order; values unused
    def __contains__(self, item):
        return item in self._items
    def __iter__(self):
        return iter(self._items)
    def __len__(self):
        return len(self._items)
    def __repr__(self):
        return f"OrderedSet({list(self._items)})"

a = OrderedSet([3, 1, 2])
b = OrderedSet([2, 5, 3])
print("\n# 09. OrderedSet (Set ABC)")
print("a =", a, "| b =", b)
print("a & b :", a & b, "(intersection - order follows b, the right operand!)")
print("a | b :", a | b)
print("a - b :", a - b)
print("a ^ b :", a ^ b, "(symmetric difference)")
print("OrderedSet([2,3]) <= a :", OrderedSet([2, 3]) <= a, "| < a:", OrderedSet([2, 3]) < a, "| a <= a:", a <= a, "| a < a:", a < a)
print("a >= OrderedSet([1]) :", a >= OrderedSet([1]))
print("a == OrderedSet([2,1,3]) :", a == OrderedSet([2, 1, 3]), "(order ignored, like a real set)")
print("a == {1, 2, 3} :", a == {1, 2, 3}, "(any Set compares equal by contents)")
print("a.isdisjoint([9]):", a.isdisjoint([9]))
print("a | {9} :", a | {9}, "| {9} | a :", {9} | a, "(set.__or__ gave up -> Set.__ror__; see 06 section 16)")
print("hasattr(a, 'add')   :", hasattr(a, "add"), "(read-only; add/discard need MutableSet)")
try:
    hash(a)
except TypeError as e:
    print("hash(a) -> TypeError:", e, "(Set defines __eq__ so it is unhashable; use Set._hash() if needed)")

# 10. Gotcha: Subclassing Builtins (dict/list) Does NOT Route Through Your Overrides
# ------------------------------------
# - CPython's builtin dict/list call their own C code directly for __init__, update(),
#   setdefault(), extend() ... they do NOT go through your overridden __setitem__/append.
# - So a "validating" dict subclass is validating only for d[k] = v. Everything else bypasses it.
# - Fixes: subclass UserDict / MutableMapping (pure Python, everything routes through
#   __setitem__), or override EVERY writer.
class DoublingDict(dict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value * 2)    # "rule": every stored value is doubled

class DoublingUserDict(UserDict):
    def __setitem__(self, key, value):
        super().__setitem__(key, value * 2)

class DoublingMapping(MutableMapping):
    def __init__(self, *args, **kwargs):
        self._d = {}
        self.update(*args, **kwargs)
    def __getitem__(self, k): return self._d[k]
    def __setitem__(self, k, v): self._d[k] = v * 2
    def __delitem__(self, k): del self._d[k]
    def __iter__(self): return iter(self._d)
    def __len__(self): return len(self._d)
    def __repr__(self): return f"{type(self).__name__}({self._d})"

def probe(cls):
    """Store the value 1 five different ways; correct behaviour is always 2."""
    d = cls()
    d["a"] = 1
    r = {"[]=": dict(d)}
    r["ctor kwargs"] = dict(cls(b=1))
    r["ctor dict"] = dict(cls({"c": 1}))
    d2 = cls(); d2.update({"d": 1}); r["update()"] = dict(d2)
    d3 = cls(); d3.setdefault("e", 1); r["setdefault()"] = dict(d3)
    return r

print("\n# 10. Subclassing dict vs UserDict vs MutableMapping (every stored value should be doubled -> 2)")
for cls in (DoublingDict, DoublingUserDict, DoublingMapping):
    print(f"{cls.__name__:<17}", probe(cls))
print("# - DoublingDict: only d['a'] = 1 is doubled; constructor, update(), setdefault() bypass the hook.")
print("# - DoublingUserDict and DoublingMapping: all five paths give 2.")

class LoudGet(dict):
    def __getitem__(self, key):
        return f"<{super().__getitem__(key)}>"
lg = LoudGet(a=1)
print("LoudGet: lg['a'] =", lg["a"], "| lg.get('a') =", lg.get("a"), "(get() ignores the __getitem__ override)")

class PositiveList(list):
    def append(self, x):
        if x < 0:
            raise ValueError("no negatives")
        super().append(x)
pl = PositiveList([-5])                        # constructor bypasses append
pl.extend([-6])                                # extend bypasses append
pl += [-7]                                     # += bypasses append
print("PositiveList after ctor/extend/+= with negatives:", pl, "(append's check never ran)")
try:
    pl.append(-1)
except ValueError as e:
    print("pl.append(-1) -> ValueError:", e, "(only the one path you overrode)")

# MutableSequence routes everything through insert, so one check covers append/extend/+=
class EvenTape(Tape):
    def insert(self, index, value):
        if value % 2:
            raise ValueError(f"{value} is odd")
        super().insert(index, value)
et = EvenTape([2, 4])
for label, action in (("append(3)", lambda: et.append(3)),
                      ("extend([6, 7])", lambda: et.extend([6, 7])),
                      ("+= [9]", lambda: et.__iadd__([9]))):
    try:
        action()
    except ValueError as e:
        print(f"EvenTape.{label:<15} -> ValueError: {e}")
print("EvenTape after attempts:", et, "(extend added 6 before rejecting 7 - not atomic)")
print("# - Careful: __setitem__ is a SEPARATE writer on MutableSequence (et[0] = 3 would bypass insert).")

# 11. UserList / UserDict / UserString - When to Use Them
# ------------------------------------
# - collections.UserList/UserDict/UserString are pure-Python wrappers around a REAL list/dict/str
#   kept in the `.data` attribute. They behave like the builtin but are safe to subclass.
# - Use them when: you want list/dict/str behaviour with a few CHANGES, and you don't need
#   to pass it to C code that demands a true list/dict/str.
# - Use MutableMapping/MutableSequence (sections 07-08) when your storage is NOT a plain
#   list/dict (a file, a database, a cache, a view of other data).
# - Subclass dict/list directly only to ADD methods or defaults (like __missing__) without
#   changing how existing writes work.
ul = UserList([1, 2, 3])
ud = UserDict({"a": 1})
us = UserString("hello")
print("\n# 11. UserList / UserDict / UserString")
print("ul.data           :", ul.data, type(ul.data).__name__, "(the real list inside)")
print("type(ul[0:2])     :", type(ul[0:2]).__name__, "(slices come back as UserList, not list)")
print("us.upper()        :", repr(us.upper()), type(us.upper()).__name__, "(methods return UserString)")
print("isinstance(ul, list):", isinstance(ul, list), "| isinstance(ul, MutableSequence):", isinstance(ul, MutableSequence))
print("isinstance(ud, dict):", isinstance(ud, dict), "| isinstance(ud, MutableMapping):", isinstance(ud, MutableMapping))
print("isinstance(us, str) :", isinstance(us, str), "| isinstance(us, Sequence):", isinstance(us, Sequence))
try:
    json.dumps(ul)
except TypeError as e:
    print("json.dumps(ul) -> TypeError:", e)
print("json.dumps(ul.data):", json.dumps(ul.data), "(unwrap .data when real types are required)")

class EvenList(UserList):
    def append(self, item):
        if item % 2:
            raise ValueError(f"{item} is odd")
        super().append(item)
el = EvenList([2])
el.extend([3])                                 # UserList.extend writes self.data directly
print("EvenList after extend([3]):", el.data, "(UserList is nicer than list but still has many separate writers)")

# 12. ABCs in Type Hints and isinstance - Accept General, Return Concrete
# ------------------------------------
# - Parameters: ask for the MOST GENERAL ABC that has what you need.
#     only loop once        -> Iterable[T]       (lists, tuples, sets, generators, files...)
#     need len() / loop twice -> Collection[T]   or Sequence[T] if you index
#     need indexing         -> Sequence[T]
#     only read key->value  -> Mapping[K, V]     (dict, MappingProxyType, CIDict ...)
# - Return values: return a CONCRETE type (list[str], dict[str, int]). Callers can then index,
#   mutate and len() without guessing; a vague return type only hides what you really give.
# - Type hints are NOT enforced at runtime - a checker (mypy/pyright) reads them. These
#   functions run fine with anything that quacks right.
def total(numbers: Iterable[int]) -> int:
    return sum(numbers)

def first_and_last(items: Sequence[str]) -> list[str]:
    return [items[0], items[-1]]

def describe(scores: Mapping[str, int]) -> list[str]:
    return [f"{name}={score}" for name, score in sorted(scores.items())]

print("\n# 12. ABCs in Type Hints and isinstance")
print("total(list)      :", total([1, 2, 3]))
print("total(tuple)     :", total((1, 2, 3)))
print("total(set)       :", total({1, 2, 3}))
print("total(range)     :", total(range(4)))
print("total(generator) :", total(i for i in range(4)))
print("first_and_last(list) :", first_and_last(["a", "b", "c"]))
print("first_and_last('xyz'):", first_and_last("xyz"), "(a str IS a Sequence[str] - so 'xyz' passes silently!)")
print("describe(dict)   :", describe({"b": 2, "a": 1}))
print("describe(CIDict) :", describe(CIDict(b=2, a=1)))
print("describe(read-only view):", describe(types.MappingProxyType({"z": 26})))
print("describe(OrderedDict)   :", describe(OrderedDict(q=1)))

gen = (i for i in range(3))
print("Iterable gotcha: two passes over a generator ->", total(gen), "then", total(gen), "(second is 0: already consumed)")
print("# - If you loop twice, annotate Collection/Sequence (generators are rejected by a checker),")
print("#   or materialise first: items = list(items).")

def flatten_one_level(value):
    """isinstance with an ABC for runtime dispatch - exclude str/bytes or you recurse forever."""
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        return [x for part in value for x in part]
    return [value]
print("flatten_one_level([[1, 2], (3,)]):", flatten_one_level([[1, 2], (3,)]))
print("flatten_one_level('ab')          :", flatten_one_level("ab"), "(str excluded on purpose)")
try:
    isinstance([1], Iterable[int])
except TypeError as e:
    print("isinstance([1], Iterable[int]) -> TypeError:", e, "(use bare Iterable at runtime; Iterable[int] is for hints)")

# 13. Forgetting an Abstract Method - The TypeError You Will See
# ------------------------------------
# - The error appears when you INSTANTIATE, not when you define the class and not when
#   you call the missing method. (ABC mechanics: see 05-Abstraction.py sections 05-07.)
# - It names the missing methods, so just read it and add them.
class NoLen(Sequence):
    def __getitem__(self, i):
        return i

class HalfMutable(MutableSequence):
    def __getitem__(self, i): return i
    def __len__(self): return 0
    # forgot __setitem__, __delitem__ and insert

class HalfMap(MutableMapping):
    def __getitem__(self, k): return k
    def __iter__(self): return iter(())
    def __len__(self): return 0
    def __setitem__(self, k, v): pass
    # forgot __delitem__

print("\n# 13. Forgetting an Abstract Method")
for cls in (NoLen, HalfMutable, HalfMap):
    try:
        cls()
    except TypeError as e:
        print(f"{cls.__name__}() -> TypeError: {e}")

# 14. Cheat Table - ABC -> You Must Write -> You Get Free
# ------------------------------------
#   ABC               You must write (abstract)                 You get free (mixins)
#   ---------------   ---------------------------------------   --------------------------------------------------
#   Sized             __len__                                   -
#   Iterable          __iter__                                  -
#   Container         __contains__                              -
#   Collection        __len__, __iter__, __contains__           -
#   Iterator          __next__                                  __iter__ (returns self)
#   Reversible        __reversed__, __iter__                    -
#   Sequence          __getitem__, __len__                      __contains__, __iter__, __reversed__, index, count
#   MutableSequence   Sequence's + __setitem__, __delitem__,    append, extend, pop, remove, reverse, clear, +=
#                     insert
#   Mapping           __getitem__, __iter__, __len__            __contains__, keys, items, values, get, ==, !=
#   MutableMapping    Mapping's + __setitem__, __delitem__      pop, popitem, clear, update, setdefault
#   Set               __contains__, __iter__, __len__           <, <=, >, >=, ==, &, |, -, ^, isdisjoint
#   MutableSet        Set's + add, discard                      remove, pop, clear, |=, &=, -=, ^=
# - NOT free anywhere: sort(), copy(), + and * on sequences, nice __repr__, ==/hash on MutableSequence.
# - The printed check below compares the abstract column against the real classes.
expected = {
    Sized: {"__len__"}, Iterable: {"__iter__"}, Container: {"__contains__"},
    Collection: {"__len__", "__iter__", "__contains__"}, Iterator: {"__next__"},
    Sequence: {"__getitem__", "__len__"},
    MutableSequence: {"__getitem__", "__len__", "__setitem__", "__delitem__", "insert"},
    Mapping: {"__getitem__", "__iter__", "__len__"},
    MutableMapping: {"__getitem__", "__iter__", "__len__", "__setitem__", "__delitem__"},
    Set: {"__contains__", "__iter__", "__len__"},
    MutableSet: {"__contains__", "__iter__", "__len__", "add", "discard"},
}
print("\n# 14. Cheat table above (see comments) - verified against the real classes:")
for abc, names in expected.items():
    assert abc.__abstractmethods__ == names, (abc, abc.__abstractmethods__)
print(f"All {len(expected)} abstract-method sets match the table.")
