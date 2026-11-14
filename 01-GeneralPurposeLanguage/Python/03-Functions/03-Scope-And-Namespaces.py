import builtins
import functools
import math
import sys
import types
from types import SimpleNamespace

# 01. Scope & Namespaces - Introduction
# ------------------------------------
# - A NAMESPACE is a mapping from names to objects (in CPython: a real dict).
# - A SCOPE is the region of source code where a namespace is directly reachable.
# - Every `x = ...`, `def f`, `class C`, `import m` just adds a key to some namespace.
# - "Where does this name live?" is the question behind most NameError,
#   UnboundLocalError and "why did my variable change?" bugs.
# - Closures, `global` and `nonlocal` are covered lightly in 02-Functions.py
#   (sections 10 and 20). This file is the full mental model behind them.

print("# 01. Scope & Namespaces - Introduction")
print("# ------------------------------------")
print("# - Namespace = name -> object mapping (a dict in CPython).")
print("# - Scope = the part of the code where that mapping is visible.")

# 02. globals() and locals() are real dicts
# ------------------------------------
# - globals() returns the module's namespace dict. Writing to it creates variables.
# - locals() at MODULE level is the very same dict as globals().
# - locals() inside a function is a snapshot dict of that call's local names.

print("\n# 02. globals() and locals() are real dicts")
print("# ------------------------------------")

site = "demo"
visits = 3
print("type(globals()):", type(globals()).__name__)
print("my own names in globals():", [k for k, v in globals().items() if not k.startswith("__") and not isinstance(v, types.ModuleType) and k != "SimpleNamespace"])
print("globals()['site'] ->", globals()["site"])
print("module level: locals() is globals() ->", locals() is globals())

# Writing to the dict creates a real variable - names are just dict keys.
globals()["created_by_dict"] = 42
print("created_by_dict (used as a plain name) ->", created_by_dict)


def show_locals(a, b=2):
    c = a + b
    return dict(locals())  # copy so we print a stable snapshot


print("locals() inside a function ->", show_locals(1))
print("(parameters are locals too; 'site' and 'visits' are NOT in there)")


def where_is_my_world():
    return where_is_my_world.__globals__ is globals()


print("function.__globals__ is the module dict ->", where_is_my_world())

# 03. __dict__ of a module, class and instance
# ------------------------------------
# - Module, class and instance each OWN a namespace stored in __dict__.
# - Attribute lookup `obj.name` is itself a namespace search: instance -> class -> bases.
# - Class __dict__ is a read-only mappingproxy (so you can't corrupt it by accident).

print("\n# 03. __dict__ of a module, class and instance")
print("# ------------------------------------")

print("math.__dict__['pi'] ->", math.__dict__["pi"], "(same as math.pi)")

scratch = types.ModuleType("scratch")  # build a module by hand
scratch.answer = 42
print("custom module's own names ->", [k for k in scratch.__dict__ if not k.startswith("__")])


class Dog:
    species = "canine"  # class attribute: lives in Dog.__dict__

    def __init__(self, name):
        self.name = name  # instance attribute: lives in rex.__dict__

    def speak(self):
        return f"{self.name} says woof"


rex = Dog("Rex")
print("type(Dog.__dict__) ->", type(Dog.__dict__).__name__)
print("Dog.__dict__ public names ->", [k for k in Dog.__dict__ if not k.startswith("__")])
print("rex.__dict__ ->", rex.__dict__)
print("rex.species (found on the class) ->", rex.species)
rex.species = "wolf"  # creates a NEW key in the instance dict, class untouched
print("after rex.species = 'wolf': rex.__dict__ ->", rex.__dict__, "| Dog.species ->", Dog.species)

# 04. LEGB - the lookup rule, step by step
# ------------------------------------
# When Python meets a bare NAME it searches these scopes, innermost first:
#   L  Local      - names assigned inside the current function (incl. parameters)
#   E  Enclosing  - local scopes of any outer functions (closures), nearest first
#   G  Global     - the module's top-level names
#   B  Built-in   - the `builtins` module (len, print, list, ...)
# First hit wins. No hit anywhere -> NameError.
# KEY FACT: for a function, Python decides at COMPILE time which names are
# local (anything assigned in the function body). Global vs built-in is
# resolved at RUN time by dict lookup. We can prove it by reading the code object.

print("\n# 04. LEGB - the lookup rule, step by step")
print("# ------------------------------------")

g_name = "I am a GLOBAL"


def outer():
    e_name = "I am ENCLOSING"

    def inner():
        l_name = "I am LOCAL"
        # one name from each level:
        return l_name, e_name, g_name, len  # len is a built-in

    return inner


def resolve(func, name):
    """Report which LEGB level a bare name resolves to for `func`."""
    code = func.__code__
    if name in code.co_varnames or name in code.co_cellvars:
        return "L (Local)"
    if name in code.co_freevars:
        return "E (Enclosing)"
    if name in code.co_names:
        if name in func.__globals__:
            return "G (Global)"
        if hasattr(builtins, name):
            return "B (Built-in)"
    return "not found -> NameError"


inner_fn = outer()
print("inner_fn() ->", inner_fn()[:3], "+ the len builtin")
for n in ("l_name", "e_name", "g_name", "len"):
    print(f"  {n:7} resolves to: {resolve(inner_fn, n)}")

print("\nWhat the compiler recorded for inner():")
print("  co_varnames (locals)  :", inner_fn.__code__.co_varnames)
print("  co_freevars (closure) :", inner_fn.__code__.co_freevars)
print("  co_names (G or B)     :", inner_fn.__code__.co_names)


def uses_missing():
    return definitely_not_defined_anywhere


try:
    uses_missing()
except NameError as e:
    print("\nNo level has it ->", type(e).__name__ + ":", e)

# Same name at every level: the innermost wins ("shadowing").
who = "global who"


def level_e():
    who = "enclosing who"

    def level_l():
        who = "local who"
        return who

    return level_l(), who


print("\nsame name 'who' at 3 levels ->", level_e()[0], "|", level_e()[1], "|", who)

# 05. global - rebind a module-level name from inside a function
# ------------------------------------
# - READING a global needs nothing special (LEGB finds it).
# - ASSIGNING makes a local unless you declare `global name` first.
# - Mutating a mutable global (list.append, dict[k] = v) is NOT assignment,
#   so it works without `global`. Only REBINDING the name needs it.

print("\n# 05. global - rebinding a module-level name")
print("# ------------------------------------")

hits = 0
log = []


def no_global():
    hits = 100  # creates a LOCAL 'hits'; module 'hits' untouched
    return hits


def with_global():
    global hits
    hits += 1


def mutate_without_global():
    log.append("event")  # mutation, not rebinding -> no 'global' needed


no_global()
print("after no_global()      : hits =", hits)
with_global()
with_global()
print("after 2x with_global() : hits =", hits)
mutate_without_global()
print("after log.append in fn : log  =", log)


def declare_new_global():
    global brand_new_global  # may not exist yet
    brand_new_global = "born inside a function"


declare_new_global()
print("`global` can even create a name ->", brand_new_global)

# 06. nonlocal - rebind a name in the nearest ENCLOSING function
# ------------------------------------
# - `nonlocal x` skips the local scope and targets the closest enclosing function scope.
# - The name MUST already exist there (checked at compile time).
# - It can never reach the global scope - that's what `global` is for.

print("\n# 06. nonlocal - rebinding an enclosing name")
print("# ------------------------------------")


def make_accumulator():
    total = 0

    def add(n):
        nonlocal total
        total += n
        return total

    return add


acc = make_accumulator()
print("acc(5), acc(10), acc(1) ->", acc(5), acc(10), acc(1))

try:
    compile("def f():\n    nonlocal ghost\n    ghost = 1\n", "<demo>", "exec")
except SyntaxError as e:
    print("nonlocal on a name that doesn't exist ->", type(e).__name__ + ":", e.msg)

# 07. The UnboundLocalError gotcha (read a global, then assign it)
# ------------------------------------
# - If a name is assigned ANYWHERE in a function body, it is local in the WHOLE
#   function - even on lines before the assignment, even in a branch that never runs.
# - Python decides this at compile time (it scans the body once), not line by line.
# - So `print(counter)` above `counter = ...` doesn't see the global; it reads
#   a local that has no value yet -> UnboundLocalError.

print("\n# 07. The UnboundLocalError gotcha")
print("# ------------------------------------")

counter = 10


def broken_increment():
    counter = counter + 1  # RHS reads local 'counter' - which isn't assigned yet
    return counter


try:
    broken_increment()
except UnboundLocalError as e:
    print("broken_increment ->", type(e).__name__ + ":", e)

print("compile-time proof: 'counter' in co_varnames ->", "counter" in broken_increment.__code__.co_varnames)

total = 500


def never_assigns():
    if False:
        total = 0  # never executes, but it still makes 'total' local!
    return total


try:
    never_assigns()
except UnboundLocalError as e:
    print("never_assigns ->", type(e).__name__ + ":", e)


def augmented_global():
    global counter
    counter += 1
    return counter


print("fix with `global counter` ->", augmented_global())
print("better fix: pass it in, return the new value (no hidden state):")


def increment(value):
    return value + 1


counter = increment(counter)
print("  counter =", counter)

# 08. The builtins module and __builtins__
# ------------------------------------
# - Built-ins (len, print, list, ValueError, ...) are just attributes of the
#   `builtins` module. That module is the last stop of the LEGB search.
# - In the script you run, `__builtins__` IS that module; in imported modules
#   CPython makes it a plain dict. Never rely on `__builtins__` - import builtins.

print("\n# 08. The builtins module")
print("# ------------------------------------")

print("builtins.len is len ->", builtins.len is len)
print("number of names in builtins ->", len(dir(builtins)), "(sample:", dir(builtins)[-6:], ")")
print("__builtins__ in a run script is the module ->", __builtins__ is builtins)

# 09. Shadowing built-ins (and recovering)
# ------------------------------------
# - Assigning to a name like `list`, `sum`, `max`, `id` in YOUR scope puts a key
#   in your namespace, found BEFORE the built-in. Built-in is untouched but hidden.
# - Recovery: `del name` removes your binding (built-in reappears),
#   or call `builtins.name` directly.

print("\n# 09. Shadowing built-ins")
print("# ------------------------------------")

list = [1, 2, 3]  # classic accident
try:
    list("abc")
except TypeError as e:
    print("after `list = [1,2,3]`, list('abc') ->", type(e).__name__ + ":", e)
print("builtins.list('abc') still works ->", builtins.list("abc"))
del list
print("after `del list`, list('abc') ->", list("abc"))

sum = 10
max = 99
id = "user-7"
try:
    sum([1, 2])
except TypeError as e:
    print("sum shadowed ->", e)
try:
    max(1, 2)
except TypeError as e:
    print("max shadowed ->", e)
try:
    id(rex)
except TypeError as e:
    print("id shadowed  ->", e)
del sum, max, id
print("restored: sum, max, id(rex) is int ->", sum([1, 2]), max(1, 2), isinstance(id(rex), int))


def sneaky_max(a, b):
    max = max(a, b)  # 'max' is local for the whole function -> UnboundLocalError
    return max


try:
    sneaky_max(1, 2)
except UnboundLocalError as e:
    print("`max = max(a, b)` inside a function ->", type(e).__name__ + ":", e)

# Global-vs-builtin is decided at RUN time, so late shadowing is picked up:
def count_things(x):
    return len(x)


print("count_things('abcd') ->", count_things("abcd"))
globals()["len"] = lambda x: "shadowed!"
print("after planting a global 'len'  ->", count_things("abcd"))
del globals()["len"]
print("after removing it again        ->", count_things("abcd"))

# You can even inject into builtins (every module sees it). Don't do this in real code.
builtins.injected_everywhere = "visible in all modules"
print("injected builtin ->", injected_everywhere)
del builtins.injected_everywhere

# 10. Loop variables: leak out of `for`, not out of comprehensions
# ------------------------------------
# - `for` (and `while`, `with`, `if`) do NOT create a scope. The loop variable
#   is an ordinary name in the enclosing function/module and survives the loop.
# - List/set/dict comprehensions and generator expressions DO get their own
#   scope in Python 3, so their variable does not leak.
# - Walrus (:=) inside a comprehension is the exception: it binds in the ENCLOSING scope.

print("\n# 10. Loop variables and scope")
print("# ------------------------------------")

for leaky in range(3):
    pass
print("`for` variable after loop: leaky =", leaky)

for never_set in []:
    pass
print("empty loop never binds the name ->", "never_set" in globals())

squares = [sq_item**2 for sq_item in range(4)]
print("comprehension result:", squares, "| 'sq_item' leaked?", "sq_item" in globals())
try:
    sq_item
except NameError as e:
    print("reading it ->", type(e).__name__ + ":", e)

_ = [walrus_val := n * 10 for n in range(3)]
print("walrus inside comprehension leaks into outer scope: walrus_val =", walrus_val)

# 11. del and name lifetime
# ------------------------------------
# - `del name` removes the BINDING (the dict key), not the object.
# - The object is freed when nothing refers to it (CPython: refcount hits 0).
# - `except ... as e` auto-deletes `e` at the end of the except block.

print("\n# 11. del and name lifetime")
print("# ------------------------------------")


class Noisy:
    def __init__(self, label):
        self.label = label

    def __del__(self):
        print(f"   [freed] {self.label}")


first = Noisy("the object")
second = first  # two names, one object
print("two names, same object ->", first is second)
del first
print("after `del first`: 'first' in globals() ->", "first" in globals(), "| object alive via second:", second.label)
print("deleting the last name...")
del second
print("...(CPython freed it immediately above)")

try:
    int("x")
except ValueError as caught:
    pass
print("after the except block, 'caught' still exists ->", "caught" in globals(), "(auto-deleted, even at module level)")


def except_cleanup():
    try:
        int("x")
    except ValueError as err:
        saved = err  # save it explicitly if you need it later
    try:
        return err
    except UnboundLocalError as e:
        return f"'err' was auto-deleted -> {type(e).__name__}"


print(except_cleanup())

# 12. Class body scope gotchas
# ------------------------------------
# - A class body runs like a mini-function that builds the class namespace.
# - That namespace is NOT an enclosing scope for methods nor (mostly) for
#   comprehensions inside it. LEGB skips class bodies.
# - Methods must use self.x or ClassName.x for class variables.

print("\n# 12. Class body scope gotchas")
print("# ------------------------------------")


class Config:
    LIMIT = 3

    def bare_name(self):
        return LIMIT  # NameError: methods can't see class variables by bare name

    def via_self(self):
        return self.LIMIT  # correct

    def via_class(self):
        return Config.LIMIT  # also correct


cfg = Config()
try:
    cfg.bare_name()
except NameError as e:
    print("method using bare LIMIT ->", type(e).__name__ + ":", e)
print("self.LIMIT ->", cfg.via_self(), "| Config.LIMIT ->", cfg.via_class())

try:
    class BrokenComp:
        LIMIT = 3
        small = [n for n in range(10) if n < LIMIT]  # LIMIT used in the condition
except NameError as e:
    print("comprehension condition inside class body ->", type(e).__name__ + ":", e)


class FineComp:
    LIMIT = 3
    first_n = [n for n in range(LIMIT)]  # the FIRST iterable is evaluated in class scope
    # Workaround for conditions: compute outside, or use a helper with a parameter.
    small = (lambda limit: [n for n in range(10) if n < limit])(LIMIT)


print("range(LIMIT) as first iterable works ->", FineComp.first_n)
print("passing LIMIT in as an argument works ->", FineComp.small)
print("(Python 3.12 inlined comprehensions for speed, but kept this class-body rule.)")

# 13. Late-binding closures in a loop
# ------------------------------------
# - A closure captures the VARIABLE (a cell), not its value at creation time.
# - All lambdas in the loop share one `i`; they read it when CALLED, after the loop finished.
# - Fixes: bind the current value as a default arg (i=i), use functools.partial,
#   or build each function in a factory so every call gets its own scope.
# - Closure basics: see 02-Functions.py section 10.

print("\n# 13. Late-binding closures in a loop")
print("# ------------------------------------")

late = [lambda: i for i in range(3)]
print("[lambda: i for i in range(3)] called ->", [f() for f in late], "(not 0,1,2!)")
print("they share one cell:", late[0].__closure__[0] is late[2].__closure__[0], "| cell value:", late[0].__closure__[0].cell_contents)

fixed_default = [lambda i=i: i for i in range(3)]
print("default-arg fix  (i=i) ->", [f() for f in fixed_default])

fixed_partial = [functools.partial(lambda n: n, i) for i in range(3)]
print("functools.partial fix  ->", [f() for f in fixed_partial])


def make_const(n):
    return lambda: n  # each call to make_const has its own 'n'


fixed_factory = [make_const(i) for i in range(3)]
print("factory-function fix   ->", [f() for f in fixed_factory])
print("gotcha of the i=i trick: callers can override it ->", fixed_default[0](99))

# 14. dir() with no args, and vars()
# ------------------------------------
# - dir()      -> sorted list of names in the CURRENT scope.
# - dir(obj)   -> attribute names of obj (includes inherited ones).
# - vars()     -> same as locals(); vars(obj) -> obj.__dict__ (own attrs only).

print("\n# 14. dir() and vars()")
print("# ------------------------------------")


def tiny(a, b):
    c = a + b
    return dir()


print("dir() inside a function ->", tiny(1, 2))
print("module-level dir() contains 'g_name' and 'hits' ->", "g_name" in dir() and "hits" in dir())
print("vars(rex) ->", vars(rex), "| same object as rex.__dict__:", vars(rex) is rex.__dict__)
print("'speak' in dir(rex) ->", "speak" in dir(rex), "| 'speak' in vars(rex) ->", "speak" in vars(rex), "(it lives on the class)")
print("vars() at module level is globals() ->", vars() is globals())

# 15. Mutating locals() does not change real locals (in functions)
# ------------------------------------
# - Inside a function, local variables live in fast array slots, not a dict.
# - locals() builds a dict COPY from them. Writing to the copy changes nothing real.
# - (At module level locals() IS globals(), so writes do work there - section 02.)

print("\n# 15. locals() mutation inside a function")
print("# ------------------------------------")


def try_to_mutate():
    x = 1
    snapshot = locals()
    snapshot["x"] = 999  # modify the copy
    snapshot["y"] = "invented"  # add a key to the copy
    return x, locals()["x"], "y" in try_to_mutate.__code__.co_varnames


print("try_to_mutate() -> (real x, locals()['x'] again, y is a real variable?) =", try_to_mutate())
print("x stayed 1 and calling locals() again refreshes the copy from the real slots.")
print("'y' was only ever a key in a throwaway dict - never a variable. Use plain assignment.")
print("(CPython 3.13 formalised this: PEP 667 makes locals() an independent snapshot.)")

# 16. Module scope vs `if __name__ == "__main__"`
# ------------------------------------
# - The `if __name__ == "__main__":` block is NOT a new scope. Names assigned in
#   it are module globals - but they exist only when the file is RUN, not imported.
# - Functions that quietly read such names work in a script and crash on import.
# - We simulate "run" vs "import" by executing the same source in two fresh namespaces.

print("\n# 16. Module scope vs __main__ block")
print("# ------------------------------------")

print("this file's __name__ ->", __name__)

source = '''
def report():
    return "mode=" + mode

if __name__ == "__main__":
    mode = "script"      # global, but only created when run directly
'''
as_script = {"__name__": "__main__"}
exec(source, as_script)
print("run as script   ->", as_script["report"](), "| 'mode' in namespace:", "mode" in as_script)

as_import = {"__name__": "some_module"}
exec(source, as_import)
try:
    as_import["report"]()
except NameError as e:
    print("when imported   ->", type(e).__name__ + ":", e)
print("fix: put the setup in a function main() and pass values explicitly.")

# 17. Mutable module globals are a code smell
# ------------------------------------
# - A function that reads/writes module-level state has hidden inputs and outputs:
#   same call, different results; hard to test; breaks with threads/reloads.
# - Prefer parameters + return values, or an object that owns its state.
# - Constants (UPPER_CASE, never changed) are fine.

print("\n# 17. Mutable module globals are a code smell")
print("# ------------------------------------")

_seen = []


def remember_bad(item):
    _seen.append(item)
    return len(_seen)  # answer depends on EVERY previous call


print("remember_bad('a'), remember_bad('a') ->", remember_bad("a"), remember_bad("a"), "(same input, different output)")


class Remember:
    def __init__(self):
        self._seen = []

    def add(self, item):
        self._seen.append(item)
        return len(self._seen)


r1, r2 = Remember(), Remember()
print("object owns its state: r1.add('a'), r2.add('a') ->", r1.add("a"), r2.add("a"), "(independent, testable)")

# 18. types.SimpleNamespace - a clean, explicit namespace
# ------------------------------------
# - SimpleNamespace is a tiny object whose attributes are exactly the keywords you give.
# - Nicer than a dict for config (ns.port vs d["port"]), lighter than writing a class.
# - Because `state.count += 1` mutates an attribute (no rebinding of `state`),
#   you don't need `global` - but it is still shared state, so use it deliberately.

print("\n# 18. types.SimpleNamespace")
print("# ------------------------------------")

settings = SimpleNamespace(host="localhost", port=8080)
settings.debug = True
print("repr ->", settings)
print("settings.port ->", settings.port, "| vars(settings) ->", vars(settings))
del settings.debug
print("after del settings.debug ->", settings)
print("equality compares contents ->", SimpleNamespace(a=1) == SimpleNamespace(a=1))
print("from a dict ->", SimpleNamespace(**{"x": 1, "y": 2}))

state = SimpleNamespace(count=0)


def bump():
    state.count += 1  # no `global` needed: we mutate, not rebind


bump()
bump()
print("state.count after 2 bumps ->", state.count)

try:
    settings.missing
except AttributeError as e:
    print("typo'd attribute fails loudly ->", type(e).__name__ + ":", e)

# 19. Cheat sheet
# ------------------------------------
print("\n# 19. Cheat sheet")
print("# ------------------------------------")
print("# - Lookup order: Local -> Enclosing -> Global -> Built-in (LEGB), else NameError.")
print("# - Assigned anywhere in a function body => local everywhere in it (compile time).")
print("# - global/nonlocal rebind outer names; mutating objects never needs them.")
print("# - Only def, class, lambda, comprehensions and modules make scopes; if/for/while/with don't.")
print("# - Class bodies are not enclosing scopes. Use self.x / ClassName.x.")
print("# - Closures capture variables, not values (late binding).")
print("# - Don't shadow builtins; if you did, `del name` or builtins.name.")
