# A second module in demo_package - exists to demonstrate __all__, dynamic
# imports, and sys.modules caching from 05-Modules-And-Packages.py.

print("demo_package.extra module body is executing (side effect, runs ONCE per process)")

# __all__ controls what `from demo_package.extra import *` pulls in.
# Names not listed here are still accessible via explicit import
# (demo_package.extra._private_function), just not via the star-import.
__all__ = ["public_function", "PUBLIC_CONSTANT"]

PUBLIC_CONSTANT = 42
_PRIVATE_CONSTANT = "not exported by import *"


def public_function():
    return "called public_function from demo_package.extra"


def _private_function():
    return "this won't be pulled in by import *"
