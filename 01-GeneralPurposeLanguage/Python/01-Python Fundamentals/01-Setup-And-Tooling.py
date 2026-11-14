#!/usr/bin/env python3
# ^ 05. Shebang: this very first line is one (explained in section 05).

import contextlib
import importlib
import io
import keyword
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import textwrap

# 01. Setup & Tooling - the "before you write code" file
# ------------------------------------
# - Before any language feature, you need to know: WHICH Python is running,
#   HOW to run code, HOW to ask Python for help, and HOW to keep project
#   dependencies from fighting each other.
# - Most beginner pain is not syntax - it is "wrong Python", "wrong pip",
#   "module not found". This file makes those visible.

print("# 01. Setup & Tooling - the 'before you write code' file")
print("# ------------------------------------")


def run(*args, stdin=None, env=None, cwd=None):
    """Run a command, return (stdout, stderr) stripped. Helper for this file."""
    cp = subprocess.run(
        list(args), capture_output=True, text=True, input=stdin, env=env, cwd=cwd
    )
    return cp.stdout.strip(), cp.stderr.strip()


# 02. Which Python am I running?
# ------------------------------------
# - sys.version / sys.version_info : the interpreter version.
# - sys.executable                 : the exact file that is running this code.
# - platform                       : OS + machine details.
# - GOTCHA: you can have many Pythons installed (system, Homebrew, pyenv,
#   venvs). `python` on the command line may NOT be the one you think.
#   sys.executable is the truth.

print("\n# 02. Which Python am I running?")
print("sys.version      :", sys.version.splitlines()[0])
print("version_info     :", sys.version_info[:3], "| major =", sys.version_info.major)
print("sys.executable   :", sys.executable)
print("implementation   :", platform.python_implementation())  # usually CPython
print("OS / machine     :", platform.system(), platform.machine())
print("3.9+ ?           :", sys.version_info >= (3, 9))
# - Comparing version tuples is the right way to guard newer features.
if sys.version_info < (3, 10):
    print("(note: you are on <3.10 - some friendly error messages below differ)")

# 03. The REPL and `python -c`
# ------------------------------------
# - REPL = Read-Eval-Print Loop. Type `python3` in a terminal, get a `>>>`
#   prompt, and every expression's value is printed back. Perfect for
#   "what does this do?" experiments. Exit with exit() or Ctrl-D.
# - `python -c "code"` runs a one-off snippet without creating a file.
# - We cannot type into a real REPL from a script, but we CAN feed one through
#   stdin, which is exactly what happens when you press Enter in a terminal.

print("\n# 03. The REPL and `python -c`")
out, _ = run(sys.executable, "-c", "print(2 ** 10)")
print("python -c 'print(2 ** 10)'  ->", out)

# `-i` after a script/command = run it, then drop into interactive mode.
# Here stdin plays the role of the keyboard.
out, err = run(sys.executable, "-i", stdin="x = 6 * 7\nx\n'hi'.upper()\n")
print("REPL fed 'x = 6 * 7', 'x', \"'hi'.upper()\" printed:", out.splitlines())
print("(prompts like '>>>' go to stderr:", repr(err.splitlines()[-1][:12]), "...)")
# - In the REPL, `_` holds the last result and a bare expression echoes itself
#   (an assignment prints nothing). That is why `x` printed 42 above.

# 04. Script vs `-c` vs `-m` vs `-i`
# ------------------------------------
# - python file.py     : run a file. sys.argv[0] = the file path.
# - python -c "code"   : run a string. sys.argv[0] = '-c'.
# - python -m module   : find `module` on sys.path and run it as a script.
#                        Preferred for tools (-m venv, -m pip, -m http.server)
#                        because it uses THIS interpreter's packages.
# - python -i file.py  : run the file, then stay in the REPL with its variables
#                        alive - great for debugging a crash.
# - In all of the first three, `__name__` is "__main__" (explained in 05).

print("\n# 04. Script vs -c vs -m vs -i")
with tempfile.TemporaryDirectory() as tmp:
    script = os.path.join(tmp, "who_am_i.py")
    with open(script, "w") as f:
        f.write("import sys\nprint('__name__ =', __name__, '| argv =', sys.argv[1:] or 'none')\n")

    print("script   :", run(sys.executable, script, "a", "b")[0])
    print("-c       :", run(sys.executable, "-c", "import sys; print('__name__ =', __name__, '| argv[0] =', sys.argv[0])")[0])
    print("-m       :", run(sys.executable, "-m", "who_am_i", cwd=tmp)[0])

    # -m finds modules on sys.path; json.tool is a stdlib pretty-printer.
    pretty, _ = run(sys.executable, "-m", "json.tool", stdin='{"b":1,"a":[1,2]}')
    print("-m json.tool pretty-prints JSON from stdin:")
    print(textwrap.indent(pretty, "    "))

    # -i with a script: variables from the script survive for inspection.
    with open(script, "w") as f:
        f.write("answer = 42\n")
    out, _ = run(sys.executable, "-i", script, stdin="answer + 1\n")
    print("-i script.py then typing 'answer + 1' ->", out)

# 05. `if __name__ == "__main__":` and the shebang
# ------------------------------------
# - Every module has a __name__.
#     * run directly (script/-m/-c)  -> "__main__"
#     * imported by someone else     -> the module's own name, e.g. "mymod"
# - So the guard `if __name__ == "__main__":` means "only do this when I am
#   the program, NOT when I am being imported as a library".
# - WHY it matters: without it, importing your file would re-run its demo
#   code / start servers as a side effect.
# - Shebang (#!/usr/bin/env python3) on line 1: on macOS/Linux, lets you run
#   `./script.py` directly (after `chmod +x`). Windows ignores it (the `py`
#   launcher reads it though). It is just a comment to Python itself.

print("\n# 05. __name__ guard and shebang")
with tempfile.TemporaryDirectory() as tmp:
    mod = os.path.join(tmp, "greeter.py")
    with open(mod, "w") as f:
        f.write(textwrap.dedent('''\
            #!/usr/bin/env python3
            def greet(name):
                return f"Hello, {name}!"

            print("top-level code runs on EVERY import; __name__ =", __name__)

            if __name__ == "__main__":
                print("main block runs only when executed:", greet("script"))
        '''))
    print("-- executed directly:")
    print(textwrap.indent(run(sys.executable, mod)[0], "    "))
    print("-- imported (-c 'import greeter'):")
    print(textwrap.indent(run(sys.executable, "-c", "import greeter", cwd=tmp)[0], "    "))

    if os.name != "nt":
        os.chmod(mod, 0o755)  # make executable
        try:
            out, err = run(mod)  # run it like a program: no 'python' in front
            print("-- ./greeter.py via shebang :", out.splitlines()[-1] if out else err)
        except OSError as e:  # e.g. temp dir mounted noexec
            print("-- shebang run skipped:", e)
    else:
        print("-- (Windows: shebang run skipped, use `py greeter.py`)")
print("this file's own __name__ right now:", __name__)

# 06. Self-discovery: help() / dir() / type() / __doc__
# ------------------------------------
# - You will not memorise the standard library. You WILL learn to ask Python.
#     type(x)   : what kind of object is this?
#     dir(x)    : what names (attributes/methods) does it have?
#     x.__doc__ : the docstring, a one-paragraph description.
#     help(x)   : formatted docs (opens a pager in a terminal; q to quit).
# - Underscore-wrapped names ("dunder") are Python's internals; filter them
#   out first when exploring.

print("\n# 06. Self-discovery")
print("type(42)      :", type(42))
print("type('hi')    :", type("hi"))
print("type(len)     :", type(len))
print("type(None)    :", type(None))
methods = [n for n in dir("text") if not n.startswith("_")]
print(f"dir('text') has {len(methods)} public names; first 8:", methods[:8])
print("len.__doc__   :", len.__doc__)


def add(a, b):
    """Return a + b. (Your own docstring shows up in help() too.)"""
    return a + b


print("add.__doc__   :", add.__doc__)

# help() prints to stdout. Capture it so we can trim the output.
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    help(str.upper)
print("help(str.upper) ->", " | ".join(l.strip() for l in buf.getvalue().splitlines() if l.strip()))
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    help(add)
print("help(add)       ->", " | ".join(l.strip() for l in buf.getvalue().splitlines() if l.strip()))
# - GOTCHA: help(len) vs help(len()) - the second CALLS len first (error).
#   Pass the object itself, not its result.

# 07. `import this` - the Zen of Python (PEP 20)
# ------------------------------------
# - Importing `this` prints 19 guiding aphorisms. It prints on FIRST import
#   only, so we drop it from sys.modules and capture the output.
# - They are not rules; they are a design philosophy that explains why Python
#   code looks the way it does.

print("\n# 07. The Zen of Python")
sys.modules.pop("this", None)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    importlib.import_module("this")
zen = [l for l in buf.getvalue().splitlines() if l.strip()]
print("lines captured:", len(zen), "(title + 19 aphorisms)")
meanings = {
    "Beautiful is better than ugly.": "Readable layout is a feature, not decoration.",
    "Explicit is better than implicit.": "Say what you mean; hidden magic bites later.",
    "Simple is better than complex.": "Start with the plain solution.",
    "Readability counts.": "Code is read far more often than written.",
    "Errors should never pass silently.": "Don't write bare `except: pass` - failures should be loud.",
    "There should be one-- and preferably only one --obvious way to do it.": "Python favours one clear idiom over many clever ones.",
}
for line in zen:
    if line in meanings:
        print(f"  '{line}'\n      -> {meanings[line]}")

# 08. Keywords: Python's reserved words
# ------------------------------------
# - Keywords have fixed meaning; you cannot use them as variable names.
# - Soft keywords (3.9+) are only special in certain positions, so they can
#   still be used as ordinary names elsewhere (e.g. a variable called `match`).

print("\n# 08. Keywords")
print(f"keyword.kwlist has {len(keyword.kwlist)} reserved words:")
print(textwrap.fill(", ".join(keyword.kwlist), width=76, initial_indent="  ", subsequent_indent="  "))
if hasattr(keyword, "softkwlist"):  # added in Python 3.9
    print("keyword.softkwlist:", keyword.softkwlist)
else:
    print("softkwlist skipped: needs Python 3.9+")
print("iskeyword('class') :", keyword.iskeyword("class"))
print("iskeyword('print') :", keyword.iskeyword("print"), "(print is a built-in FUNCTION, not a keyword)")
match = "soft keyword used as a plain variable - legal!"
print("match =", match)
# - GOTCHA: True/False/None are keywords (capitalised). `true` is just an
#   unknown name -> NameError. Built-in names like list, str, sum are NOT
#   reserved, so you CAN overwrite them by accident (see the builtins file).

# 09. PEP 8 essentials (the style guide)
# ------------------------------------
# - PEP 8 = the community style guide. Not enforced by Python, but every
#   team, tutorial and linter assumes it. Style never changes behaviour; it
#   changes how fast a human can read your code.
# - Naming:  snake_case  -> variables, functions, modules (total_price)
#            PascalCase  -> classes (ShoppingCart)
#            UPPER_CASE  -> constants (MAX_RETRIES)
#            _leading    -> "internal, please don't touch" (_cache)
# - 4 spaces per indent level. Never mix tabs and spaces.
# - Line length: PEP 8 says 79; formatter `black` defaults to 88. Pick one and
#   let a tool enforce it.
# - Imports at the top, in 3 groups separated by blank lines:
#   standard library, third-party, your own project. One import per line.
# - Spaces around operators and after commas; none inside brackets or around
#   `=` in keyword arguments (f(x=1)).

print("\n# 09. PEP 8 essentials")
bad = '''\
import sys,os
from math import *
MaxRetries=3
class shopping_cart:
  def AddItem(self,Item):
      return Item+1
def Total (a,b) :
    return a+b
'''
good = '''\
import os
import sys

from math import sqrt

MAX_RETRIES = 3


class ShoppingCart:
    def add_item(self, item):
        return item + 1


def total(a, b):
    return a + b
'''
print("-- non-compliant (legal Python, hard to read):")
print(textwrap.indent(bad, "    "))
print("-- compliant:")
print(textwrap.indent(good, "    "))
compile(bad, "<bad>", "exec")
compile(good, "<good>", "exec")
print("Both compile fine -> style is about humans, not the interpreter.")
print("Tools: `ruff check` / `flake8` (find problems), `black` / `ruff format` (auto-fix layout).")

# 10. Virtual environments - for real
# ------------------------------------
# - Problem: project A needs requests 2.0, project B needs requests 3.0.
#   Installing both globally is impossible and pollutes the system Python.
# - Solution: a virtual environment (venv) = a private folder with its own
#   interpreter link and its own site-packages. Install per project.
# - Create : python3 -m venv .venv
# - Activate (mac/Linux): source .venv/bin/activate   (Windows: .venv\Scripts\activate)
#   Activation just puts .venv/bin first on PATH. You can skip it and call
#   .venv/bin/python directly - which is what we do below.
# - Detect : inside a venv, sys.prefix != sys.base_prefix.
# - Never commit .venv to git (add it to .gitignore); commit requirements.txt.
# - We build a real one in a temp directory; nothing is installed from the
#   network, and the folder is deleted at the end of the `with` block.

print("\n# 10. Virtual environments - for real")
print("Running this script: in a venv? ->", sys.prefix != sys.base_prefix)
print("  sys.prefix      :", sys.prefix)
print("  sys.base_prefix :", sys.base_prefix)

with tempfile.TemporaryDirectory() as tmp:
    venv_dir = os.path.join(tmp, "venv")
    venv_path_for_later = venv_dir
    cp = subprocess.run([sys.executable, "-m", "venv", venv_dir], capture_output=True, text=True)
    if cp.returncode != 0:
        print("venv creation skipped:", cp.stderr.strip()[:200])
    else:
        bindir = "Scripts" if os.name == "nt" else "bin"
        vpy = os.path.join(venv_dir, bindir, "python.exe" if os.name == "nt" else "python")
        print("venv created. Contents of its", bindir, "folder:", sorted(os.listdir(os.path.join(venv_dir, bindir)))[:8])
        with open(os.path.join(venv_dir, "pyvenv.cfg")) as f:
            print("pyvenv.cfg keys:", [l.split("=")[0].strip() for l in f if "=" in l])

        out, _ = run(vpy, "-c",
                     "import sys; print('in venv:', sys.prefix != sys.base_prefix)")
        print("venv python ->", out)
        out, _ = run(vpy, "-c", "import sys; print(sys.prefix)")
        print("venv sys.prefix is our temp venv:", out == os.path.realpath(venv_dir) or out == venv_dir)
        out, _ = run(vpy, "-m", "pip", "--version")
        print("venv pip   ->", out.split(" from ")[0], "(lives inside the venv)")
        out, _ = run(vpy, "-m", "pip", "list", "--disable-pip-version-check")
        pkgs = [l.split()[0] for l in out.splitlines()[2:]]
        print("venv pip list ->", pkgs, "(a fresh venv is nearly empty)")
        out, _ = run(vpy, "-c", "import site; print([p for p in site.getsitepackages()][0].endswith('site-packages'))")
        print("venv has its own site-packages:", out)
print("temp venv deleted:", not os.path.exists(venv_path_for_later))

# 11. pip, freeze, requirements.txt, uv, pipx (reference - NOT executed)
# ------------------------------------
print("\n# 11. Package management (reference, not run: needs the network)")
notes = """\
pip install requests           install the newest version into the ACTIVE env
pip install "requests==2.31.0" pin an exact version
pip install -U requests        upgrade
pip uninstall requests         remove
pip list                       what is installed here
pip show requests              details: version, location, dependencies
pip freeze > requirements.txt  snapshot exact versions (commit this file)
pip install -r requirements.txt  recreate the same environment elsewhere
uv                             a much faster, all-in-one replacement for pip + venv:
                               `uv venv`, `uv pip install ...`, `uv add ...`
pipx install black             install a command-line TOOL in its own hidden venv
                               (use pipx for apps, pip for libraries your code imports)
pyproject.toml                 the modern project file: name, version, dependencies,
                               and tool settings (black/ruff/pytest) in one place."""
print(textwrap.indent(notes, "  "))

# 12. `pip` vs `python -m pip` - a classic gotcha
# ------------------------------------
# - `pip` is whatever script is first on PATH; it may belong to a DIFFERENT
#   Python than the one you are using -> you install a package, then
#   `import` says ModuleNotFoundError.
# - `python -m pip` runs pip FOR that exact interpreter. Same for `python -m venv`,
#   `python -m pytest`. When in doubt, use the -m form.

print("\n# 12. pip vs python -m pip")
print("`pip` found on PATH   :", shutil.which("pip"))
print("`python3` found on PATH:", shutil.which("python3"))
print("this interpreter       :", sys.executable)
out, _ = run(sys.executable, "-m", "pip", "--version")
print("python -m pip --version:", out.split(" from ")[0] if out else "pip not installed here")
print("If those paths point to different installs, `pip install x` is not")
print("installing into the Python you are running right now.")

# 13. How Python finds modules: sys.path and PYTHONPATH
# ------------------------------------
# - `import foo` searches, in order:
#     1. already-imported modules (sys.modules cache)
#     2. each folder in sys.path, left to right:
#          - the script's folder (or '' = current dir for -c / REPL)
#          - folders in the PYTHONPATH environment variable
#          - the standard library
#          - site-packages (where pip installs things)
# - First match wins. GOTCHA: naming your file `random.py` or `json.py`
#   shadows the real stdlib module -> baffling errors. Never reuse stdlib names.
# - PYTHONPATH is a quick way to add a folder without code changes.
# - Proper projects avoid PYTHONPATH tricks: they use packages + pyproject.toml
#   and `pip install -e .` (editable install).

print("\n# 13. sys.path and PYTHONPATH")
print("sys.path[0] (this script's folder):", os.path.basename(sys.path[0]))
print(f"sys.path has {len(sys.path)} entries; site-packages is on it:",
      any(p.endswith("site-packages") for p in sys.path))
print("entry names:", [os.path.basename(p) or "''" for p in sys.path])
with tempfile.TemporaryDirectory() as tmp:
    with open(os.path.join(tmp, "secret_helper.py"), "w") as f:
        f.write("MESSAGE = 'found via PYTHONPATH'\n")
    code = "import secret_helper; print(secret_helper.MESSAGE)"
    out, err = run(sys.executable, "-c", code)
    print("without PYTHONPATH:", err.splitlines()[-1] if err else out)
    env = dict(os.environ, PYTHONPATH=tmp)
    out, err = run(sys.executable, "-c", code, env=env)
    print("with PYTHONPATH   :", out or err)
if hasattr(sys, "stdlib_module_names"):  # added in Python 3.10
    print("stdlib modules known:", len(sys.stdlib_module_names), "| 'json' in it:", "json" in sys.stdlib_module_names)
else:
    print("sys.stdlib_module_names skipped: needs Python 3.10+")

# 14. Common beginner errors - read the message, it tells you the fix
# ------------------------------------
# - A traceback reads bottom-up: LAST line = error type + message,
#   lines above = where it happened. Start at the bottom.
# - Each case below is triggered on purpose and caught with try/except.

print("\n# 14. Common beginner errors")


def show_error(label, fn, meaning):
    try:
        fn()
    except Exception as e:
        print(f"{label}\n   {type(e).__name__}: {e}\n   meaning: {meaning}")


# SyntaxError: the code is not valid Python at all - nothing runs.
# compile() lets us check text without running it.
show_error("SyntaxError  (if x = 3:)",
           lambda: compile("if x = 3:\n    pass", "<demo>", "exec"),
           "You used = (assign) where == (compare) was needed, or typed something Python can't parse.")
show_error("SyntaxError  (missing bracket)",
           lambda: compile("print('hi'", "<demo>", "exec"),
           "A bracket or quote was opened and never closed. Look at the line BEFORE the reported one too.")

# IndentationError is a subclass of SyntaxError.
show_error("IndentationError",
           lambda: compile("def f():\nprint(1)", "<demo>", "exec"),
           "A block (after ':') must be indented. Use 4 spaces consistently.")
print("   IndentationError is a SyntaxError subclass:", issubclass(IndentationError, SyntaxError))


def name_error():
    return undefined_variable + 1  # noqa: F821 - deliberate


show_error("NameError", name_error,
           "You used a name that was never defined: typo, wrong case (True vs true), or used before assignment.")
show_error("TypeError (str + int)", lambda: "5" + 5,
           "Operation on the wrong kind of value. Convert first: int('5') + 5 or '5' + str(5).")
show_error("TypeError (wrong argument type)", lambda: len(5),
           "A function got an argument of a type it cannot handle.")
show_error("ModuleNotFoundError", lambda: importlib.import_module("definitely_not_installed_xyz"),
           "Module isn't on sys.path: not installed in THIS Python (see pip vs python -m pip) or misspelled.")
show_error("ImportError (name missing inside real module)",
           lambda: exec("from math import not_a_function"),
           "The module exists but has no such name. ModuleNotFoundError is a subclass of ImportError.")
print("   ModuleNotFoundError is an ImportError subclass:", issubclass(ModuleNotFoundError, ImportError))

# 15. Quick checklist
# ------------------------------------
print("\n# 15. Quick checklist")
print("1. python3 --version, and check sys.executable when something is odd")
print("2. one venv per project: python3 -m venv .venv")
print("3. install with `python -m pip install ...`")
print("4. guard demos with `if __name__ == '__main__':`")
print("5. explore with type / dir / help instead of guessing")
print("6. follow PEP 8 and let ruff/black do the policing")
print("7. read tracebacks from the BOTTOM line up")

# 16. Notebooks: Jupyter and Google Colab - what they are
# ------------------------------------
# - A NOTEBOOK is a document made of CELLS. Each cell is either code or
#   Markdown text. You run a code cell and its output appears right below it.
# - A KERNEL is the Python process behind the notebook. It stays alive between
#   cells, so variables from one cell are visible in the next (this matters
#   for the "hidden state" gotcha in section 22).
# - Jupyter = the open-source notebook tool you run yourself (JupyterLab is
#   the modern interface). Google Colab = Google's hosted Jupyter-style
#   notebooks: nothing to install, runs in the browser on Google's machines.
# - A notebook file ends in `.ipynb` and is plain JSON (proved in section 17).
import json
import runpy
import timeit

print("\n# 16. Notebooks: Jupyter and Google Colab")
print("cell    = a block of code or Markdown you run/render on its own")
print("kernel  = the running Python process; it remembers variables between cells")
print(".ipynb  = the notebook file; it is JSON, not Python")

# 17. PROOF: an .ipynb file is just JSON
# ------------------------------------
# - We build the smallest valid "nbformat 4" notebook as a normal Python dict,
#   write it with json, read it back, and list its cells. No Jupyter needed.
# - Top-level keys: nbformat (4), nbformat_minor, metadata, cells.
#   Each cell has: cell_type, id (from nbformat 4.5), metadata, source
#   (+ execution_count and outputs for code cells).
print("\n# 17. An .ipynb file is just JSON")

notebook = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
        "language_info": {"name": "python"},
    },
    "cells": [
        {"cell_type": "markdown", "id": "intro", "metadata": {},
         "source": ["# Demo notebook\n", "Cells are stored as lists of lines."]},
        {"cell_type": "code", "id": "calc", "metadata": {}, "execution_count": None, "outputs": [],
         "source": ["x = 6\n", "y = 7\n", "x * y"]},
        {"cell_type": "code", "id": "show", "metadata": {}, "execution_count": None, "outputs": [],
         "source": ["print('x is', x)"]},
    ],
}

with tempfile.TemporaryDirectory() as tmp:
    nb_path = os.path.join(tmp, "demo.ipynb")
    with open(nb_path, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)                 # a notebook IS this JSON text
    with open(nb_path, encoding="utf-8") as f:
        raw_text = f.read()
        f.seek(0)
        loaded = json.load(f)

print("file starts with :", repr(raw_text[:20]), "...")
print("nbformat         :", loaded["nbformat"], "minor", loaded["nbformat_minor"])
for i, cell in enumerate(loaded["cells"], 1):
    first_line = "".join(cell["source"]).splitlines()[0]
    print(f"  cell {i}: type={cell['cell_type']:8} first line={first_line!r}")
print("code cells only  :", [c["id"] for c in loaded["cells"] if c["cell_type"] == "code"])
print("round trip equal :", loaded == notebook)

# Optional extra: the real `nbformat` library can validate it, IF installed.
try:
    import nbformat
    nbformat.validate(nbformat.from_dict(loaded))        # raises ValidationError if the structure is wrong
    print("nbformat library : installed, validation passed (version", nbformat.__version__ + ")")
except ImportError:
    print("nbformat library : not installed -> validation demo skipped (pip install nbformat)")
except Exception as e:                                   # a library problem must not break this file
    print("nbformat library : validation skipped:", type(e).__name__, e)
print("# - GOTCHA: because it is JSON, outputs (even big images) are stored INSIDE the file.")

# 18. Notebook vs `.py` script - which to use, and why this repo uses .py
# ------------------------------------
print("\n# 18. Notebook vs script")
print("Notebooks are great for : exploring data, quick experiments, plots, teaching, sharing results")
print("Scripts (.py) are better: real programs, imports from other files, tests, git diffs, CI, servers")
print("Why this repo uses .py  :")
print("  - diffs     : a .py change is a few readable lines; an .ipynb diff is noisy JSON (outputs, counters, ids)")
print("  - tests     : you can `import` a .py module and unit-test it; a notebook cannot be imported cleanly")
print("  - order     : a script runs top to bottom, every time (no hidden state, see section 22)")
print("  - tools     : linters, formatters and type checkers work on .py out of the box")

# 19. Installing and starting Jupyter (reference - NOT executed)
# ------------------------------------
# - Do this inside a virtual environment (section 10).
# - `python -m ipykernel install` registers a venv as a kernel, so the
#   notebook can run code with THAT venv's packages (otherwise it may pick
#   the wrong Python - the notebook version of the pip-vs-python gotcha).
print("\n# 19. Install and start Jupyter (reference, not run)")
notes = """\
python3 -m venv .venv && source .venv/bin/activate
python -m pip install jupyterlab           install JupyterLab (also installs the kernel pieces)
jupyter lab                                start it; opens http://localhost:8888 in your browser
jupyter notebook                           the older, simpler single-notebook interface
python -m pip install ipykernel            (if only the kernel is missing)
python -m ipykernel install --user --name my-venv --display-name "Python (my-venv)"
                                           make THIS venv appear in the notebook's kernel list
jupyter kernelspec list                    see every registered kernel
jupyter kernelspec remove my-venv          unregister it
VS Code                                    can also open .ipynb files (needs the Jupyter extension)"""
print(textwrap.indent(notes, "  "))

# 20. Magic commands and shell escapes - and the plain-Python equivalent
# ------------------------------------
# - Inside Jupyter/Colab (IPython), a line starting with % is a MAGIC command
#   (%% = whole-cell magic) and a line starting with ! is a SHELL command.
#   They are NOT Python syntax: in a .py file they are a SyntaxError.
# - Everything they do has a plain-Python equivalent, which also works in
#   scripts. We run the equivalents below.
print("\n# 20. Magics / shell escapes (reference) and the plain-Python equivalents")
notes = """\
%timeit sum(range(1000))     time a statement          ->  timeit.timeit(...)
%run other.py                run a file in this kernel ->  runpy.run_path("other.py")
!pip install requests        run a shell command       ->  subprocess.run([...])
%pip install requests        installs into THIS kernel's Python (prefer it over !pip)
%who / %whos                 list variables            ->  dir() / globals()
%matplotlib inline           show plots under the cell"""
print(textwrap.indent(notes, "  "))

secs = timeit.timeit("sum(range(1000))", number=2000)
print(f"timeit equivalent : 2000 runs took {secs:.4f}s (value varies by machine)")

with tempfile.TemporaryDirectory() as tmp:
    other = os.path.join(tmp, "other.py")
    with open(other, "w") as f:
        f.write("answer = 6 * 7\nprint('other.py ran')\n")
    result = runpy.run_path(other)                       # like %run: executes the file, returns its globals
    print("runpy equivalent  : answer =", result["answer"])

cp = subprocess.run([sys.executable, "-m", "pip", "--version"], capture_output=True, text=True)
print("subprocess (like !pip --version):", cp.stdout.split(" from ")[0] or cp.stderr.strip()[:60])
print("# - GOTCHA: `!pip` can belong to a different Python than the kernel. `%pip` (or")
print("#   `python -m pip`) targets the right one. Restart the kernel after installing.")

# 21. Google Colab specifics (reference - NOT executed)
# ------------------------------------
# - Colab gives you a notebook on a temporary cloud VM: free to start, no
#   setup, can use a GPU/TPU. The price: it is EPHEMERAL.
print("\n# 21. Google Colab (reference, not run)")
notes = """\
Ephemeral VM        files, installed packages and variables vanish when the runtime is
                    recycled (idle timeout / session limit). Save results to Drive or download.
!pip install pkg    needed again after every fresh runtime (put installs in the first cell).
Mount Drive         from google.colab import drive
                    drive.mount('/content/drive')    # asks you to log in and allow access
                    -> your files appear under /content/drive/MyDrive
GPU/TPU             Runtime > Change runtime type > pick a GPU. Check with `!nvidia-smi`.
Working folder      /content  (temporary - not your computer's files)
Upload/download     the Files side panel, or `from google.colab import files`
Secrets             use the key icon (Secrets) - never paste API keys into a shared notebook
Preinstalled        numpy, pandas, matplotlib, etc. - often no install needed
Colab-only code     `import google.colab` works ONLY there; guard it (see section 24)"""
print(textwrap.indent(notes, "  "))

# 22. The hidden-state gotcha: cells can run in ANY order
# ------------------------------------
# - The kernel keeps ONE shared namespace. You can run cells in any order, run
#   one twice, or delete a cell - the variables from earlier runs stay.
#   The notebook may then show results that a clean top-to-bottom run would
#   NOT produce, and you cannot tell by looking.
# - Simulation: each "cell" is a string; `exec` runs it against one shared
#   dict, exactly like a kernel does.
print("\n# 22. Hidden state: cells run out of order")
cells = {
    "cell A": "x = 10",
    "cell B": "x = x * 2",
    "cell C": "print('   x is now', x)",
}


def run_cells(order, namespace=None):
    ns = {} if namespace is None else namespace
    for name in order:
        print(f"  run {name}: {cells[name]}")
        exec(cells[name], ns)
    return ns


print("top to bottom (A, B, C):")
run_cells(["cell A", "cell B", "cell C"])
print("you re-run B by accident, then C (A, B, B, C):")
run_cells(["cell A", "cell B", "cell B", "cell C"])
print("kernel never restarted; B run again after C (A, B, C, B, C):")
run_cells(["cell A", "cell B", "cell C", "cell B", "cell C"])
print("  -> the notebook reads 'x = 10 then x = x * 2' but shows 40: the page lies, the kernel state decides.")

print("stale variable: you delete the cell that defined `y`, but `y` is still alive in the kernel:")
kernel = {}
exec("y = 5", kernel)                                    # cell ran once, then you deleted it
exec("print('   cell D still works, y =', y)", kernel)
try:
    exec("print(y)", {})                                 # a fresh kernel / 'Restart & Run All'
except NameError as e:
    print("   fresh run fails:", e)
print("# - Fix: use 'Restart Kernel and Run All' before trusting or sharing a notebook;")
print("#   keep cells in dependency order; move reusable code into a .py module.")

# 23. Converting a notebook to a script
# ------------------------------------
# - `jupyter nbconvert --to script notebook.ipynb` writes notebook.py: code
#   cells become code, Markdown cells become comments. This repo's own
#   history did exactly that, turning notebooks into the .py files you read.
# - Under the hood it is a simple walk over the JSON from section 17, which we
#   imitate here (so you can see there is no magic).
print("\n# 23. Notebook -> script")
print("  jupyter nbconvert --to script notebook.ipynb     writes notebook.py")
print("  jupyter nbconvert --to html notebook.ipynb       a shareable web page")
print("  jupyter nbconvert --to notebook --execute nb.ipynb   run all cells and save outputs")
script_lines = []
for cell in loaded["cells"]:
    text = "".join(cell["source"])
    if cell["cell_type"] == "markdown":
        script_lines.extend("# " + line for line in text.splitlines())
    else:
        script_lines.extend(text.splitlines())
    script_lines.append("")
print("hand-rolled conversion of our demo notebook:")
print(textwrap.indent("\n".join(script_lines).rstrip(), "  | "))
print("# - Magics (%timeit, !pip) become get_ipython().run_line_magic(...) calls in the .py -")
print("#   clean those up by hand, or the script will only run inside IPython.")

# 24. Detecting whether code runs inside Jupyter / Colab
# ------------------------------------
# - Notebook kernels import `ipykernel`, so `'ipykernel' in sys.modules` is
#   True there. Plain `python file.py` never imports it.
# - IPython also injects `get_ipython()` into the notebook's namespace. In a
#   normal script that name does not exist -> NameError. Importing IPython
#   in a script does NOT make this True; check the *running* shell instead.
# - Colab adds `google.colab` to sys.modules.
print("\n# 24. Which environment am I in?")


def detect_environment():
    if "google.colab" in sys.modules:
        return "Google Colab notebook"
    ipython = sys.modules.get("IPython")
    shell = ipython.get_ipython() if ipython else None   # None when no interactive shell is running
    if shell is None:
        return "plain Python (script or REPL)"
    if "ipykernel" in sys.modules:
        return "Jupyter notebook / kernel"
    return "IPython terminal"


print("'ipykernel' in sys.modules :", "ipykernel" in sys.modules)
print("get_ipython defined here?  :", "get_ipython" in dir(__builtins__) or "get_ipython" in globals())
print("this file is running in    :", detect_environment())
print("# - Use this to skip notebook-only code (progress bars, display()) when run as a script.")

# 25. Is Jupyter installed here?
# ------------------------------------
# - importlib.util.find_spec checks for a package WITHOUT importing it.
print("\n# 25. Is Jupyter installed in THIS Python?")
import importlib.util

for pkg in ("jupyterlab", "notebook", "ipykernel", "IPython", "nbformat", "nbconvert"):
    found = importlib.util.find_spec(pkg) is not None
    print(f"  {pkg:10}:", "installed" if found else "not installed (python -m pip install " + pkg.lower() + ")")
print("# - Missing is fine: every demo above ran without any of them.")
