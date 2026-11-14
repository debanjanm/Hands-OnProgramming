from enum import Enum, IntEnum, auto

# 01. Enum - Introduction
# ------------------------------------
# - Enum defines a fixed set of named constants, safer/clearer than raw
#   strings or magic numbers scattered through code.

print("# 01. Enum - Introduction")
print("# ------------------------------------")

# 02. Defining and Using an Enum
# ------------------------------------
class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print("\n# 02. Defining and Using an Enum")
print(Color.RED)
print(Color.RED.name, "=", Color.RED.value)
print(type(Color.RED))

# 03. Without Enum - the Problem (magic values, no safety)
# ------------------------------------
def set_status_bad(status):
    if status == "active":  # typo-prone, no autocomplete, no validation
        print("Status set")

print("\n# 03. Without Enum - the Problem")
print("# - Raw strings/ints: typos slip through silently, no fixed set of values.")

# 04. auto() - Auto-Assigned Values
# ------------------------------------
class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    CLOSED = auto()

print("\n# 04. auto()")
for status in Status:
    print(status.name, "=", status.value)

# 05. Comparing Enum Members
# ------------------------------------
print("\n# 05. Comparing Enum Members")
current = Status.ACTIVE
print("current == Status.ACTIVE:", current == Status.ACTIVE)
print("current is Status.ACTIVE:", current is Status.ACTIVE)  # members are singletons

# 06. Iterating Over an Enum
# ------------------------------------
print("\n# 06. Iterating Over an Enum")
print([s.name for s in Status])

# 07. Looking Up Members by Value or Name
# ------------------------------------
print("\n# 07. Looking Up Members")
print(Status(1))               # by value
print(Status["ACTIVE"])        # by name

# 08. IntEnum - Members That Also Behave Like Ints
# ------------------------------------
class Priority(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

print("\n# 08. IntEnum")
print(Priority.HIGH > Priority.LOW)   # works like int comparison
print(Priority.HIGH + 1)               # can do int arithmetic too

# 09. Enum in Practice - Replacing Magic Values
# ------------------------------------
def set_status(status: Status):
    print(f"Status set to {status.name}")

print("\n# 09. Enum in Practice")
set_status(Status.ACTIVE)

# 10. Flag / IntFlag - Combinable Bitwise Enum Members
# ------------------------------------
# - Flag members can be OR'd together (|) into a single value, and you can
#   test membership with `in`. Each member is a distinct bit.
from enum import Flag, IntFlag

class Permission(Flag):
    READ = auto()
    WRITE = auto()
    EXECUTE = auto()

print("\n# 10. Flag / IntFlag")
user_perms = Permission.READ | Permission.WRITE
print("combined:", user_perms)
print("has READ:", Permission.READ in user_perms)
print("has EXECUTE:", Permission.EXECUTE in user_perms)

class FilePermission(IntFlag):  # also behaves like an int (e.g. chmod-style)
    READ = 4
    WRITE = 2
    EXECUTE = 1

rwx = FilePermission.READ | FilePermission.WRITE | FilePermission.EXECUTE
print("chmod-style value:", int(rwx))

# 11. Custom Methods and Properties on an Enum
# ------------------------------------
class Direction(Enum):
    NORTH = (0, 1)
    SOUTH = (0, -1)
    EAST = (1, 0)
    WEST = (-1, 0)

    @property
    def dx(self):
        return self.value[0]

    @property
    def dy(self):
        return self.value[1]

    def opposite(self):
        return {Direction.NORTH: Direction.SOUTH, Direction.SOUTH: Direction.NORTH,
                 Direction.EAST: Direction.WEST, Direction.WEST: Direction.EAST}[self]

print("\n# 11. Custom Methods/Properties on Enum")
print("NORTH delta:", Direction.NORTH.dx, Direction.NORTH.dy)
print("opposite of NORTH:", Direction.NORTH.opposite())

# 12. @unique - Forbid Duplicate Values
# ------------------------------------
from enum import unique

print("\n# 12. @unique decorator")
try:
    @unique
    class Broken(Enum):
        A = 1
        B = 1  # duplicate value - @unique catches what plain Enum allows as an alias
except ValueError as e:
    print("ValueError:", e)

# 13. StrEnum (3.11+) / Pre-3.11 str+Enum Pattern
# ------------------------------------
import sys

print("\n# 13. StrEnum / str+Enum Pattern")
if sys.version_info >= (3, 11):
    from enum import StrEnum

    class Role(StrEnum):
        ADMIN = "admin"
        USER = "user"
else:
    class Role(str, Enum):  # pre-3.11 equivalent - members ARE strings
        ADMIN = "admin"
        USER = "user"

print("Role.ADMIN:", Role.ADMIN, "| is a str:", isinstance(Role.ADMIN, str))
print("equals raw string:", Role.ADMIN == "admin")

# 14. _missing_ - Custom Lookup Fallback
# ------------------------------------
# - Called when Enum(value) doesn't match any member's value directly -
#   lets you normalize input (e.g. case-insensitive lookup) before failing.
class Size(Enum):
    SMALL = "S"
    MEDIUM = "M"
    LARGE = "L"

    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        return None  # returning None -> normal ValueError is raised

print("\n# 14. _missing_ Custom Lookup")
print(Size("s"))          # lowercase, falls back to case-insensitive match
print(Size("m"))          # lowercase, falls back to case-insensitive match
try:
    Size("XL")
except ValueError as e:
    print("ValueError:", e)
