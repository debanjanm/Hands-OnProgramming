#### 0. Function Introduction
#### 1. Basic Function Syntax/Components
####    Parameters vs Arguments
#### 2. Function with Parameters
#### 3. Function with Return Value
#### 4. Default Arguments
#### 5. Keyword Arguments
#### 6. Arbitrary Arguments (*args)
#### 7. Arbitrary Keyword Arguments (**kwargs)
#### 8. Anonymous (Lambda) Functions
#### 9. Higher-Order Functions
#### 10. Closures
#### 11. Recursion
#### 13. Advanced Decorators with Arguments
#### 14. Function Annotations (Type Hinting)
#### 15. Partial Functions (from functools)
#### 16. Function Objects (Functions as First-Class Citizens)
#### 17. Input Function
#### 18. Output Function

# Python Function Explanation

# 0. Function Introduction
# ------------------------------------
# - Functions are blocks of reusable code that perform a specific task.
# - They help in organizing code, making it modular and readable.
# - Functions are essential for code reusability, reducing redundancy and improving maintainability.
# - In Python, functions are first-class citizens, meaning they can be passed as arguments to other functions, returned as values, and assigned to variables.

print("# 0. Function Introduction")
print("# ------------------------------------")
print("# - Reusable blocks of code, modular, readable, promotes reusability.")
print("# - Functions are first-class citizens in Python.")

# 1. Basic Function Syntax/Components
# ------------------------------------
# - Function definition starts with the keyword `def`, followed by the function name, parentheses `()`, and a colon `:`.
# - Parameters (optional) are defined inside the parentheses.
# - The function body is indented below the definition line.
# - `Parameters` are variables listed inside the parentheses in the function definition. They receive values (arguments) when the function is called.
# - `Arguments` are the actual values that are passed to the function when it is called.

print("\n# 1. Basic Function Syntax/Components")
print("# ------------------------------------")
print("# - def function_name(parameters):")
print("#     # function body")
print("# - Parameters vs Arguments:")
print("#   - Parameters: variables in function definition (placeholders).")
print("#   - Arguments: actual values passed during function call.")

# Example of a basic function definition
def greet_user():
    """This function greets the user.""" # Docstring - describes what the function does
    print("Hello, user!")

# Function call
greet_user()
print("\n# Example - Basic Function")
print("# Function definition:")
print("def greet_user():")
print("    print(\"Hello, user!\")")
print("# Function call:")
print("greet_user()")
print("# Output:")
greet_user()

# 2. Function with Parameters
# ------------------------------------
# - Functions can accept parameters to work with different inputs.
# - Parameters are specified inside the parentheses in the function definition.

print("\n# 2. Function with Parameters")
print("# ------------------------------------")
print("# - Functions can accept parameters as input.")

def greet_person(name):
    """This function greets the person passed as parameter."""
    print(f"Hello, {name}!")

# Function calls with different arguments
greet_person("Alice")
greet_person("Bob")
print("\n# Example - Function with Parameters")
print("# Function definition:")
print("def greet_person(name):")
print("    print(f\"Hello, {name}!\")")
print("# Function calls:")
print("greet_person(\"Alice\")")
print("greet_person(\"Bob\")")
print("# Output:")
greet_person("Alice")
greet_person("Bob")

# 3. Function with Return Value
# ------------------------------------
# - Functions can return a value using the `return` statement.
# - The returned value can be used in other parts of the program.
# - If no `return` statement is specified, the function implicitly returns `None`.

print("\n# 3. Function with Return Value")
print("# ------------------------------------")
print("# - Functions can return a value using 'return' statement.")

def add_numbers(num1, num2):
    """This function adds two numbers and returns the sum."""
    sum_result = num1 + num2
    return sum_result

# Calling function and using the return value
result = add_numbers(5, 3)
print("\n# Example - Function with Return Value")
print("# Function definition:")
print("def add_numbers(num1, num2):")
print("    sum_result = num1 + num2")
print("    return sum_result")
print("# Function call and using return value:")
print("result = add_numbers(5, 3)")
print("print(\"Result:\", result)")
print("# Output:")
print("Result:", result)

# 4. Default Arguments
# ------------------------------------
# - Default arguments allow you to specify a default value for parameters.
# - If no argument is passed for a parameter with a default value during function call, the default value is used.

print("\n# 4. Default Arguments")
print("# ------------------------------------")
print("# - Parameters can have default values.")

def power(base, exponent=2):
    """This function calculates the power of a number, exponent defaults to 2."""
    return base ** exponent

# Function calls with and without providing the exponent argument
power_of_2 = power(4) # Exponent is default 2
power_of_3 = power(4, 3) # Exponent is provided as 3
print("\n# Example - Default Arguments")
print("# Function definition:")
print("def power(base, exponent=2):")
print("    return base ** exponent")
print("# Function calls:")
print("power_of_2 = power(4)")
print("power_of_3 = power(4, 3)")
print("print(\"Power of 2:\", power_of_2)")
print("print(\"Power of 3:\", power_of_3)")
print("# Output:")
print("Power of 2:", power_of_2)
print("Power of 3:", power_of_3)

# 5. Keyword Arguments
# ------------------------------------
# - Keyword arguments allow you to pass arguments to a function by explicitly naming the parameters.
# - This makes function calls more readable, especially for functions with many parameters, and allows arguments to be passed in any order.

print("\n# 5. Keyword Arguments")
print("# ------------------------------------")
print("# - Arguments passed with parameter names.")

def describe_pet(animal_type, pet_name):
    """This function describes a pet."""
    print(f"\nI have a {animal_type} named {pet_name}.")

# Function calls using keyword arguments
describe_pet(animal_type="hamster", pet_name="Harry") # Order doesn't matter with keywords
describe_pet(pet_name="Lucy", animal_type="dog") # Order doesn't matter with keywords
describe_pet("cat", "Milo") # Positional arguments still work
print("\n# Example - Keyword Arguments")
print("# Function definition:")
print("def describe_pet(animal_type, pet_name):")
print("    print(f\"\\nI have a {animal_type} named {pet_name}.\")")
print("# Function calls:")
print("describe_pet(animal_type=\"hamster\", pet_name=\"Harry\")")
print("describe_pet(pet_name=\"Lucy\", animal_type=\"dog\")")
print("describe_pet(\"cat\", \"Milo\")")
print("# Output:")
describe_pet(animal_type="hamster", pet_name="Harry")
describe_pet(pet_name="Lucy", animal_type="dog")
describe_pet("cat", "Milo")

# 6. Arbitrary Arguments (*args)
# ------------------------------------
# - `*args` is used to pass a variable number of non-keyword arguments to a function.
# - Inside the function, `args` is treated as a tuple containing all the passed arguments.

print("\n# 6. Arbitrary Arguments (*args)")
print("# ------------------------------------")
print("# - Used to pass variable number of non-keyword arguments.")
print("# - *args collects arguments into a tuple.")

def calculate_sum(*args):
    """This function calculates the sum of all numbers passed as arguments."""
    total = 0
    for num in args:
        total += num
    return total

# Function calls with different numbers of arguments
sum_1 = calculate_sum(1, 2, 3)
sum_2 = calculate_sum(1, 2, 3, 4, 5)
print("\n# Example - Arbitrary Arguments (*args)")
print("# Function definition:")
print("def calculate_sum(*args):")
print("    total = 0")
print("    for num in args:")
print("        total += num")
print("    return total")
print("# Function calls:")
print("sum_1 = calculate_sum(1, 2, 3)")
print("sum_2 = calculate_sum(1, 2, 3, 4, 5)")
print("print(\"Sum 1:\", sum_1)")
print("print(\"Sum 2:\", sum_2)")
print("# Output:")
print("Sum 1:", sum_1)
print("Sum 2:", sum_2)

# 7. Arbitrary Keyword Arguments (**kwargs)
# ------------------------------------
# - `**kwargs` is used to pass a variable number of keyword arguments to a function.
# - Inside the function, `kwargs` is treated as a dictionary containing all the passed keyword arguments.

print("\n# 7. Arbitrary Keyword Arguments (**kwargs)")
print("# ------------------------------------")
print("# - Used to pass variable number of keyword arguments.")
print("# - **kwargs collects keyword arguments into a dictionary.")

def build_profile(**kwargs):
    """This function builds a user profile dictionary from keyword arguments."""
    profile = {}
    for key, value in kwargs.items():
        profile[key] = value
    return profile

# Function call with different keyword arguments
user_profile = build_profile(first_name='albert', last_name='einstein', location='princeton')
print("\n# Example - Arbitrary Keyword Arguments (**kwargs)")
print("# Function definition:")
print("def build_profile(**kwargs):")
print("    profile = {}")
print("    for key, value in kwargs.items():")
print("        profile[key] = value")
print("    return profile")
print("# Function call:")
print("user_profile = build_profile(first_name='albert', last_name='einstein', location='princeton')")
print("print(\"User Profile:\", user_profile)")
print("# Output:")
print("User Profile:", user_profile)

# 8. Anonymous (Lambda) Functions
# ------------------------------------
# - Lambda functions are small, anonymous functions defined using the `lambda` keyword.
# - They can take any number of arguments but can only have one expression.
# - They are often used for short operations where a full function definition is not necessary.

print("\n# 8. Anonymous (Lambda) Functions")
print("# ------------------------------------")
print("# - Small, anonymous functions defined using 'lambda'.")
print("# - Syntax: lambda arguments: expression")

# Example lambda function to square a number
square = lambda x: x * x

# Using the lambda function
square_of_5 = square(5)
print("\n# Example - Anonymous (Lambda) Functions")
print("# Lambda function definition:")
print("square = lambda x: x * x")
print("# Function call:")
print("square_of_5 = square(5)")
print("print(\"Square of 5:\", square_of_5)")
print("# Output:")
print("Square of 5:", square_of_5)

# 9. Higher-Order Functions
# ------------------------------------
# - Higher-order functions are functions that operate on other functions, either by taking them as arguments or by returning them.
# - Examples include `map()`, `filter()`, and `sorted()`.

print("\n# 9. Higher-Order Functions")
print("# ------------------------------------")
print("# - Functions that operate on other functions.")
print("# - Examples: map(), filter(), sorted().")

def operate_on_list(func, data_list):
    """This is a higher-order function that applies a function to each item in a list."""
    return [func(item) for item in data_list]

# Example function to double a number
def double_number(n):
    return n * 2

numbers = [1, 2, 3, 4]
doubled_numbers = operate_on_list(double_number, numbers) # Passing function 'double_number' as argument
print("\n# Example - Higher-Order Functions")
print("# Higher-order function definition:")
print("def operate_on_list(func, data_list):")
print("    return [func(item) for item in data_list]")
print("# Example function:")
print("def double_number(n):")
print("    return n * 2")
print("# Using higher-order function:")
print("numbers = [1, 2, 3, 4]")
print("doubled_numbers = operate_on_list(double_number, numbers)")
print("print(\"Doubled numbers:\", doubled_numbers)")
print("# Output:")
print("Doubled numbers:", doubled_numbers)

# 10. Closures
# ------------------------------------
# - A closure is a function object that remembers values in enclosing scopes even if they are not present in memory anymore.
# - It's an inner function that remembers and has access to variables in the local scope in which it was created even after the outer function has finished executing.

print("\n# 10. Closures")
print("# ------------------------------------")
print("# - Inner function that remembers and accesses variables from its enclosing scope.")

def outer_function(msg):
    """Outer function that defines and returns an inner function (closure)."""
    message = msg # Variable in the enclosing scope

    def inner_function():
        """Inner function - this is a closure."""
        print(message) # Accessing 'message' from the enclosing scope

    return inner_function # Returning the inner function

# Creating a closure
closure_func = outer_function("Hello Closure")

# Calling the closure - it remembers 'message' from outer_function's scope
print("\n# Example - Closures")
print("# Outer function definition:")
print("def outer_function(msg):")
print("    message = msg")
print("    def inner_function():")
print("        print(message)")
print("    return inner_function")
print("# Creating and calling closure:")
print("closure_func = outer_function(\"Hello Closure\")")
print("closure_func()")
print("# Output:")
closure_func()

# 11. Recursion
# ------------------------------------
# - Recursion is a technique where a function calls itself directly or indirectly.
# - Recursive functions need a base case to stop the recursion and prevent infinite loops.

print("\n# 11. Recursion")
print("# ------------------------------------")
print("# - Function calls itself to solve smaller instances of the same problem.")
print("# - Requires a base case to prevent infinite recursion.")

def factorial_recursive(n):
    """This function calculates factorial of a number using recursion."""
    if n == 0: # Base case: factorial of 0 is 1
        return 1
    else:
        return n * factorial_recursive(n-1) # Recursive call

# Calculating factorial using recursion
factorial_5 = factorial_recursive(5)
print("\n# Example - Recursion")
print("# Recursive function definition:")
print("def factorial_recursive(n):")
print("    if n == 0:")
print("        return 1")
print("    else:")
print("        return n * factorial_recursive(n-1)")
print("# Function call:")
print("factorial_5 = factorial_recursive(5)")
print("print(\"Factorial of 5:\", factorial_5)")
print("# Output:")
print("Factorial of 5:", factorial_5)

# 12. Function Annotations (Type Hinting)
# ------------------------------------
# - Function annotations are hints about the types of function arguments and return values.
# - They are for documentation and static analysis purposes; Python itself does not enforce type checking at runtime based on annotations.
# - Syntax: `def func(param: type) -> return_type:`

print("\n# 12. Function Annotations (Type Hinting)")
print("# ------------------------------------")
print("# - Hints for argument and return types, for documentation and static analysis.")
print("# - Syntax: def func(param: type) -> return_type:")

def greet_annotated(name: str) -> str:
    """Function with type annotations for parameter and return value."""
    return f"Greetings, {name}!"

# Calling the annotated function
greeting_message = greet_annotated("TypeHintUser")
print("\n# Example - Function Annotations (Type Hinting)")
print("# Annotated function definition:")
print("def greet_annotated(name: str) -> str:")
print("    return f\"Greetings, {name}!\"")
print("# Function call:")
print("greeting_message = greet_annotated(\"TypeHintUser\")")
print("print(\"Greeting:\", greeting_message)")
print("# Output:")
print("Greeting:", greeting_message)

# 15. Partial Functions (from functools)
# ------------------------------------
# - Partial functions allow you to derive a new function from an existing one by fixing some of its arguments.
# - It's useful when you have a function that takes multiple arguments, but you want to use it in a context that expects a function with fewer arguments (with some arguments pre-filled).
# - `functools.partial` is used to create partial functions.

print("\n# 15. Partial Functions (from functools)")
print("# ------------------------------------")
print("# - Creates a new function with some arguments of an existing function pre-filled.")
print("# - Useful for adapting functions to specific contexts.")
print("# - functools.partial")

from functools import partial

def multiply(x, y):
    """Simple function to multiply two numbers."""
    return x * y

# Create a partial function that multiplies by 2
double = partial(multiply, 2) # Fixed x=2, y is still to be provided

# Using the partial function
result_double_5 = double(5) # Only need to provide the 'y' argument (which is the second parameter of 'multiply')
print("\n# Example - Partial Functions")
print("# Original function:")
print("def multiply(x, y):")
print("    return x * y")
print("# Creating partial function:")
print("double = partial(multiply, 2)")
print("# Calling partial function:")
print("result_double_5 = double(5)")
print("print(\"Double of 5:\", result_double_5)")
print("# Output:")
print("Double of 5:", result_double_5)

# 16. Function Objects (Functions as First-Class Citizens)
# ------------------------------------
# - In Python, functions are first-class citizens, meaning they can be treated like any other object:
#   - Assigned to variables.
#   - Stored in data structures (like lists or dictionaries).
#   - Passed as arguments to other functions.
#   - Returned as values from other functions.

print("\n# 16. Function Objects (Functions as First-Class Citizens)")
print("# ------------------------------------")
print("# - Functions can be treated like any other object in Python.")
print("# - Can be assigned to variables, stored in structures, passed as arguments, returned from functions.")

def apply_operation(operation, a, b):
    """Applies a given operation (function) to two numbers."""
    return operation(a, b)

def addition(x, y):
    return x + y

def subtraction(x, y):
    return x - y

# Assigning functions to variables
add_func = addition
subtract_func = subtraction

# Passing functions as arguments to another function
sum_result_func_obj = apply_operation(add_func, 10, 5) # Passing 'add_func' (which is 'addition')
diff_result_func_obj = apply_operation(subtract_func, 10, 5) # Passing 'subtract_func' (which is 'subtraction')

print("\n# Example - Function Objects")
print("# Function apply_operation (accepts function as argument):")
print("def apply_operation(operation, a, b):")
print("    return operation(a, b)")
print("# Example functions:")
print("def addition(x, y): return x + y")
print("def subtraction(x, y): return x - y")
print("# Assigning functions to variables:")
print("add_func = addition")
print("subtract_func = subtraction")
print("# Passing functions as arguments:")
print("sum_result_func_obj = apply_operation(add_func, 10, 5)")
print("diff_result_func_obj = apply_operation(subtract_func, 10, 5)")
print("print(\"Sum result (Function Object):\", sum_result_func_obj)")
print("print(\"Difference result (Function Object):\", diff_result_func_obj)")
print("# Output:")
print("Sum result (Function Object):", sum_result_func_obj)
print("Difference result (Function Object):", diff_result_func_obj)

# 17. Input Function
# ------------------------------------
# - `input()` function is used to get user input from the console.
# - It always returns the input as a string.

print("\n# 17. Input Function")
print("# ------------------------------------")
print("# - input() function gets user input from console.")
print("# - Returns input as a string.")

# Example of using input() function
# user_name = input("Enter your name: ") # Uncomment to take interactive input
# print(f"Hello, {user_name}! Welcome.") # Uncomment to use interactive input

print("\n# Example - Input Function")
print("# Example commented out for non-interactive execution:")
print("# user_name = input(\"Enter your name: \")")
print("# print(f\"Hello, {user_name}! Welcome.\")")
print("# To test, uncomment above lines and run.")
print("# (Example output would depend on user input)")
# Example for demonstration without interactive input:
print("# Non-interactive example output (if user entered 'TestUser'):")
print("# Hello, TestUser! Welcome.")

# 18. Output Function
# ------------------------------------
# - `print()` function is used to display output to the console.
# - It can take multiple arguments, which are converted to strings and displayed, separated by spaces by default.
# - `print()` is versatile and can output various types of data.

print("\n# 18. Output Function")
print("# ------------------------------------")
print("# - print() function displays output to console.")
print("# - Can output multiple arguments, various data types.")

# Examples of using print() function
print("\n# Example - Output Function")
print("# Examples of print() usage:")
print("print(\"Hello\", \"from\", \"print\") # Multiple arguments")
print("print(123) # Number argument")
print("print([1, 2, 3]) # List argument")
print("print({\"key\": \"value\"}) # Dictionary argument")
print("# Output:")
print("Hello", "from", "print") # Multiple arguments
print(123) # Number argument
print([1, 2, 3]) # List argument
print({"key": "value"}) # Dictionary argument

print("\n# End of Function Explanation")

def describe_pet(animal_type, pet_name):
    """
    A function that accepts keyword arguments to describe a pet.
    :param animal_type: str - The type of animal (e.g., 'dog', 'cat').
    :param pet_name: str - The name of the pet.
    """
    print(f"I have a {animal_type} named {pet_name}.")

# Using keyword arguments
describe_pet(animal_type="dog", pet_name="Rex")
describe_pet(pet_name="Whiskers", animal_type="cat")

# 19. The Mutable Default Argument Gotcha
# ------------------------------------
# - Default argument values are evaluated ONCE, when the `def` statement runs -
#   not on every call. A mutable default (list, dict, set) is shared across
#   all calls that don't pass their own argument.
# - This is one of the most common Python bugs for beginners and veterans alike.

print("\n# 19. The Mutable Default Argument Gotcha")
print("# ------------------------------------")
print("# - Default values are created ONCE at function definition time.")
print("# - A mutable default (list/dict/set) is shared across calls - it persists!")

# The buggy version
def add_item_buggy(item, items=[]): # DANGER: same list reused every call!
    items.append(item)
    return items

print("\n# Example - The Bug:")
print("def add_item_buggy(item, items=[]):")
print("    items.append(item)")
print("    return items")

first_call = add_item_buggy("apple")
second_call = add_item_buggy("banana") # 'items' still has 'apple' from before!
print("# Output:")
print("first_call = add_item_buggy(\"apple\") ->", first_call)
print("second_call = add_item_buggy(\"banana\") ->", second_call, "(bug: 'apple' leaked in!)")

# The fix: use None as sentinel, create a fresh list inside the function
def add_item_fixed(item, items=None):
    if items is None:
        items = [] # fresh list every call with no argument
    items.append(item)
    return items

print("\n# Example - The Fix:")
print("def add_item_fixed(item, items=None):")
print("    if items is None:")
print("        items = []")
print("    items.append(item)")
print("    return items")

first_fixed = add_item_fixed("apple")
second_fixed = add_item_fixed("banana")
print("# Output:")
print("first_fixed = add_item_fixed(\"apple\") ->", first_fixed)
print("second_fixed = add_item_fixed(\"banana\") ->", second_fixed, "(no leak)")

# 20. nonlocal vs global in Nested Functions
# ------------------------------------
# - `global`: rebinds a name in the module's global scope from inside a function.
# - `nonlocal`: rebinds a name in the nearest enclosing function scope (not global),
#   used inside nested functions to modify a variable from the outer function.
# - Without either keyword, assignment inside a function creates a new LOCAL
#   variable instead of modifying the outer one.

print("\n# 20. nonlocal vs global in Nested Functions")
print("# ------------------------------------")
print("# - global: rebind a name in module scope.")
print("# - nonlocal: rebind a name in the nearest enclosing (non-global) function scope.")
print("# - Without either, assignment creates a new local variable, shadowing the outer one.")

counter = 0 # module-level (global) variable

def increment_global():
    global counter
    counter += 1 # rebinds the module-level 'counter'

def make_counter():
    count = 0 # enclosing scope variable
    def increment_local():
        nonlocal count
        count += 1 # rebinds 'count' in make_counter's scope, not global
        return count
    return increment_local

print("\n# Example - global:")
print("def increment_global():")
print("    global counter")
print("    counter += 1")
increment_global()
increment_global()
print("# Output: counter after two calls ->", counter)

print("\n# Example - nonlocal:")
print("def make_counter():")
print("    count = 0")
print("    def increment_local():")
print("        nonlocal count")
print("        count += 1")
print("        return count")
print("    return increment_local")
tick = make_counter()
print("# Output: tick() ->", tick())
print("# Output: tick() ->", tick())
print("# Output: tick() ->", tick(), "(each make_counter() call gets its own 'count')")

# 21. Recursion Depth Limit
# ------------------------------------
# - Python doesn't do tail-call optimization; each recursive call adds a new
#   frame to the call stack, bounded by sys.getrecursionlimit() (default 1000).
# - Exceeding it raises RecursionError, which is a subclass of RuntimeError.

print("\n# 21. Recursion Depth Limit")
print("# ------------------------------------")
print("# - sys.getrecursionlimit() reports the max stack depth (default 1000).")
print("# - Going past it raises RecursionError (no tail-call optimization in CPython).")

import sys

def count_down_forever(n):
    return count_down_forever(n + 1) # never terminates - will blow the stack

print("\n# Example - Recursion Depth Limit:")
print("print(\"sys.getrecursionlimit():\", sys.getrecursionlimit())")
print("sys.getrecursionlimit():", sys.getrecursionlimit())

print("# Output:")
try:
    count_down_forever(0)
except RecursionError as e:
    print("Caught RecursionError:", e)

# 22. Memoization - Manually and with functools.cache
# ------------------------------------
# - Memoization caches a function's results by its arguments, so repeated
#   calls with the same inputs skip re-computation.
# - Can be done manually with a dict, or automatically with functools.cache
#   (or functools.lru_cache for a bounded cache with an eviction policy).

print("\n# 22. Memoization - Manual and via functools.cache")
print("# ------------------------------------")
print("# - Caches results keyed by arguments; repeated calls are instant lookups.")
print("# - Manual: a dict. Automatic: @functools.cache / @functools.lru_cache.")

# Manual memoization
fib_cache = {}
def fib_manual(n):
    if n in fib_cache:
        return fib_cache[n]
    if n <= 1:
        result = n
    else:
        result = fib_manual(n - 1) + fib_manual(n - 2)
    fib_cache[n] = result
    return result

print("\n# Example - Manual Memoization:")
print("fib_cache = {}")
print("def fib_manual(n):")
print("    if n in fib_cache: return fib_cache[n]")
print("    result = n if n <= 1 else fib_manual(n-1) + fib_manual(n-2)")
print("    fib_cache[n] = result")
print("    return result")
print("# Output: fib_manual(30) ->", fib_manual(30))

# Automatic memoization with functools.cache (Python 3.9+)
from functools import cache

@cache
def fib_cached(n):
    if n <= 1:
        return n
    return fib_cached(n - 1) + fib_cached(n - 2)

print("\n# Example - functools.cache:")
print("from functools import cache")
print("@cache")
print("def fib_cached(n):")
print("    if n <= 1: return n")
print("    return fib_cached(n-1) + fib_cached(n-2)")
print("# Output: fib_cached(30) ->", fib_cached(30))
print("# Output: fib_cached.cache_info() ->", fib_cached.cache_info())

# 23. Keyword-Only and Positional-Only Arguments
# ------------------------------------
# - A bare `*` in the parameter list marks everything after it as keyword-only -
#   it must be passed by name, never positionally.
# - A `/` marks everything before it as positional-only - it must be passed
#   positionally, never by name. (Python 3.8+)
# - Useful for API design: lock down how a function may be called.

print("\n# 23. Keyword-Only and Positional-Only Arguments")
print("# ------------------------------------")
print("# - def f(*, x): x must be passed as a keyword argument.")
print("# - def f(x, /, y): x must be positional, y can be either.")

def create_user(*, name, age): # both name and age are keyword-only
    return f"{name}, {age}"

def divide(x, y, /): # both x and y are positional-only
    return x / y

print("\n# Example - Keyword-Only:")
print("def create_user(*, name, age):")
print("    return f\"{name}, {age}\"")
print("# Output: create_user(name=\"Alice\", age=30) ->", create_user(name="Alice", age=30))
try:
    create_user("Alice", 30) # positional call fails - name/age are keyword-only
except TypeError as e:
    print("create_user(\"Alice\", 30) raises TypeError:", e)

print("\n# Example - Positional-Only:")
print("def divide(x, y, /):")
print("    return x / y")
print("# Output: divide(10, 2) ->", divide(10, 2))
try:
    divide(x=10, y=2) # keyword call fails - x/y are positional-only
except TypeError as e:
    print("divide(x=10, y=2) raises TypeError:", e)

# 24. Function Introspection
# ------------------------------------
# - Functions are objects, so their metadata can be inspected at runtime:
#   `__defaults__` holds default argument values, `__name__` the function name,
#   and `inspect.signature()` gives a full, readable picture of the signature.

print("\n# 24. Function Introspection")
print("# ------------------------------------")
print("# - func.__defaults__: tuple of default values for positional args.")
print("# - inspect.signature(func): full signature, including annotations, defaults, kinds.")

import inspect

def sample_func(a, b=10, *args, c, d=20, **kwargs) -> str:
    return "sample"

print("\n# Example - Function Introspection:")
print("def sample_func(a, b=10, *args, c, d=20, **kwargs) -> str: ...")
print("# Output: sample_func.__defaults__ ->", sample_func.__defaults__)
print("# Output: sample_func.__name__ ->", sample_func.__name__)
print("# Output: inspect.signature(sample_func) ->", inspect.signature(sample_func))
for param_name, param in inspect.signature(sample_func).parameters.items():
    print(f"#   {param_name}: kind={param.kind}, default={param.default}")

