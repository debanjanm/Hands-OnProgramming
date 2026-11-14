# <!-- # 01. Python Introduction
# # 02. Why Python
# # 03. Syntax
# # 04. Indentation
# # 05. Comments
# # 06. Data Types
# # 07. Variables
# # 08. Memory Management
# # 09. Literals
# # 10. Operators
# # 11. Expressions -->

# Python Fundamentals Explanation

# 1. Python Introduction
# ------------------------------------
# - Python is a high-level, interpreted, general-purpose programming language.
# - Created by Guido van Rossum and first released in 1991.
# - Design philosophy emphasizes code readability with significant use of whitespace.
# - Supports multiple programming paradigms, including structured (procedural), object-oriented, and functional programming.
# - Known for its large standard library, dynamically typed nature, and automatic memory management.

print("# 1. Python Introduction")
print("# ------------------------------------")
print("# - High-level, interpreted, general-purpose.")
print("# - Emphasizes readability, supports multiple programming paradigms.")
print("# - Large standard library, dynamically typed, automatic memory management.")

# 2. Why Python
# ------------------------------------
# - Beginner-Friendly: Simple syntax, easy to learn and read, great for newcomers to programming.
# - Versatile: Used in web development (Django, Flask), data science (Pandas, NumPy, SciPy), machine learning (TensorFlow, PyTorch), scripting, automation, and more.
# - Large Community and Ecosystem: Extensive libraries, frameworks, and a supportive community for learning and problem-solving.
# - Cross-Platform: Runs on Windows, macOS, Linux, and other platforms.
# - Rapid Development: Python's clear syntax and vast libraries allow for faster development times.
# - High Demand in Industry: Widely used in various industries, leading to ample job opportunities.

print("\n# 2. Why Python")
print("# ------------------------------------")
print("# - Beginner-Friendly, Versatile, Large Community, Cross-Platform, Rapid Development, High Demand.")
print("# - Used for: Web Dev, Data Science, ML/AI, Scripting, Automation, etc.")

# 3. Syntax
# ------------------------------------
# - Python's syntax is designed to be clean and readable.
# - Uses English keywords and mathematical notations, making it intuitive.
# - Relies heavily on indentation to define code blocks (unlike curly braces in languages like C++ or Java).
# - Dynamically typed, meaning you don't need to declare the type of a variable explicitly.
# - Case-sensitive language (variable 'name' is different from 'Name').

print("\n# 3. Syntax")
print("# ------------------------------------")
print("# - Clean and readable, uses English keywords.")
print("# - Indentation for code blocks, dynamically typed, case-sensitive.")

print("\n# Example of Python Syntax (simple print statement):")
print("print('Hello, Python!')") # Simple print statement
print("# Output:")
print("Hello, Python!")

# 4. Indentation
# ------------------------------------
# - Indentation is crucial in Python. It's used to define blocks of code, such as in loops, conditional statements, and functions.
# - Consistent indentation (usually 4 spaces or a tab) is mandatory; incorrect indentation will lead to errors.
# - Encourages clean, structured, and readable code.

print("\n# 4. Indentation")
print("# ------------------------------------")
print("# - Defines code blocks (loops, conditionals, functions).")
print("# - Consistent indentation (4 spaces or tab) is MANDATORY.")
print("# - Promotes clean and readable code.")

print("\n# Example of Indentation (if statement):")
number = 10
if number > 0: # Indentation starts here for the block of code inside 'if'
    print("Number is positive") # This line is indented, part of the 'if' block
else:
    print("Number is not positive") # This line would be indented if 'else' block had content
print("# Output:")
if number > 0:
    print("Number is positive")
else:
    print("Number is not positive")

# 5. Comments
# ------------------------------------
# - Comments are used to add explanatory notes to your code, making it more understandable.
# - Python supports two types of comments:
#   - Single-line comments: Start with a hash symbol `#` and continue to the end of the line.
#   - Multi-line comments (Docstrings): Enclosed in triple quotes `'''Docstring'''` or `"""Docstring"""`. Used for function/class/module documentation.
# - Comments are ignored by the Python interpreter.

print("\n# 5. Comments")
print("# ------------------------------------")
print("# - Explanatory notes in code, ignored by interpreter.")
print("# - Single-line comments: start with #")
print("# - Multi-line comments (Docstrings): ''' or \"\"\"")

print("\n# Example of Comments:")
print("# This is a single-line comment") # This is a single-line comment
print("print('Hello') # This is a comment after code")
print('''\n"""This is a
multi-line comment
using triple quotes (Docstring).
"""''') # Multi-line comment using triple quotes (Docstring)
print("# Output (only 'Hello' is printed):")
print("Hello")

# 6. Data Types
# ------------------------------------
# - Data types classify the kind of value a variable holds. Python has several built-in data types:
#   - Numeric Types: int (integers), float (floating-point numbers), complex (complex numbers).
#   - Text Type: str (strings).
#   - Sequence Types: list, tuple, range.
#   - Mapping Type: dict (dictionary).
#   - Set Types: set, frozenset.
#   - Boolean Type: bool (True, False).
#   - Binary Types: bytes, bytearray, memoryview.
# - Python is dynamically typed, so you don't need to explicitly declare data types when you define variables.

print("\n# 6. Data Types")
print("# ------------------------------------")
print("# - Classify the kind of value a variable holds.")
print("# - Built-in types: Numeric (int, float, complex), Text (str), Sequence (list, tuple, range),")
print("#   Mapping (dict), Set (set, frozenset), Boolean (bool), Binary (bytes, bytearray, memoryview).")
print("# - Dynamically typed - no explicit type declaration needed.")

print("\n# Example of Data Types:")
integer_example = 10
float_example = 10.5
string_example = "Hello"
list_example = [1, 2, 3]
tuple_example = (1, 2, 3)
dict_example = {"a": 1, "b": 2}
bool_example = True

print(f"Integer: {integer_example}, Type: {type(integer_example)}")
print(f"Float: {float_example}, Type: {type(float_example)}")
print(f"String: {string_example}, Type: {type(string_example)}")
print(f"List: {list_example}, Type: {type(list_example)}")
print(f"Tuple: {tuple_example}, Type: {type(tuple_example)}")
print(f"Dictionary: {dict_example}, Type: {type(dict_example)}")
print(f"Boolean: {bool_example}, Type: {type(bool_example)}")

# 7. Variables
# ------------------------------------
# - Variables are containers for storing data values.
# - In Python, variables are created when you first assign a value to them.
# - Variable names must follow certain rules (e.g., start with a letter or underscore, can contain alphanumeric characters and underscores).
# - You don't need to declare the data type of a variable explicitly; Python automatically infers the type based on the assigned value (dynamic typing).

print("\n# 7. Variables")
print("# ------------------------------------")
print("# - Containers for storing data values.")
print("# - Created upon first assignment, dynamically typed.")
print("# - Variable naming rules: start with letter/underscore, alphanumeric and underscore chars allowed.")

print("\n# Example of Variables:")
variable_name = "Python" # Variable 'variable_name' is created and assigned a string value
variable_number = 100   # Variable 'variable_number' is assigned an integer value
_variable_start_underscore = "underscore_start" # Valid variable name starting with underscore

print(f"Variable name: {variable_name}, Value: {variable_name}, Type: {type(variable_name)}")
print(f"Variable number: {variable_number}, Value: {variable_number}, Type: {type(variable_number)}")
print(f"Variable underscore: {_variable_start_underscore}, Value: {_variable_start_underscore}, Type: {type(_variable_start_underscore)}")

# 8. Memory Management
# ------------------------------------
# - Python uses automatic memory management, primarily through garbage collection.
# - Memory is allocated dynamically when objects are created.
# - Python's garbage collector automatically reclaims memory that is no longer in use (when objects are no longer referenced).
# - This simplifies memory management for the programmer compared to languages like C or C++ where manual memory management is required.
# - Python's memory management is mostly handled in the background, making development more efficient and reducing memory leaks.

print("\n# 8. Memory Management")
print("# ------------------------------------")
print("# - Automatic memory management through Garbage Collection.")
print("# - Memory allocated dynamically when objects are created.")
print("# - Garbage collector reclaims unused memory automatically.")
print("# - Simplifies memory management for developers, reduces memory leaks.")
print("# - Mostly handled in the background.")

# 9. Literals
# ------------------------------------
# - Literals are raw values in a program. In Python, there are various types of literals:
#   - String Literals: Text enclosed in quotes (single, double, triple). e.g., "Hello", 'World', '''Multi-line'''
#   - Numeric Literals: Integer, float, complex numbers. e.g., 10, 3.14, 2+3j
#   - Boolean Literals: `True` or `False`.
#   - Special Literals: `None` - represents absence of a value or null value.

print("\n# 9. Literals")
print("# ------------------------------------")
print("# - Raw values in a program.")
print("# - Types of Literals:")
print("#   - String Literals: 'Hello', \"World\", '''Multi-line'''")
print("#   - Numeric Literals: 10, 3.14, 2+3j")
print("#   - Boolean Literals: True, False")
print("#   - Special Literals: None")

# Example of Literals:
print("\n# Example - Literals:")
string_literal = "Python Literal"
print("String Literal:", string_literal)
integer_literal = 100
print("Integer Literal:", integer_literal)
float_literal = 99.9
print("Float Literal:", float_literal)
complex_literal = 1j
print("Complex Literal:", complex_literal)
boolean_literal_true = True
print("Boolean True Literal:", boolean_literal_true)
boolean_literal_false = False
print("Boolean False Literal:", boolean_literal_false)
none_literal = None
print("None Literal:", none_literal)

# 10. Operators
# ------------------------------------
# - Operators are symbols that perform operations on variables and values (operands).
# - Python supports several types of operators:
#   - Arithmetic Operators: +, -, *, /, %, **, //
#   - Assignment Operators: =, +=, -=, *=, /=, %=, //=, **=, &=, |=, ^=, >>=, <<=
#   - Comparison Operators: ==, !=, >, <, >=, <=
#   - Logical Operators: and, or, not
#   - Identity Operators: is, is not
#   - Membership Operators: in, not in
#   - Bitwise Operators: &, |, ^, ~, <<, >>

print("\n# 10. Operators")
print("# ------------------------------------")
print("# - Symbols that perform operations on variables and values.")
print("# - Types of Operators:")
print("#   - Arithmetic Operators: +, -, *, /, %, **, //")
print("#   - Assignment Operators: =, +=, -=, ...")
print("#   - Comparison Operators: ==, !=, >, <, ...")
print("#   - Logical Operators: and, or, not")
print("#   - Identity Operators: is, is not")
print("#   - Membership Operators: in, not in")
print("#   - Bitwise Operators: &, |, ^, ~, <<, >>")

# Example of Operators:
print("\n# Example - Operators:")
a = 10
b = 5

print("\n# Arithmetic Operators:")
print("a + b =", a + b) # Addition
print("a - b =", a - b) # Subtraction
print("a * b =", a * b) # Multiplication
print("a / b =", a / b) # Division
print("a % b =", a % b) # Modulus (remainder)
print("a ** b =", a ** b) # Exponentiation (a to the power of b)
print("a // b =", a // b) # Floor division (integer division)

print("\n# Assignment Operators:")
c = a # Simple assignment
print("c = a, c =", c)
a += b # Add and assign (a = a + b)
print("a += b, a =", a)
a -= b # Subtract and assign (a = a - b)
print("a -= b, a =", a)

print("\n# Comparison Operators:")
print("a == b :", a == b) # Equal to
print("a != b :", a != b) # Not equal to
print("a > b  :", a > b)  # Greater than
print("a < b  :", a < b)  # Less than
print("a >= b :", a >= b) # Greater than or equal to
print("a <= b :", a <= b) # Less than or equal to

print("\n# Logical Operators:")
x = True
y = False
print("x and y:", x and y) # Logical AND
print("x or y :", x or y)  # Logical OR
print("not x  :", not x)  # Logical NOT

print("\n# Membership Operators:")
list_example = [1, 2, 3, 4, 5]
print("3 in list_example:", 3 in list_example) # Is 3 in list_example?
print("6 not in list_example:", 6 not in list_example) # Is 6 not in list_example?

# Operator Precedence in Python
print("\n# Operator Precedence:")
print("# ------------------------------------")
print("# - Order in which operations are performed in an expression.")
print("# - Python follows PEMDAS/BODMAS rule (Parentheses, Exponents, Multiplication and Division, Addition and Subtraction) with some additions.")
print("# - Higher precedence operators are evaluated before lower precedence ones.")
print("# - Use parentheses '()' to override precedence.")
print("# - Precedence (Highest to Lowest):")
print("#   1. Parentheses: ()")
print("#   2. Exponentiation: **")
print("#   3. Unary plus and minus: +, - (e.g., +3, -5)")
print("#   4. Multiplication, Division, Floor Division, Modulus: *, /, //, %")
print("#   5. Addition and Subtraction: +, -")
print("#   6. Comparison Operators: ==, !=, >, >=, <, <=")
print("#   7. Assignment Operators: =, +=, -=, ...")
print("#   8. Logical Operators: not, and, or")
print("#   9. Identity Operators: is, is not")
print("#   10. Membership Operators: in, not in")
print("#   11. Bitwise Operators: |, ^, &, <<, >>")

# 11. Expressions
# ------------------------------------
# - An expression is a combination of values, variables, operators, and function calls that the Python interpreter can evaluate to produce a value.
# - Expressions are used to perform calculations, make decisions, and manipulate data within a program.
# - Every expression in Python evaluates to some value.
# - Types of expressions include:
#   - Arithmetic Expressions: Perform numeric calculations. e.g., `2 + 3`, `x * 5`, `(a + b) / c`
#   - Comparison Expressions: Compare values and result in a boolean value (True or False). e.g., `a == b`, `x > 10`, `y <= z`
#   - Logical Expressions: Combine boolean values using logical operators (`and`, `or`, `not`). e.g., `x and y`, `not is_valid`, `a or b`
#   - Assignment Expressions: Assign values to variables (introduced in Python 3.8 using the walrus operator `:=`). e.g., `y := x + 1` (assigns `x + 1` to `y` and also returns the value)
#   - String Expressions: Operations involving strings, like concatenation or formatting. e.g., `"Hello" + " " + name`, `f"Age: {age}"`

print("\n# 11. Expressions")
print("# ------------------------------------")
print("# - Combination of values, variables, operators, function calls that Python evaluates.")
print("# - Used for calculations, decisions, data manipulation.")
print("# - Every expression evaluates to a value.")
print("# - Types of Expressions:")
print("#   - Arithmetic Expressions: 2 + 3, x * 5, (a + b) / c")
print("#   - Comparison Expressions: a == b, x > 10, y <= z")
print("#   - Logical Expressions: x and y, not is_valid, a or b")
print("#   - Assignment Expressions: (Python 3.8+) y := x + 1")
print("#   - String Expressions: \"Hello\" + \" \" + name, f\"Age: {age}\"")

# Example of Expressions:
print("\n# Example - Expressions:")

print("\n# Arithmetic Expressions:")
arithmetic_expression = 10 + 5 * 2 # Evaluates to 20 (operator precedence)
print("10 + 5 * 2 =", arithmetic_expression)

print("\n# Comparison Expressions:")
comparison_expression = (5 > 3) # Evaluates to True
print("5 > 3 is", comparison_expression)

print("\n# Logical Expressions:")
logical_expression = True and (10 < 20) # Evaluates to True
print("True and (10 < 20) is", logical_expression)

print("\n# Assignment Expression (Python 3.8+):")
number = 5
assignment_expression = number + 2 # Just an expression first
print("number + 2 =", assignment_expression)

print("\n# Walrus Operator := (Python 3.8+) - assign AND use a value in one expression:")
walrus_result = (y := number + 2) # assigns 7 to y, and the expression evaluates to 7 too
print("(y := number + 2) =", walrus_result, ", y =", y)

# Common use: avoid computing/calling something twice
data = [1, 2, 3, 4, 5, 6]
filtered = [half for n in data if (half := n / 2) > 1]  # reuse `half` without recomputing n / 2
print("walrus inside comprehension:", filtered)

count = 0
while (count := count + 1) <= 3:  # assign + test in the loop condition itself
    print("walrus in while condition, count =", count)

print("\n# String Expressions:")
name_val = "Alice"
string_expression = "Hello, " + name_val # String concatenation
print("\"Hello, \" + name_val =", string_expression)
formatted_string_expression = f"Value of number: {number}" # f-string formatting
print("f\"Value of number: {number}\" =", formatted_string_expression)

# 12. Identity vs Equality (is vs ==)
# ------------------------------------
# - `==` compares VALUES (calls __eq__). `is` compares IDENTITY - whether two
#   names point to the exact same object in memory.
# - `id(obj)` returns that object's unique memory identifier (CPython: its address).
# - Gotcha: CPython caches small integers (-5 to 256) and some strings
#   (interning), so `is` can appear to work for equality by accident on these
#   values, but it's an implementation detail - never rely on it.

print("\n# 12. Identity vs Equality (is vs ==)")
print("# ------------------------------------")

a = [1, 2, 3]
b = [1, 2, 3]
c = a
print("a == b :", a == b, "(same values)")
print("a is b :", a is b, "(different objects)")
print("a is c :", a is c, "(c was assigned = a, same object)")
print("id(a):", id(a), ", id(b):", id(b), ", id(c):", id(c))

# Small-int caching: CPython pre-allocates ints -5..256 and reuses them.
small_x = 100
small_y = 100
print("\n100 is 100 (in cached range -5..256):", small_x is small_y)

big_x = 1000
big_y = 1000
print("1000 is 1000 (outside cached range):", big_x is big_y, "(implementation detail, don't rely on it)")

# String interning: short/identifier-like string literals are often interned.
str_x = "hello"
str_y = "hello"
print("\n'hello' is 'hello' (interned literal):", str_x is str_y)

str_a = "hello world!"
str_b = "hello world!"
print("'hello world!' is 'hello world!' (may or may not be interned):", str_a is str_b)

print("\n# Rule of thumb: use '==' for value comparison, 'is' only for")
print("# identity checks like 'x is None', 'x is True', singleton sentinels.")

# 13. Chained Comparisons
# ------------------------------------
# - Python lets you chain comparisons: `a < b < c` means `a < b and b < c`,
#   with `b` evaluated only once (unlike most languages where it would be
#   parsed as `(a < b) < c`, comparing a bool to c).

print("\n# 13. Chained Comparisons")
print("# ------------------------------------")

value = 5
print("1 < value < 10 :", 1 < value < 10)
print("Equivalent to  :", 1 < value and value < 10)

# Tricky example combining precedence rules from section 10:
# ** binds tighter than unary -, comparisons chain, 'and'/'or' come last.
tricky = -2 ** 2 < 10 == 10.0 > 0
print("\n-2 ** 2 < 10 == 10.0 > 0 =", tricky)
print("# Step by step: -2 ** 2 = -(2**2) = -4")
print("#               -4 < 10  -> True")
print("#               10 == 10.0 -> True")
print("#               10.0 > 0 -> True")
print("#               all chained comparisons True -> True")

# 14. Short-Circuit Evaluation Internals
# ------------------------------------
# - `and` / `or` do NOT always return True/False - they return one of the
#   OPERANDS itself (whichever one decided the result), evaluating the
#   right-hand side only when needed ("short-circuiting").
# - `x and y`: if x is falsy, returns x without evaluating y; else returns y.
# - `x or y` : if x is truthy, returns x without evaluating y; else returns y.

print("\n# 14. Short-Circuit Evaluation Internals")
print("# ------------------------------------")

print("0 and 'never evaluated' =", 0 and "never evaluated")   # returns 0, right side skipped
print("'left' and 'right' =", "left" and "right")             # left truthy -> returns right
print("'' or 'fallback' =", "" or "fallback")                 # left falsy -> returns right
print("'value' or 'fallback' =", "value" or "fallback")       # left truthy -> returns left, short-circuits

def noisy(label, return_value):
    print(f"   noisy({label}) was called")
    return return_value

print("\nDemonstrating short-circuit skips the call entirely:")
result = noisy("A", False) and noisy("B", True)   # B's call never happens
print("result:", result)

result = noisy("C", True) or noisy("D", True)     # D's call never happens
print("result:", result)

# Common idiom relying on this: default values
config_value = None
effective_value = config_value or "default_setting"
print("\nconfig_value or 'default_setting' =", effective_value)

# 15. Numeric Precision: Integers vs Floats
# ------------------------------------
# - Python ints have arbitrary precision - they grow as large as memory
#   allows, with no overflow.
# - Floats are IEEE-754 double precision (64-bit) - finite precision, so
#   decimal fractions like 0.1 cannot be represented exactly in binary.
# - This is why `0.1 + 0.2 != 0.3` - it's a binary floating-point rounding
#   artifact, not a Python bug.

print("\n# 15. Numeric Precision: Integers vs Floats")
print("# ------------------------------------")

huge_int = 2 ** 200
print("2 ** 200 =", huge_int, "(exact, arbitrary precision)")

print("\n0.1 + 0.2 =", 0.1 + 0.2)
print("0.1 + 0.2 == 0.3 :", 0.1 + 0.2 == 0.3)
print("# Why: 0.1 and 0.2 have no exact binary floating-point representation,")
print("#      so tiny rounding errors accumulate.")

import math
print("\nUse math.isclose() for float comparisons instead of ==:")
print("math.isclose(0.1 + 0.2, 0.3) =", math.isclose(0.1 + 0.2, 0.3))

print("\n# End of Python Fundamentals Explanation")

