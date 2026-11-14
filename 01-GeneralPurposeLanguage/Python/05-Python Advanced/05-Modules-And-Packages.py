import math                       # 02. import a built-in module
import math as m                  # 03. import with an alias
from math import sqrt             # 04. import a specific name
from math import pi as PI         # 05. import a specific name with an alias

# 01. Modules and Packages - Introduction
# ------------------------------------
# - A module is a single .py file containing code (functions, classes, vars).
# - A package is a directory of modules, marked with an __init__.py file.
# - Splitting code this way keeps large programs organized and reusable.

print("# 01. Modules and Packages - Introduction")
print("# ------------------------------------")

# 02-05. Different Import Styles (see imports at top of file)
# ------------------------------------
print("\n# 02-05. Different Import Styles")
print("math.sqrt(16):", math.sqrt(16))
print("m.pi (aliased module):", m.pi)
print("sqrt(25) (imported name directly):", sqrt(25))
print("PI (imported + aliased name):", PI)

# 06. import * - Import Everything (generally discouraged)
# ------------------------------------
print("\n# 06. import * (discouraged)")
print("# - from module import * pulls all public names into current namespace.")
print("# - Avoid: makes it unclear where a name came from, risks name clashes.")

# 07. dir() - Inspecting a Module's Contents
# ------------------------------------
print("\n# 07. dir() - Inspecting a Module's Contents")
print([name for name in dir(math) if not name.startswith("_")][:10], "...")

# 08. The __name__ == "__main__" Idiom
# ------------------------------------
# - Every module has a __name__ variable.
# - When run directly, __name__ == "__main__".
# - When imported by another file, __name__ == the module's own name.
print("\n# 08. __name__ == \"__main__\"")
print("this file's __name__:", __name__)
print("# - Code inside `if __name__ == \"__main__\":` only runs when the")
print("#   file is executed directly, not when it's imported elsewhere.")

# 09. Creating and Importing Your Own Module
# ------------------------------------
# - See demo_package/helper.py and demo_package/math_utils.py next to this file.
# - Python automatically adds a directly-run script's own folder to sys.path,
#   so the sibling demo_package/ is importable without any extra setup.
from demo_package import helper
from demo_package.math_utils import add, multiply

print("\n# 09. Creating and Importing Your Own Module")
print(helper.GREETING)
print("helper.shout('hi'):", helper.shout("hi"))
print("add(2, 3):", add(2, 3))
print("multiply(4, 5):", multiply(4, 5))

# 10. Package Structure (reference)
# ------------------------------------
print("\n# 10. Package Structure (reference)")
print("# demo_package/")
print("#   __init__.py     <- marks the folder as a package")
print("#   helper.py       <- a module inside the package")
print("#   math_utils.py   <- another module inside the package")

# 11. Standard Library, Third-Party, and Local Modules
# ------------------------------------
print("\n# 11. Standard Library, Third-Party, and Local Modules")
print("# - Standard library: ships with Python (math, os, sys, json, ...)")
print("# - Third-party: installed via pip (requests, numpy, pandas, ...)")
print("# - Local: modules/packages you write yourself in the project")

# 12. Virtual Environments and pip (reference, not executed)
# ------------------------------------
print("\n# 12. Virtual Environments and pip (reference)")
print("# python -m venv venv          create a virtual environment")
print("# source venv/bin/activate     activate it (macOS/Linux)")
print("# pip install requests         install a third-party package")
print("# pip freeze > requirements.txt   save installed packages")
print("# pip install -r requirements.txt install from that file")

# 13. __all__ - Controlling `from module import *`
# ------------------------------------
# - __all__ is a list of names, defined at module level, that explicitly
#   controls what `import *` pulls in. Anything not listed is skipped by
#   the star-import (though still reachable via a normal dotted import).
# - See demo_package/extra.py: __all__ = ["public_function", "PUBLIC_CONSTANT"]
print("\n# 13. __all__ Controls import *")
from demo_package.extra import *  # only names in __all__ come in

print("public_function() available:", public_function())
print("PUBLIC_CONSTANT available:", PUBLIC_CONSTANT)
print("_private_function was NOT imported by *:", "_private_function" not in dir())

import demo_package.extra as extra_module
print("but it's still reachable via the module itself:", extra_module._private_function())

# 14. Relative Imports Within a Package (conceptual)
# ------------------------------------
# - Inside a package, modules can import siblings with a LEADING DOT instead
#   of the full dotted path. demo_package is flat here (no sub-packages),
#   so this is explained rather than executed - the syntax still matters.
print("\n# 14. Relative Imports (conceptual, not run here)")
print("# If helper.py needed something from math_utils.py in the SAME package:")
print("#     from . import math_utils        # '.'  = current package")
print("#     from .math_utils import add     # import a specific name")
print("# If math_utils.py needed something from a PARENT package:")
print("#     from .. import some_module      # '..' = parent package")
print("# Relative imports only work inside a package (never in a script run directly).")

# 15. importlib.import_module() - Dynamic Imports
# ------------------------------------
# - Sometimes the module name is only known at runtime (e.g. from a config
#   file or plugin system). importlib.import_module() imports by STRING name.
import importlib

print("\n# 15. importlib.import_module() for Dynamic Imports")
module_name = "math"  # could come from user input / config
dynamic_math = importlib.import_module(module_name)
print(f"dynamically imported '{module_name}', dynamic_math.sqrt(9):", dynamic_math.sqrt(9))

# 16. Module Caching via sys.modules
# ------------------------------------
# - Python only RUNS a module's top-level code the first time it's imported.
#   Every import after that (from anywhere in the program) reuses the same
#   cached module object from sys.modules - no re-execution, no re-print.
import sys

print("\n# 16. Module Caching via sys.modules")
print("demo_package.extra already in sys.modules:", "demo_package.extra" in sys.modules)
print("importing it again - no 'module body is executing' print below:")
import demo_package.extra  # already cached, body does NOT run again
importlib.import_module("demo_package.extra")  # same story via importlib
print("(confirmed: no side-effect print appeared above this line on re-import)")

# 17. Namespace Packages (PEP 420, brief mention)
# ------------------------------------
# - Since Python 3.3, a directory WITHOUT __init__.py can still act as a
#   package (a "namespace package"), letting a single logical package be
#   split across multiple directories/distributions on disk.
# - demo_package has an __init__.py (a "regular" package) - namespace
#   packages are the __init__.py-less alternative for that specific use case.
print("\n# 17. Namespace Packages (PEP 420, brief)")
print("# - Directory with __init__.py       -> regular package")
print("# - Directory without __init__.py    -> namespace package (3.3+)")
print("# - Useful for splitting one package's code across multiple installed distributions.")
