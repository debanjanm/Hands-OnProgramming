import argparse
import ast
import dis
import functools
import gc
import inspect
import io
import sys
import traceback
import types
import typing

# 01. Introspection - Looking Inside Python
# ------------------------------------
# - "Introspection" = a program examining its own parts while it runs:
#   what arguments does this function take? what is its source? what does the
#   interpreter actually DO when it runs this line?
# - Python makes this unusually easy because functions, classes, modules and
#   even code itself are ordinary objects you can pick up and look at.
# - Four tools, from high level to low level:
#     inspect -> ask about live objects (signatures, members, callers)
#     types   -> the classes behind functions/modules, to build them by hand
#     ast     -> the parsed STRUCTURE of source code (a tree) - read or rewrite it
#     dis     -> the BYTECODE the interpreter runs (the lowest level you normally see)
# - You rarely need these in everyday code, but every framework you use
#   (pytest, FastAPI, Django, dataclasses, argparse-like CLIs) is built on them.
#   Learning them demystifies the "magic".

print("# 01. Introspection - Looking Inside Python")
print("# ------------------------------------")

# --- some sample things to inspect (used throughout the file) ---


def greet(name, greeting="Hello", *extras, punct="!", **options):
    """Return a greeting string.

    Shows every kind of parameter on purpose.
    """
    return f"{greeting}, {name}{punct}"


def positional_demo(a, b, /, c, *, d):
    """a, b are positional-only; c is normal; d is keyword-only."""
    return a, b, c, d


class Dog:
    """A small class to inspect."""

    species = "canis"

    def __init__(self, name):
        self.name = name

    def speak(self):
        """Make a sound."""
        return f"{self.name} says woof"

    @staticmethod
    def kinds():
        return ["small", "large"]

    @classmethod
    def create(cls, name):
        return cls(name)


async def fetch_data():
    return 42


def count_up(n):
    for i in range(n):
        yield i


# 02. inspect.signature() and Parameter Kinds
# ------------------------------------
# - signature() returns a Signature object: the function's parameter list as DATA.
# - Each Parameter has .name, .kind, .default, .annotation.
# - kinds (in the order they must appear in a def):
#     POSITIONAL_ONLY     a, b before "/"
#     POSITIONAL_OR_KEYWORD  the ordinary kind
#     VAR_POSITIONAL      *args
#     KEYWORD_ONLY        after * or *args
#     VAR_KEYWORD         **kwargs
print("\n# 02. inspect.signature() and Parameter kinds")
sig = inspect.signature(greet)
print("signature:", sig)
for pname, p in sig.parameters.items():
    default = "(required)" if p.default is inspect.Parameter.empty else repr(p.default)
    print(f"  {pname:8} kind={p.kind.name:22} default={default}")

print("positional_demo:", inspect.signature(positional_demo))
print("kinds:", [p.kind.name for p in inspect.signature(positional_demo).parameters.values()])

# 03. Signature.bind() - Check a Call Without Making It
# ------------------------------------
# - sig.bind(*args, **kwargs) matches a call against the signature and raises
#   TypeError if it would be invalid - the same error Python would give.
# - apply_defaults() fills in omitted parameters so you can see the full picture.
print("\n# 03. Signature.bind() and apply_defaults()")
bound = sig.bind("Asha", punct="?")
bound.apply_defaults()
print("bound arguments:", dict(bound.arguments))
try:
    sig.bind()  # missing required 'name'
except TypeError as err:
    print("bind() rejected a bad call:", err)

# 04. inspect.getsource() and getdoc()
# ------------------------------------
# - getsource(obj) returns the source text - IF Python can find the file.
# - It FAILS (OSError / TypeError) for: built-ins written in C, code made with
#   exec()/eval(), code in the interactive prompt, or when only .pyc files exist.
#   Always guard it.
# - getdoc() returns the docstring cleaned of its indentation.
print("\n# 04. inspect.getsource() / getdoc()")
try:
    src = inspect.getsource(Dog.speak)
    print("source of Dog.speak:")
    print(src.rstrip())
except (OSError, TypeError) as err:
    print("source not available:", err)

print("getdoc(greet):", repr(inspect.getdoc(greet)))
print("getdoc(Dog)  :", repr(inspect.getdoc(Dog)))

for thing in (len, "compile-made function"):
    try:
        if thing is len:
            inspect.getsource(len)
        else:
            ns = {}
            exec("def made(): return 1", ns)
            inspect.getsource(ns["made"])
    except (OSError, TypeError) as err:
        print(f"getsource({getattr(thing, '__name__', thing)}) -> {type(err).__name__}: {err}")

# 05. inspect.getmembers() with Predicates
# ------------------------------------
# - getmembers(obj, predicate) lists (name, value) pairs, sorted by name.
# - The predicate filters: inspect.isfunction, isclass, ismethod, ...
# - Real use: test runners find "test_*" methods; plugin systems find classes.
print("\n# 05. getmembers with predicates")
pets = Dog("Rex")
public = [n for n, _ in inspect.getmembers(pets) if not n.startswith("_")]
print("public members of a Dog instance:", public)
print("bound methods   : (a classmethod like create() counts as bound - to the class)")
print("methods (bound) :", [n for n, _ in inspect.getmembers(pets, inspect.ismethod) if not n.startswith("_")])
print("functions on the CLASS:", [n for n, _ in inspect.getmembers(Dog, inspect.isfunction) if not n.startswith("_")])


# A tiny test-runner: find and call every method starting with "test_".
class Checks:
    def test_math(self):
        assert 1 + 1 == 2

    def test_fail(self):
        assert False, "demo failure"

    def helper(self):
        pass


print("mini test runner:")
for name, method in inspect.getmembers(Checks(), inspect.ismethod):
    if name.startswith("test_"):
        try:
            method()
            print(f"  {name}: PASS")
        except AssertionError as err:
            print(f"  {name}: FAIL ({err})")

# 06. The is* Family
# ------------------------------------
# - Plain isinstance() checks are not enough: a generator FUNCTION and a
#   generator OBJECT are different things; so are async functions vs coroutines.
print("\n# 06. isfunction / isclass / ismethod / iscoroutinefunction / isgenerator")
print("isfunction(greet)            :", inspect.isfunction(greet))
print("isclass(Dog)                 :", inspect.isclass(Dog))
print("ismethod(Dog('x').speak)     :", inspect.ismethod(Dog("x").speak))
print("ismethod(Dog.speak)          :", inspect.ismethod(Dog.speak), "(plain function on the class)")
print("iscoroutinefunction(fetch)   :", inspect.iscoroutinefunction(fetch_data))
print("isgeneratorfunction(count_up):", inspect.isgeneratorfunction(count_up))
print("isgenerator(count_up(3))     :", inspect.isgenerator(count_up(3)))
print("isgenerator(count_up)        :", inspect.isgenerator(count_up), "(the function, not the object)")
coro = fetch_data()  # calling an async def does not run it; it returns a coroutine object
print("iscoroutine(fetch_data())    :", inspect.iscoroutine(coro))
coro.close()  # avoid the "coroutine was never awaited" warning

# 07. Who Called Me? currentframe() and stack()
# ------------------------------------
# - A "frame" is one active function call: its code, its local variables, its line.
# - currentframe().f_back is the CALLER's frame. Its f_code.co_name is the name.
# - inspect.stack() gives the whole stack but is SLOW (it reads source lines for
#   every frame). Prefer currentframe() for hot paths like logging.
print("\n# 07. currentframe() / stack()")


def whoami():
    return inspect.currentframe().f_code.co_name


def caller_name():
    return inspect.currentframe().f_back.f_code.co_name


def some_function():
    return caller_name()


def stack_names():
    return [frame.function for frame in inspect.stack()][:3]


print("whoami() ->", whoami())
print("some_function() calls caller_name(), which reports ->", some_function())
print("top of stack from inside stack_names ->", stack_names()[:2])
frame = inspect.currentframe()
print("current line number inside this module:", frame.f_lineno > 0, "| locals include 'sig':", "sig" in frame.f_locals)
del frame  # frames reference locals -> reference cycles; delete them when done

# 08. inspect.getmodule()
# ------------------------------------
print("\n# 08. inspect.getmodule()")
print("getmodule(greet).__name__     :", inspect.getmodule(greet).__name__)
print("getmodule(inspect.signature)  :", inspect.getmodule(inspect.signature).__name__)
print("getmodule(len)                :", inspect.getmodule(len), "(built-ins have no source module)")

# 09. getfullargspec() - the Legacy Way
# ------------------------------------
# - Older code uses inspect.getfullargspec(). It still works but cannot express
#   positional-only parameters well and does not follow __wrapped__.
# - Prefer inspect.signature() in new code.
print("\n# 09. getfullargspec (legacy)")
spec = inspect.getfullargspec(greet)
print("args:", spec.args, "| varargs:", spec.varargs, "| varkw:", spec.varkw)
print("defaults:", spec.defaults, "| kwonlyargs:", spec.kwonlyargs)

# 10. Decorators and Signatures
# ------------------------------------
# - A naive decorator wraps f in wrapper(*args, **kwargs). The wrapper's own
#   signature is then (*args, **kwargs) - help(), IDEs and frameworks that
#   read signatures lose all information.
# - functools.wraps copies __name__/__doc__ AND sets __wrapped__, which
#   inspect.signature() follows to show the ORIGINAL signature.
print("\n# 10. Decorators that preserve signatures")


def naive(f):
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


def good(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return f(*args, **kwargs)
    return wrapper


@naive
def add_naive(a, b=2):
    return a + b


@good
def add_good(a, b=2):
    return a + b


print("naive :", add_naive.__name__, inspect.signature(add_naive))
print("wraps :", add_good.__name__, inspect.signature(add_good))
print("wraps keeps a pointer to the original:", add_good.__wrapped__.__name__)


# A decorator that USES the signature: log every call with argument NAMES.
def log_calls(f):
    sig_ = inspect.signature(f)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        bound_ = sig_.bind(*args, **kwargs)
        bound_.apply_defaults()
        shown = ", ".join(f"{k}={v!r}" for k, v in bound_.arguments.items())
        print(f"  CALL {f.__name__}({shown})")
        return f(*args, **kwargs)
    return wrapper


@log_calls
def area(width, height=10):
    return width * height


print("decorator reading the signature:")
print("  result:", area(3))

# 11. Worked Example: Auto-Validator and Auto-CLI from Type Hints
# ------------------------------------
# - Frameworks like FastAPI and Typer read your function's type hints and
#   build validation / command-line parsing for you. The core idea is small.
# - typing.get_type_hints(f) resolves annotations (including string ones);
#   see 06-Typing-And-Type-Hints.py for the typing side of this.
print("\n# 11. Auto-validator from type hints")


def validated(f):
    """Convert/check arguments against f's type hints before calling f."""
    hints = typing.get_type_hints(f)
    sig_ = inspect.signature(f)

    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        bound_ = sig_.bind(*args, **kwargs)
        bound_.apply_defaults()
        for pname, value in bound_.arguments.items():
            expected = hints.get(pname)
            if expected in (int, float, str) and not isinstance(value, expected):
                try:
                    bound_.arguments[pname] = expected(value)  # "5" -> 5
                except (TypeError, ValueError):
                    raise TypeError(f"{pname} must be {expected.__name__}, got {value!r}") from None
        return f(*bound_.args, **bound_.kwargs)
    return wrapper


@validated
def make_rect(width: int, height: int = 1, label: str = "box") -> str:
    return f"{label}: {width}x{height} = {width * height}"


print(make_rect("4", height="3"))  # strings coerced to int
try:
    make_rect("four")
except TypeError as err:
    print("rejected:", err)


def auto_cli(func):
    """Build an argparse parser from func's signature and run it on a fake argv."""
    sig_ = inspect.signature(func)
    hints = typing.get_type_hints(func)
    parser = argparse.ArgumentParser(prog=func.__name__, description=inspect.getdoc(func))
    for pname, p in sig_.parameters.items():
        kind = hints.get(pname, str)
        if p.default is inspect.Parameter.empty:
            parser.add_argument(pname, type=kind)  # required positional
        elif kind is bool:
            parser.add_argument(f"--{pname}", action="store_true")
        else:
            parser.add_argument(f"--{pname}", type=kind, default=p.default)
    return func, parser


def deploy(env: str, replicas: int = 2, dry_run: bool = False) -> str:
    """Pretend to deploy the app."""
    return f"deploying to {env} with {replicas} replicas (dry_run={dry_run})"


print("\nauto-CLI generated from deploy()'s signature:")
fn, parser = auto_cli(deploy)
print(" ", parser.format_usage().strip())
ns = parser.parse_args(["prod", "--replicas", "5", "--dry_run"])
print(" ", fn(**vars(ns)))

# 12. The types Module - the Classes Behind Python's Objects
# ------------------------------------
# - types.FunctionType      the class of every `def` function
# - types.MethodType        a function bound to an instance (how self gets filled in)
# - types.SimpleNamespace   a bare "object with attributes", nicer than an empty class or dict
# - types.ModuleType        the class of imported modules - you can create one on the fly
# - types.CodeType          compiled code objects (what f.__code__ is); rarely built by hand
print("\n# 12. The types module")
print("type(greet) is types.FunctionType      :", type(greet) is types.FunctionType)
print("type(Dog('x').speak) is MethodType     :", type(Dog("x").speak) is types.MethodType)
print("type(greet.__code__) is types.CodeType :", type(greet.__code__) is types.CodeType)

point = types.SimpleNamespace(x=1, y=2)
point.z = 3
print("SimpleNamespace:", point, "| point.x =", point.x)


# MethodType: bind any function to an instance after the fact ("monkey patching" one object).
def shout(self):
    return self.name.upper() + "!"


rex = Dog("rex")
rex.shout = types.MethodType(shout, rex)  # self is now filled in automatically
print("bound later:", rex.shout(), "| another Dog has it?", hasattr(Dog("max"), "shout"))

# ModuleType: build a module with no file.
plugin = types.ModuleType("plugin_demo", "a module made at runtime")
exec("def hello():\n    return 'hi from a dynamic module'\nVERSION = (1, 0)", plugin.__dict__)
print("dynamic module:", plugin.__name__, plugin.hello(), plugin.VERSION)
print("importing by string name instead -> see 05-Python Advanced/05-Modules-And-Packages.py (importlib.import_module).")

# 13. Function Internals: __code__, __defaults__
# ------------------------------------
# - A function object = a code object (the compiled body) + its defaults +
#   its globals + its closure cells. All visible as attributes.
# - co_varnames  names of parameters and local variables
# - co_argcount  number of ordinary positional parameters
# - co_consts    constants used in the body (literals, nested code objects)
# - co_names     global/attribute names the code refers to
print("\n# 13. Function internals")


def compute(a, b=5):
    scale = 100
    total = (a + b) * scale
    label = "result"
    return label, total


code = compute.__code__
print("co_name      :", code.co_name)
print("co_argcount  :", code.co_argcount)
print("co_varnames  :", code.co_varnames)
print("co_consts    :", code.co_consts)
print("__defaults__ :", compute.__defaults__, "(values for the LAST n parameters)")
print("__kwdefaults__:", greet.__kwdefaults__, "(keyword-only defaults)")
print("__annotations__:", make_rect.__annotations__)

# Mutable default gotcha is visible here: the default is stored ON the function object.


def append_to(item, bucket=[]):
    bucket.append(item)
    return bucket


append_to(1)
append_to(2)
print("the shared default list lives at append_to.__defaults__ ->", append_to.__defaults__)

# 14. Closures Made Visible: __closure__
# ------------------------------------
# - A closure is an inner function that remembers variables from the function
#   that created it. Python keeps them in "cells", reachable via __closure__.
print("\n# 14. Closures: __closure__ cells")


def make_counter(start):
    count = start

    def tick():
        nonlocal count
        count += 1
        return count
    return tick


counter = make_counter(10)
print("free variable names :", counter.__code__.co_freevars)
print("cell contents before:", counter.__closure__[0].cell_contents)
counter()
counter()
print("after two ticks     :", counter.__closure__[0].cell_contents, "<- same cell, state kept alive")
print("plain function closure:", greet.__closure__)

# 15. dis - What the Interpreter Actually Runs
# ------------------------------------
# - Python first compiles your source into BYTECODE: a list of tiny
#   instructions for a stack-based virtual machine. dis prints them.
# - Exact opcodes CHANGE between Python versions (3.11 and 3.12 differ a lot),
#   so treat the output as an explanation tool, never as something to assert on.
# - Reading guide (typical opcodes, names may vary by version):
#     LOAD_FAST x     push local variable x onto the stack
#     LOAD_CONST 2    push the constant 2
#     BINARY_OP *     pop two values, multiply, push the result
#     RETURN_VALUE    pop the top of the stack and return it
#     (3.12: RETURN_CONST returns a constant directly; RESUME marks function start)
print("\n# 15. dis - bytecode of a tiny function")


def double(x):
    return x * 2


print(f"Python {sys.version_info.major}.{sys.version_info.minor} bytecode for double(x):")
dis.dis(double)
print("opnames only:", [i.opname for i in dis.get_instructions(double)])


def opnames(f):
    return [i.opname for i in dis.get_instructions(f)]


# 16. Bytecode Comparisons - Curiosities
# ------------------------------------
print("\n# 16. Bytecode comparisons (print, do not assert - versions differ)")


def times_two(x):
    return x * 2


def shift_one(x):
    return x << 1


def binop(f):
    return [i.argrepr for i in dis.get_instructions(f) if i.opname == "BINARY_OP"]


print("x * 2 :", opnames(times_two), "operator:", binop(times_two))
print("x << 1:", opnames(shift_one), "operator:", binop(shift_one))
print("=> identical shape, only the operator argument differs: the compiler does not")
print("   rewrite * 2 into a shift for you. Write the clear one; this kind of")
print("   micro-optimization almost never matters in real programs.")


# Constant folding: the compiler does constant arithmetic ONCE, before running.
def seconds_per_day():
    return 60 * 60 * 24


print("seconds_per_day co_consts:", seconds_per_day.__code__.co_consts, "<- 86400 precomputed, no multiplication at runtime")


def squares_loop(n):
    out = []
    for i in range(n):
        out.append(i * i)
    return out


def squares_comp(n):
    return [i * i for i in range(n)]


print("loop version instructions         :", len(list(dis.get_instructions(squares_loop))))
print("list-comp version instructions    :", len(list(dis.get_instructions(squares_comp))))
print("same results:", squares_loop(4) == squares_comp(4))
print("LESSON: fewer instructions does NOT automatically mean faster. A comprehension uses a")
print("  dedicated LIST_APPEND instruction (no .append attribute lookup + call per item), which is")
print("  why it is usually a bit faster even if the raw instruction count differs by version.")


# Swap without a temporary variable.
def swap(a, b):
    a, b = b, a
    return a, b


print("a, b = b, a ->", opnames(swap))
print("  No temp variable: the right side (b, a) is evaluated onto the STACK first, then the")
print("  values are stored into a and b. The stack IS the temporary. For two names modern")
print("  Python skips even the tuple/SWAP step and just stores in reverse order; for longer")
print("  swaps older versions used ROT_TWO / ROT_THREE and newer ones use SWAP.")
print("  swap(1, 2) =", swap(1, 2))

# dis can also write to a file-like object, e.g. to count or search lines:
buffer = io.StringIO()
dis.dis(compute, file=buffer)
print("dis(compute) produced", len(buffer.getvalue().splitlines()), "lines of text")

# 17. ast.parse() and ast.dump() - Source Code as a Tree
# ------------------------------------
# - ast.parse(source) turns text into an Abstract Syntax Tree: nested node
#   objects (Module > Assign > BinOp > Name, Constant ...). It does NOT run
#   the code - it is safe to parse untrusted text (parsing is not executing).
# - ast.dump(tree, indent=2) prints the tree readably (indent= needs 3.9+).
print("\n# 17. ast.parse() and ast.dump()")
tree = ast.parse("total = price * 2 + 1")
print(ast.dump(tree, indent=2))

# 18. ast.walk(), NodeVisitor, NodeTransformer
# ------------------------------------
# - ast.walk(tree)  yields EVERY node (breadth-first) - quick scripts.
# - NodeVisitor     subclass with visit_<NodeType> methods; call generic_visit
#                   to keep descending into children.
# - NodeTransformer same, but a visit_ method RETURNS a replacement node.
# - ast.unparse(tree) turns a tree back into source code (3.9+).
print("\n# 18. walk / NodeVisitor / NodeTransformer / unparse")
SAMPLE = '''
import os, sys, json

def alpha(x):
    return x + 1

class Box:
    def beta(self):
        print("inside beta")
        return 2

def gamma():
    print("gamma")
    value = alpha(3)
    return value
'''
sample_tree = ast.parse(SAMPLE)
kinds = sorted({type(node).__name__ for node in ast.walk(sample_tree)})
print("node types present:", kinds[:8], "...")


class FunctionCounter(ast.NodeVisitor):
    def __init__(self):
        self.names = []

    def visit_FunctionDef(self, node):
        self.names.append(node.name)
        self.generic_visit(node)  # also look INSIDE (finds nested defs)


counter_visitor = FunctionCounter()
counter_visitor.visit(sample_tree)
print("function defs found (including methods):", counter_visitor.names)


class Rename(ast.NodeTransformer):
    """Rename every variable called `old` to `new`."""

    def __init__(self, old, new):
        self.old, self.new = old, new

    def visit_Name(self, node):
        if node.id == self.old:
            node.id = self.new
        return node


before = ast.parse("price = base * 2\nprint(price)")
after = Rename("price", "cost").visit(before)
ast.fix_missing_locations(after)  # keep line/col info valid after edits
print("renamed code:")
print(ast.unparse(after))


class FoldTimesOne(ast.NodeTransformer):
    """Replace `expr * 1` with `expr` - a tiny optimizer."""

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Mult) and isinstance(node.right, ast.Constant) and node.right.value == 1:
            return node.left
        return node


print("optimized  :", ast.unparse(FoldTimesOne().visit(ast.parse("y = (a + b) * 1"))))

# 19. ast.literal_eval() - the Safe Alternative to eval()
# ------------------------------------
# - eval(text) executes ARBITRARY Python: eval("__import__('os').system(...)")
#   is a full compromise if the text came from a user, file or network.
# - literal_eval(text) only accepts Python LITERALS: numbers, strings, bytes,
#   tuples, lists, dicts, sets, booleans, None. Anything else raises ValueError.
# - Use it to read Python-literal-looking config or repr() output.
#   For general data prefer json (see 04-Json-And-Csv.py).
print("\n# 19. ast.literal_eval()")
accepted = ["[1, 2, 3]", "{'a': 1, 'b': (2, 3)}", "{1, 2}", "None", "-5", "'text'", "1+2j"]
for text in accepted:
    print(f"  accepts {text!r:28} -> {ast.literal_eval(text)!r}")
rejected = ["__import__('os').getcwd()", "1 + 2", "[x for x in range(3)]", "len([1])", "abc"]
for text in rejected:
    try:
        ast.literal_eval(text)
    except (ValueError, SyntaxError) as err:
        print(f"  rejects {text!r:28} -> {type(err).__name__}")
print("  note: even '1 + 2' is rejected - arithmetic is code, not a literal.")
print("  caution: literal_eval is NOT a sandbox for huge/deeply nested input (can crash or eat memory).")

# 20. compile() and exec() with an AST
# ------------------------------------
# - compile(tree, filename, mode) turns an AST into a code object; exec runs it.
#   Pipeline: source -> ast.parse -> (inspect/modify) -> compile -> exec.
#   This is exactly how pytest rewrites asserts to show nice failure messages.
print("\n# 20. compile() + exec() of an AST")
tree = ast.parse("result = sum(n * n for n in range(5))")
code_obj = compile(tree, filename="<ast-demo>", mode="exec")
namespace = {}
exec(code_obj, namespace)  # only do this with code YOU trust
print("result from executed AST:", namespace["result"])
print("code object type:", type(code_obj).__name__)

# Modify the tree first: change the multiplication into addition, then run it.


class MultToAdd(ast.NodeTransformer):
    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Mult):
            node.op = ast.Add()
        return node


tree2 = ast.fix_missing_locations(MultToAdd().visit(ast.parse("result = sum(n * n for n in range(5))")))
ns2 = {}
exec(compile(tree2, "<ast-demo-2>", "exec"), ns2)
print("after rewriting * to +:", ns2["result"], "(n + n summed over 0..4)")

# 21. Mini Static Checks with ast (no code is run)
# ------------------------------------
# - Linters (flake8, pylint, ruff) are built this way: parse, walk, report.
print("\n# 21. Mini static checks: print() calls and unused imports")
CHECK_ME = '''
import os
import sys
import json as js
from collections import OrderedDict, defaultdict

def f():
    print("debug leftover")
    return defaultdict(list), sys.argv
'''
check_tree = ast.parse(CHECK_ME)

print_lines = [
    n.lineno for n in ast.walk(check_tree)
    if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "print"
]
print("print() calls on lines:", print_lines)

imported = {}  # local name -> line number
for node in ast.walk(check_tree):
    if isinstance(node, ast.Import):
        for alias in node.names:
            imported[(alias.asname or alias.name).split(".")[0]] = node.lineno
    elif isinstance(node, ast.ImportFrom):
        for alias in node.names:
            imported[alias.asname or alias.name] = node.lineno
used = {n.id for n in ast.walk(check_tree) if isinstance(n, ast.Name)}  # attribute roots are Names too
unused = {name: line for name, line in imported.items() if name not in used}
print("unused imports (name: line):", unused)
print("  (lite check: a name used only in a string or __all__ would be a false positive)")

# 22. sys._getframe() and traceback.extract_stack()
# ------------------------------------
# - sys._getframe(n) is the fast, CPython-specific cousin of inspect.currentframe:
#   n frames up the call stack. The leading underscore warns "implementation detail".
# - traceback.extract_stack() gives the call chain as safe, simple objects
#   (filename, line, function name) - good for logging "who got me here".
print("\n# 22. sys._getframe / traceback.extract_stack")


def level_two():
    caller = sys._getframe(1).f_code.co_name
    chain = [fs.name for fs in traceback.extract_stack()]
    return caller, chain[-3:]


def level_one():
    return level_two()


print("caller via sys._getframe(1) and last 3 stack names:", level_one())

# 23. Pointers to Related Files
# ------------------------------------
# - Importing by name at runtime (__import__, importlib.import_module):
#       05-Python Advanced/05-Modules-And-Packages.py
# - Annotations and typing.get_type_hints (used in section 11 above):
#       06-Standard Library/06-Typing-And-Type-Hints.py
print("\n# 23. Related files")
print("dynamic imports       -> 05-Python Advanced/05-Modules-And-Packages.py")
print("type hints / typing   -> 06-Standard Library/06-Typing-And-Type-Hints.py")
print("raw annotations       :", typing.get_type_hints(deploy))

# 24. gc.get_referrers() Curiosity - Who Is Holding This Object?
# ------------------------------------
# - Python frees an object when nothing refers to it (reference counting). When
#   an object "will not die", gc.get_referrers(obj) answers "who still points at it?"
# - Debugging memory leaks and "why is this still alive?" - a curiosity for
#   everyday work, a lifesaver in long-running services.
print("\n# 24. gc.get_referrers()")


class Resource:
    pass


res = Resource()
cache = {"the-resource": res}
holder_list = [res]
referrer_types = sorted({type(r).__name__ for r in gc.get_referrers(res)})
print("types of things referencing res:", referrer_types)
print("sys.getrefcount(res) > 3:", sys.getrefcount(res) > 3, "(res, cache, holder_list + the temporary argument)")
del cache, holder_list

# 25. When Introspection Is the Right Tool - and When It Is a Smell
# ------------------------------------
# RIGHT TOOL (generic code that must work with code it has never seen):
# - Frameworks: web routers reading handler signatures, dependency injection,
#   serializers that look at dataclass fields, ORMs reading class attributes.
# - Test runners: discover test_* functions, rewrite asserts via ast, show failing source.
# - Debuggers, profilers, loggers: need frames, line numbers, caller names.
# - Plugin systems, CLI generators, documentation generators (getdoc/signature).
# - Linters and code-mod tools: ast reading and rewriting.
#
# SMELL (ordinary business logic):
# - if hasattr(obj, "x") chains instead of a clear interface/Protocol.
# - Looking at the caller's name to change behaviour ("if called from X do Y") -
#   pass a parameter instead; hidden coupling is a nightmare to debug.
# - exec/eval on strings to "be flexible" - almost always a data structure
#   (dict of functions) or literal_eval/json is what you actually wanted.
# - Rewriting functions at runtime (monkey patching) in production code.
# - Reading source with getsource for logic: it breaks in zipped/compiled deployments.
#
# RULES OF THUMB:
# - Introspection is fine at the edges (frameworks, tooling, debugging), suspicious in the core.
# - Prefer public API (inspect.signature) over implementation details
#   (sys._getframe, __code__ internals, opcodes) - the latter change between versions.
# - Always guard: source may be missing; frames create reference cycles (del them).
print("\n# 25. When introspection is right vs a smell")
print("right : frameworks, test runners, debuggers, serializers, linters, plugin loaders")
print("smell : business logic that peeks at callers, hasattr chains, eval on strings")
print("tip   : use public inspect APIs; treat dis/__code__/sys._getframe as version-specific")
