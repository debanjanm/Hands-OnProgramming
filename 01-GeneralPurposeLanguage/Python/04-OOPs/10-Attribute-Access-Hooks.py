import copy

# 01. The Four Attribute Operations and Their Hooks
# ------------------------------------
# - Reading, writing, deleting and listing attributes each map to a dunder:
#     obj.x          -> __getattribute__ (always), then __getattr__ (only if that failed)
#     obj.x = v      -> __setattr__
#     del obj.x      -> __delattr__
#     dir(obj)       -> __dir__
# - Every class gets default versions from `object`. Overriding them lets you log,
#   validate, delegate, or freeze attribute access.
# - Descriptors (see 09-Descriptors-And-Properties.py) are invoked INSIDE the default
#   object.__getattribute__ / __setattr__, so these hooks sit one level above them.
class Spy:
    def __getattribute__(self, name):
        print(f"      -> __getattribute__({name!r})")
        return super().__getattribute__(name)
    def __getattr__(self, name):
        print(f"      -> __getattr__({name!r})")
        return "fallback"
    def __setattr__(self, name, value):
        print(f"      -> __setattr__({name!r}, {value!r})")
        super().__setattr__(name, value)
    def __delattr__(self, name):
        print(f"      -> __delattr__({name!r})")
        super().__delattr__(name)

s = Spy()
print("s.a = 1:");        s.a = 1
print("s.a:");            s.a
print("s.missing:");      s.missing
print("del s.a:");        del s.a

# 02. __getattr__ : The Fallback Hook
# ------------------------------------
# - Called ONLY when normal lookup fails (AttributeError would otherwise be raised).
# - Great for defaults, computed names, and delegation.
# - It must raise AttributeError for names it does not handle, otherwise hasattr(),
#   copy, pickle and friends get confused.
class Defaults:
    def __init__(self):
        self.real = "I exist"
    def __getattr__(self, name):
        if name.startswith("get_"):
            return f"computed {name[4:]}"
        raise AttributeError(f"{type(self).__name__!r} object has no attribute {name!r}")

dflt = Defaults()
print(dflt.real, "|", dflt.get_color)
print("hasattr(dflt, 'nothing'):", hasattr(dflt, "nothing"))
try:
    dflt.nothing
except AttributeError as e:
    print("AttributeError:", e)

# 03. __getattribute__ : The Hook for EVERY Read
# ------------------------------------
# - Called for every attribute read, including ones that exist, and including
#   methods and dunder-looking names you access explicitly.
# - It runs first; __getattr__ is only reached if it raises AttributeError.
# - Quick rule: use __getattr__ unless you really need to intercept existing attributes.
#   Use __getattribute__ with great care: it is easy to break and slows every access.
#   (Implicit dunder calls like len(obj) skip it, see section 14.)
class Counted:
    def __init__(self):
        object.__setattr__(self, "reads", 0)
        object.__setattr__(self, "value", 10)
    def __getattribute__(self, name):
        if name != "reads":
            object.__setattr__(self, "reads", object.__getattribute__(self, "reads") + 1)
        return object.__getattribute__(self, name)

cn = Counted()
cn.value; cn.value; cn.value
print("value read 3 times -> reads counter:", cn.reads)

# 04. The Classic Gotcha: Infinite Recursion
# ------------------------------------
# - Inside __getattribute__, writing self.anything calls __getattribute__ again... forever.
# - Same for __setattr__ doing self.x = v, and __getattr__ touching a missing self.attr.
# - Fix: go through object (or super()) so the hook is not re-entered.
class Broken:
    def __getattribute__(self, name):
        return self.__dict__[name]          # self.__dict__ is itself an attribute read!

try:
    Broken().x
except RecursionError:
    print("Broken.__getattribute__ -> RecursionError (self.__dict__ re-enters the hook)")

class BrokenSet:
    def __setattr__(self, name, value):
        self.__dict__[name] = value          # reads self.__dict__ -> fine for set...
        self.last = name                     # ...but this calls __setattr__ again

try:
    BrokenSet().a = 1
except RecursionError:
    print("BrokenSet.__setattr__ -> RecursionError (self.last = ... re-enters the hook)")

class Fixed:
    def __getattribute__(self, name):
        return super().__getattribute__(name)   # or object.__getattribute__(self, name)
    def __setattr__(self, name, value):
        super().__setattr__(name, value)

fx = Fixed()
fx.a = 5
print("Fixed works:", fx.a)

# 05. __getattr__ Recursion During Copy/Pickle (The Sneaky Variant)
# ------------------------------------
# - copy/pickle build a blank object WITHOUT calling __init__, then look up things
#   like __setstate__ / __deepcopy__ on it. If your __getattr__ reads self._data,
#   and _data does not exist yet, then __getattr__('_data') calls itself forever.
# - Fix: guard private/dunder names and raise AttributeError for them.
class Wrapper:
    def __init__(self, data):
        self._data = data
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)           # the guard
        return getattr(self._data, name)

w = Wrapper([3, 1, 2])
w2 = copy.deepcopy(w)
print("deepcopy of guarded wrapper works:", w2._data, "| w2.count(1) ->", w2.count(1))

class WrapperNoGuard:
    def __init__(self, data):
        self._data = data
    def __getattr__(self, name):
        return getattr(self._data, name)

try:
    copy.copy(WrapperNoGuard([1]))
except RecursionError:
    print("unguarded __getattr__ + copy.copy -> RecursionError")

# 06. __setattr__ : Intercept Every Assignment
# ------------------------------------
# - Called for self.x = v EVERYWHERE, including inside __init__.
# - Good for validation, normalisation, change tracking. Always finish with
#   super().__setattr__(...) so the value actually gets stored.
class Tracked:
    def __init__(self, **kw):
        object.__setattr__(self, "_changes", [])
        for k, v in kw.items():
            setattr(self, k, v)
    def __setattr__(self, name, value):
        if name == "age" and value < 0:
            raise ValueError("age cannot be negative")
        if isinstance(value, str):
            value = value.strip()
        self._changes.append(name)
        super().__setattr__(name, value)

tr = Tracked(name="  Asha  ", age=30)
tr.age = 31
print("name:", repr(tr.name), "| age:", tr.age, "| changes:", tr._changes)
try:
    tr.age = -1
except ValueError as e:
    print("ValueError:", e)

# 07. __delattr__ and __dir__
# ------------------------------------
# - __delattr__ guards `del obj.x`.
# - __dir__ controls what dir(obj) lists (tab-completion, introspection). It should
#   return an iterable of names; dir() sorts it for you.
# - Gotcha: __dir__ only changes the LISTING, it does not make an attribute exist.
class Protected:
    def __init__(self):
        self.keep = 1
        self.drop = 2
    def __delattr__(self, name):
        if name == "keep":
            raise AttributeError("keep cannot be deleted")
        super().__delattr__(name)
    def __dir__(self):
        return ["keep", "drop", "virtual_attr"]
    def __getattr__(self, name):
        if name == "virtual_attr":
            return "I come from __getattr__"
        raise AttributeError(name)

pr = Protected()
del pr.drop
try:
    del pr.keep
except AttributeError as e:
    print("AttributeError:", e)
print("dir(pr):", dir(pr))
print("virtual_attr:", pr.virtual_attr, "| 'drop' still listed even though deleted:", "drop" in dir(pr))

# 08. The Built-in Functions: getattr, setattr, hasattr, delattr
# ------------------------------------
# - Use them when the attribute NAME is a string in a variable (dynamic access).
# - getattr(obj, name, default) returns the default instead of raising.
# - hasattr is just "try getattr, catch AttributeError" - so it RUNS property code
#   and __getattr__, and hides AttributeErrors raised inside a property (gotcha!).
class Sample:
    answer = 42
    @property
    def broken(self):
        return self.not_there                  # AttributeError inside the property

sm = Sample()
print("getattr with default:", getattr(sm, "nope", "default"))
setattr(sm, "dynamic", "set by name")
print("setattr/getattr:", getattr(sm, "dynamic"), "| hasattr:", hasattr(sm, "dynamic"))
delattr(sm, "dynamic")
print("after delattr, hasattr:", hasattr(sm, "dynamic"))
print("hasattr(sm, 'broken') lies (property exists but raised):", hasattr(sm, "broken"))
for field in ("answer", "nope"):
    print(f"   field {field!r} ->", getattr(sm, field, "<missing>"))

# 09. vars(), __dict__ and Where Attributes Really Live
# ------------------------------------
# - vars(obj) is obj.__dict__ - the plain dict holding instance attributes.
# - Class attributes, methods and descriptors live in Class.__dict__ (a read-only
#   mappingproxy, so you cannot assign into it).
# - Gotcha: classes using __slots__ have no __dict__ (see 02-Encapsulation.py).
# - Gotcha: writing obj.__dict__[name] = v BYPASSES __setattr__ and data descriptors.
class Where:
    shared = "class attribute"
    def __init__(self):
        self.mine = "instance attribute"
    def method(self):
        pass

wh = Where()
print("vars(wh):", vars(wh))
print("class dict keys (no dunders):", [k for k in vars(Where) if not k.startswith("__")])
print("type of Where.__dict__:", type(Where.__dict__).__name__)
try:
    Where.__dict__["x"] = 1
except TypeError as e:
    print("cannot assign into class __dict__:", e)

class Slotty:
    __slots__ = ("a",)

try:
    vars(Slotty())
except TypeError as e:
    print("vars() on __slots__ object:", e)

# 10. Proxy / Delegation with __getattr__
# ------------------------------------
# - Wrap another object and forward whatever you do not handle yourself.
# - Composition + delegation avoids inheritance when you only want some behaviour.
#   (Design view: see 08-SOLID-Principles.py.)
# - Gotcha: __getattr__ is NOT used for implicit dunder lookups such as len(proxy) or
#   proxy[0]; Python looks those up on the TYPE. Define them explicitly (section 14).
class LoggingProxy:
    def __init__(self, target):
        object.__setattr__(self, "_target", target)
    def __getattr__(self, name):
        attr = getattr(self._target, name)
        if callable(attr):
            def wrapper(*args, **kwargs):
                print(f"      [log] calling {name}{args}")
                return attr(*args, **kwargs)
            return wrapper
        return attr
    def __setattr__(self, name, value):
        print(f"      [log] set {name} = {value!r}")
        setattr(self._target, name, value)

prox = LoggingProxy([])
prox.append(1)
prox.append(2)
print("proxied list contents:", prox._target)
try:
    len(prox)
except TypeError as e:
    print("len(proxy) -> TypeError:", e)

class Config:
    def __init__(self):
        self.debug = False

cfg = LoggingProxy(Config())
cfg.debug = True
print("config.debug through proxy:", cfg.debug)

# 11. Dict-Like Attribute Access (Bunch / AttrDict)
# ------------------------------------
# - Let d.key work like d["key"]. Handy for config and JSON-style data.
# - Gotchas: keys that clash with real methods (like "items") are shadowed by the
#   method; keys that are not valid identifiers ("my-key") still need d["my-key"].
class AttrDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name) from None
    def __setattr__(self, name, value):
        self[name] = value
    def __delattr__(self, name):
        try:
            del self[name]
        except KeyError:
            raise AttributeError(name) from None

ad = AttrDict(host="localhost", port=8080)
ad.debug = True
print(ad.host, ad.port, ad.debug, "| as dict:", dict(ad))
ad["items"] = "my data"
print("ad.items is the dict METHOD, not the key:", callable(ad.items), "| ad['items']:", ad["items"])

# 12. Read-Only / Frozen Objects
# ------------------------------------
# - Block __setattr__ and __delattr__ after construction to make an immutable object.
# - Python does not have true immutability for user classes: object.__setattr__ can
#   still force a value in (dataclasses use exactly this trick: frozen=True, see 06).
class Frozen:
    def __init__(self, x, y):
        object.__setattr__(self, "x", x)         # bypass our own block, once
        object.__setattr__(self, "y", y)
    def __setattr__(self, name, value):
        raise AttributeError(f"cannot assign to {name!r}: object is frozen")
    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}: object is frozen")
    def __repr__(self):
        return f"Frozen(x={self.x}, y={self.y})"

fr = Frozen(1, 2)
for label, action in [("assign", lambda: setattr(fr, "x", 9)), ("delete", lambda: delattr(fr, "y"))]:
    try:
        action()
    except AttributeError as e:
        print(f"{label}: {e}")
object.__setattr__(fr, "x", 99)
print("the loophole object.__setattr__ still works:", fr)

# 13. Restricting Attributes (Typo Guard) - __setattr__ vs __slots__
# ------------------------------------
# - A common bug: obj.colour = "red" when you meant obj.color silently creates a new
#   attribute. Two cures: __slots__ (fast, structural) or a __setattr__ allow-list.
class Strict:
    _allowed = {"color", "size"}
    def __setattr__(self, name, value):
        if name not in self._allowed:
            raise AttributeError(f"{name!r} is not an allowed attribute")
        super().__setattr__(name, value)

st = Strict()
st.color = "red"
try:
    st.colour = "blue"
except AttributeError as e:
    print("typo caught:", e)

class WithSlots:
    __slots__ = ("color", "size")

ws = WithSlots()
try:
    ws.colour = "blue"
except AttributeError as e:
    print("__slots__ also catches it:", e)

# 14. Implicit Special-Method Lookup Skips __getattr__ and __getattribute__
# ------------------------------------
# - len(x), x[0], x + y, str(x), for ... in x look up __len__ etc. on type(x), never
#   on the instance, so instance-level hooks and instance attributes do not apply.
# - That is why proxies must define dunders explicitly, and why this trick fails:
class Trick:
    def __getattr__(self, name):
        if name == "__len__":
            return lambda: 5
        raise AttributeError(name)

tk = Trick()
print("explicit tk.__len__() works:", tk.__len__())
try:
    len(tk)
except TypeError as e:
    print("len(tk) ignores __getattr__:", e)

# 15. Properties/Descriptors vs Hooks: Which Runs When?
# ------------------------------------
# - Data descriptors and properties are found INSIDE object.__getattribute__. If you
#   override __getattribute__ without calling super, properties stop working.
# - __getattr__ is only the last resort: an AttributeError raised inside a property
#   getter makes Python fall through to __getattr__ too (confusing error messages!).
class Quirk:
    @property
    def prop(self):
        raise AttributeError("property failed internally")
    def __getattr__(self, name):
        return f"__getattr__ rescued {name!r}"

print("AttributeError inside a property triggers __getattr__:", Quirk().prop)

# 16. Attribute Lookup Order - The Full Recap
# ------------------------------------
# - obj.name goes through type(obj).__getattribute__, which (by default) does:
#     1. data descriptor found on the class MRO      -> its __get__
#     2. obj.__dict__[name]                          -> that value
#     3. non-data descriptor / plain class attribute -> its __get__ / the value
#     4. AttributeError raised
#   then, ONLY if step 4 happened, type(obj).__getattr__(obj, name) is tried.
# - Writes: obj.name = v -> type(obj).__setattr__ -> data descriptor __set__ if present,
#   else obj.__dict__[name] = v.
# - Proof with a trace through all levels:
class DataD:
    def __get__(self, obj, objtype=None):
        return "1-data descriptor"
    def __set__(self, obj, value):
        pass

class NonDataD:
    def __get__(self, obj, objtype=None):
        return "3-non-data descriptor"

class Order:
    a = DataD()
    b = NonDataD()
    c = "3-plain class attribute"
    def __getattr__(self, name):
        return "5-__getattr__"

o = Order()
o.__dict__.update(a="2-instance dict", b="2-instance dict", c="2-instance dict")
print("a (data desc + dict):     ", o.a)
print("b (non-data + dict):      ", o.b)
print("c (plain class + dict):   ", o.c)
del o.__dict__["c"]
print("c after removing from dict:", o.c)
print("zzz (nothing anywhere):   ", o.zzz)

# 17. Class-Level Access Is Different: type.__getattribute__
# ------------------------------------
# - Order.attr (reading on the class) uses type.__getattribute__, which checks the
#   metaclass first (data descriptors), then the class MRO __dict__s, then the metaclass.
# - Instance hooks like __getattr__ defined in the class do NOT apply to the class itself.
#   Class-level dynamic attributes need a metaclass __getattr__
#   (see 11-Metaclasses-And-Class-Creation.py).
try:
    Order.zzz
except AttributeError as e:
    print("class-level miss ignores instance __getattr__:", e)

# 18. Summary: Choosing a Hook
# ------------------------------------
# - Missing names / defaults / delegation   -> __getattr__
# - Intercept ALL reads (rare)              -> __getattribute__ (+ super(), watch recursion)
# - Validate / track / freeze writes        -> __setattr__ (+ __delattr__)
# - Per-attribute rule reused on many names -> descriptor (09-Descriptors-And-Properties.py)
# - Single computed attribute               -> @property (02-Encapsulation.py)
# - Customise listing                       -> __dir__
print("Done: hooks always end in super().__xxx__ unless you really mean to replace storage.")
