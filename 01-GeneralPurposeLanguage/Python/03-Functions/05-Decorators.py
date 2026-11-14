import functools
import time

# 01. Decorators - Introduction
# ------------------------------------
# - A decorator is a function that takes another function (or class) and
#   extends/modifies its behavior without permanently changing its code.
# - Possible because functions are first-class objects in Python -
#   they can be passed around and returned like any other value.

print("# 01. Decorators - Introduction")
print("# ------------------------------------")

# 02. Functions as First-Class Objects (recap)
# ------------------------------------
def shout(text):
    return text.upper()

def greet(func):
    return func("hello")

print("\n# 02. Functions as First-Class Objects")
print(greet(shout))

# 03. Writing a Basic Decorator
# ------------------------------------
def my_decorator(func):
    def wrapper():
        print("Something before the function runs.")
        func()
        print("Something after the function runs.")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

print("\n# 03. Writing a Basic Decorator")
say_hello()
# Equivalent to: say_hello = my_decorator(say_hello)

# 04. Decorating Functions with Arguments
# ------------------------------------
def logger(func):
    @functools.wraps(func)  # preserves original function's name/docstring
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result}")
        return result
    return wrapper

@logger
def add(a, b):
    """Add two numbers."""
    return a + b

print("\n# 04. Decorating Functions with Arguments")
add(3, 5)
print("name preserved by functools.wraps:", add.__name__)

# 05. Decorators with Arguments (decorator factory)
# ------------------------------------
def repeat(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(times=3)
def say_hi():
    print("Hi!")

print("\n# 05. Decorators with Arguments")
say_hi()

# 06. Chaining Multiple Decorators
# ------------------------------------
def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<b>{func(*args, **kwargs)}</b>"
    return wrapper

def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return f"<i>{func(*args, **kwargs)}</i>"
    return wrapper

@bold
@italic
def message():
    return "Hello"

print("\n# 06. Chaining Multiple Decorators")
print(message())  # applied bottom-up: bold(italic(message))

# 07. Practical Example - Timing a Function
# ------------------------------------
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {end - start:.6f} seconds")
        return result
    return wrapper

@timer
def compute_sum(n):
    return sum(range(n))

print("\n# 07. Practical Example - Timing a Function")
compute_sum(1_000_000)

# 08. Class-Based Decorators
# ------------------------------------
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        print(f"Call {self.calls} of {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def say_bye():
    print("Bye!")

print("\n# 08. Class-Based Decorators")
say_bye()
say_bye()

# 09. Built-in Decorators Recap (@staticmethod, @classmethod, @property)
# ------------------------------------
# - Covered in depth in 04-OOPs/02-Encapsulation.py; mentioned here as they
#   are decorators too, just applied to methods inside a class.
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def radius(self):
        return self._radius

    @radius.setter
    def radius(self, value):
        if value < 0:
            raise ValueError("radius cannot be negative")
        self._radius = value

print("\n# 09. Built-in Decorators Recap")
c = Circle(5)
print("radius via @property:", c.radius)
c.radius = 10
print("radius after @radius.setter:", c.radius)

# 10. Decorator with Optional Arguments (works as @deco or @deco(arg=1))
# ------------------------------------
# - Normally a decorator factory always needs parentheses: @repeat(times=3).
# - To support BOTH @deco and @deco(arg=1), check whether the single
#   positional argument received is the function itself (bare usage) or None
#   (parameterized usage), and branch accordingly.
def smart_decorator(func=None, *, greeting="Hello"):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            print(f"{greeting}, calling {f.__name__}")
            return f(*args, **kwargs)
        return wrapper
    if func is not None:
        return decorator(func) # bare usage: @smart_decorator - func is the target function
    return decorator # parameterized usage: @smart_decorator(greeting="Hi") - func is None

@smart_decorator
def bare_call():
    return "bare"

@smart_decorator(greeting="Hi")
def parameterized_call():
    return "parameterized"

print("\n# 10. Decorator with Optional Arguments")
print("bare_call():", bare_call())
print("parameterized_call():", parameterized_call())

# 11. Stacking Order Edge Cases - Mutating State Across Stacked Decorators
# ------------------------------------
# - Decorators apply bottom-up, but shared MUTABLE state (like a list defined
#   outside) lets stacked decorators see each other's side effects - the
#   order they're stacked in changes what each one observes.
call_log = []

def track(label):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            call_log.append(f"before {label}") # mutating shared state
            result = func(*args, **kwargs)
            call_log.append(f"after {label}")
            return result
        return wrapper
    return decorator

@track("outer")
@track("inner")
def action():
    call_log.append("action running")

print("\n# 11. Stacking Order Edge Cases")
action()
print("call_log order:", call_log) # shows outer wraps inner - inner's effects are nested inside outer's

# 12. Class-Based Decorator with __set_name__
# ------------------------------------
# - __set_name__(self, owner, name) is called automatically when a descriptor
#   (here, our decorator instance) is assigned as a class attribute - it tells
#   the descriptor its owning class and the attribute name it was bound to.
class LoggedMethod:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
    def __set_name__(self, owner, name):
        print(f"LoggedMethod bound to {owner.__name__}.{name}")
    def __get__(self, instance, owner):
        if instance is None:
            return self
        return functools.partial(self.func, instance)

class Robot:
    @LoggedMethod
    def move(self):
        return "Robot moving"

print("\n# 12. Class-Based Decorator with __set_name__")
robot = Robot()
print("robot.move():", robot.move())

# 13. functools.singledispatch as a Decorator
# ------------------------------------
# - singledispatch is itself implemented as a decorator - it wraps a function
#   and lets you register type-specific overloads with @func.register, using
#   the same wrapping mechanics as the decorators above.
@functools.singledispatch
def render(value):
    return f"generic: {value}"

@render.register
def _(value: int):
    return f"int: {value}"

print("\n# 13. functools.singledispatch as a Decorator")
print("render('text'):", render("text"))
print("render(42):", render(42))

# 14. functools.wraps vs inspect.signature - Why Both Matter
# ------------------------------------
# - Without @functools.wraps, a wrapper function's __name__/__doc__ become the
#   WRAPPER's, not the original's - confusing for debugging and documentation.
# - functools.wraps also copies __wrapped__, which inspect.signature() follows
#   to report the ORIGINAL function's signature, not wrapper(*args, **kwargs).
# - Without @wraps, inspect.signature() would show the wrapper's generic
#   (*args, **kwargs) signature instead of the real one.
import inspect

def undecorated_logger(func):
    def wrapper(*args, **kwargs): # no @functools.wraps applied here
        return func(*args, **kwargs)
    return wrapper

def decorated_logger(func):
    @functools.wraps(func) # preserves __name__, __doc__, and __wrapped__
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@undecorated_logger
def without_wraps(a, b):
    """Adds two numbers."""
    return a + b

@decorated_logger
def with_wraps(a, b):
    """Adds two numbers."""
    return a + b

print("\n# 14. functools.wraps vs inspect.signature")
print("without_wraps.__name__:", without_wraps.__name__)         # 'wrapper' - lost!
print("with_wraps.__name__:", with_wraps.__name__)               # 'with_wraps' - preserved
print("inspect.signature(without_wraps):", inspect.signature(without_wraps)) # (*args, **kwargs)
print("inspect.signature(with_wraps):", inspect.signature(with_wraps))       # (a, b) - correct
