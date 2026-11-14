# 01. Python Control Flow
# 02. If-Elif-Else Clause
# 03. For Loop
# 04. While Loop
# 05. Break, Continue

# 01. Python Control Flow
# ------------------------------------
# - Control flow is the order in which statements or blocks of code are executed at runtime.
# - It determines the path of execution in a program based on conditions, loops, and function calls.
# - Control flow structures allow for decision making and repetition in programs, making them dynamic and versatile.
# - Python supports sequential, conditional (branching), and iterative (looping) control flow structures.

print("# 01. Python Control Flow")
print("# ------------------------------------")
print("# - Order of execution of code statements.")
print("# - Determines program's execution path based on conditions and loops.")
print("# - Enables decision making and repetition.")
print("# - Python supports sequential, conditional, and iterative control flow.")

# 02. If-Elif-Else Clause
# ------------------------------------
# - `if`, `elif` (else if), and `else` are conditional statements used to execute different blocks of code based on whether certain conditions are true or false.
# - `if` statement: Executes a block of code if a condition is true.
# - `elif` statement (optional, can have multiple): Checks for an additional condition if the preceding `if` or `elif` conditions are false.
# - `else` statement (optional, can have at most one): Executes a block of code if all preceding `if` and `elif` conditions are false.

print("\n# 02. If-Elif-Else Clause")
print("# ------------------------------------")
print("# - Conditional statements for executing code based on conditions.")
print("# - 'if': Execute if condition is true.")
print("# - 'elif': (optional) Check another condition if previous 'if' or 'elif' is false.")
print("# - 'else': (optional) Execute if all 'if' and 'elif' conditions are false.")

# Example of If-Elif-Else Clause
print("\n# Example - If-Elif-Else Clause:")
print("number = 10")
print("if number > 0:")
print("    print(\"Number is positive\")")
print("elif number == 0:")
print("    print(\"Number is zero\")")
print("else:")
print("    print(\"Number is negative\")")

print("# Output:")
number = 10
if number > 0:
    print("Number is positive") # Condition is true, this block executes
elif number == 0:
    print("Number is zero")
else:
    print("Number is negative")

number = 0
print("\nnumber = 0")
print("if number > 0:")
print("    print(\"Number is positive\")")
print("elif number == 0:")
print("    print(\"Number is zero\")")
print("else:")
print("    print(\"Number is negative\")")
print("# Output:")
if number > 0:
    print("Number is positive")
elif number == 0:
    print("Number is zero") # This condition is true, this block executes
else:
    print("Number is negative")

number = -5
print("\nnumber = -5")
print("if number > 0:")
print("    print(\"Number is positive\")")
print("elif number == 0:")
print("    print(\"Number is zero\")")
print("else:")
print("    print(\"Number is negative\")")
print("# Output:")
if number > 0:
    print("Number is positive")
elif number == 0:
    print("Number is zero")
else:
    print("Number is negative") # All conditions above are false, else block executes

# 03. For Loop
# ------------------------------------
# - `for` loop is used for iterating over a sequence (like a list, tuple, string, or range) or other iterable objects.
# - It executes a block of code for each item in the sequence.
# - Useful for automating repetitive tasks on a collection of items.
# - Can be used with `else` clause which executes after the loop completes normally (i.e., not terminated by `break`).

print("\n# 03. For Loop")
print("# ------------------------------------")
print("# - Iterates over a sequence (list, tuple, string, range) or iterable.")
print("# - Executes a block of code for each item in the sequence.")
print("# - Used for repetitive tasks on collections.")
print("# - Optional 'else' clause executes after loop completion (if not broken).")

# Example of For Loop
print("\n# Example - For Loop:")
print("fruits = [\"apple\", \"banana\", \"cherry\"]")
print("for fruit in fruits:")
print("    print(\"Fruit:\", fruit)")

print("# Output:")
fruits = ["apple", "banana", "cherry"]
for fruit in fruits:
    print("Fruit:", fruit) # This block executes for each item in fruits

print("\n# Example - For Loop with range():")
print("for i in range(3):")
print("    print(\"Number:\", i)")

print("# Output:")
for i in range(3):
    print("Number:", i) # This block executes for each number in the range 0 to 2

print("\n# Example - For Loop with string:")
print("for char in \"Python\":")
print("    print(\"Character:\", char)")

print("# Output:")
for char in "Python":
    print("Character:", char) # This block executes for each character in "Python"

print("\n# Example - For Loop with else clause:")
print("for i in range(3):")
print("    print(\"Looping, i:\", i)")
print("else:")
print("    print(\"Loop finished without break\")")

print("# Output:")
for i in range(3):
    print("Looping, i:", i) # Loop iterates through 0, 1, 2
else:
    print("Loop finished without break") # Else block executes after loop completes

print("\n# Example - For Loop with break (else clause not executed):")
print("for i in range(5):")
print("    if i == 3:")
print("        break")
print("    print(\"Looping, i:\", i)")
print("else:")
print("    print(\"Loop finished without break (this won't print)\")")

print("# Output:")
for i in range(5):
    if i == 3:
        break # Loop breaks when i is 3
    print("Looping, i:", i)
else:
    print("Loop finished without break (this won't print)") # Else block is skipped because loop was broken

# 04. While Loop
# ------------------------------------
# - `while` loop is used to repeatedly execute a block of code as long as a condition is true.
# - The condition is checked at the start of each iteration.
# - It is essential to ensure that the condition eventually becomes false to avoid infinite loops.
# - Can be used with `else` clause which executes when the condition becomes false and the loop terminates normally (not by `break`).

print("\n# 04. While Loop")
print("# ------------------------------------")
print("# - Repeatedly executes a block of code as long as a condition is true.")
print("# - Condition is checked at the beginning of each iteration.")
print("# - Important to have a condition that eventually becomes false to avoid infinite loop.")
print("# - Optional 'else' clause executes when condition becomes false (if not broken).")

# Example of While Loop
print("\n# Example - While Loop:")
print("count = 0")
print("while count < 3:")
print("    print(\"Count is:\", count)")
print("    count += 1")

print("# Output:")
count = 0
while count < 3:
    print("Count is:", count) # This block executes as long as count < 3
    count += 1

print("\n# Example - While Loop with else clause:")
print("count = 0")
print("while count < 3:")
print("    print(\"Count is:\", count)")
print("    count += 1")
print("else:")
print("    print(\"While loop condition is no longer true\")")

print("# Output:")
count = 0
while count < 3:
    print("Count is:", count) # Loop continues as long as count < 3
    count += 1
else:
    print("While loop condition is no longer true") # Else block executes when condition becomes false

print("\n# Example - While Loop with break (else clause not executed):")
print("count = 0")
print("while count < 5:")
print("    if count == 3:")
print("        break")
print("    print(\"Count is:\", count)")
print("    count += 1")
print("else:")
print("    print(\"While loop condition is no longer true (this won't print)\")")

print("# Output:")
count = 0
while count < 5:
    if count == 3:
        break # Loop breaks when count is 3
    print("Count is:", count)
    count += 1
else:
    print("While loop condition is no longer true (this won't print)") # Else block skipped due to break

# 05. Break, Continue
# ------------------------------------
# - `break` and `continue` are statements that alter the flow of loops (both `for` and `while`).
# - `break` statement: Immediately terminates the loop and the program control flows to the statement immediately following the loop.
# - `continue` statement: Skips the rest of the current iteration of the loop and continues to the next iteration.

print("\n# 05. Break, Continue")
print("# ------------------------------------")
print("# - Statements to alter loop flow.")
print("# - 'break': Terminate the loop immediately.")
print("# - 'continue': Skip current iteration and proceed to the next iteration.")

# Example of Break Statement
print("\n# Example - Break Statement in For Loop:")
print("for i in range(5):")
print("    if i == 3:")
print("        break")
print("    print(\"i is:\", i)")
print("print(\"Loop exited due to break\")")

print("# Output:")
for i in range(5):
    if i == 3:
        break # Loop terminates when i is 3
    print("i is:", i)
print("Loop exited due to break") # Executed after loop is broken

# Example of Continue Statement
print("\n# Example - Continue Statement in For Loop:")
print("for i in range(5):")
print("    if i == 2:")
print("        continue")
print("    print(\"i is:\", i)")
print("print(\"Loop finished\")")

print("# Output:")
for i in range(5):
    if i == 2:
        continue # Skips printing when i is 2, goes to next iteration
    print("i is:", i)
print("Loop finished") # Loop completes all iterations (except skipped ones)

# Example Break in While Loop
print("\n# Example - Break Statement in While Loop:")
print("number = 0")
print("while True:") # Intentionally infinite loop condition
print("    number += 1")
print("    print(\"Number:\", number)")
print("    if number >= 3:")
print("        break")
print("print(\"While loop broken\")")

print("# Output:")
number = 0
while True: # Intentionally infinite loop condition
    number += 1
    print("Number:", number)
    if number >= 3:
        break # Breaks out of infinite loop when number is 3 or more
print("While loop broken") # Executed after while loop is broken

# 06. match-case - Structural Pattern Matching (Python 3.10+)
# ------------------------------------
# - Like a more powerful switch statement: matches VALUES and STRUCTURE
#   (unpacks tuples/lists/dicts, binds variables, supports guards).
print("\n# 06. match-case - Structural Pattern Matching")

def http_status_message(code):
    match code:
        case 200:
            return "OK"
        case 404:
            return "Not Found"
        case 500 | 502 | 503:  # | matches any of several literal values
            return "Server Error"
        case _:  # wildcard - matches anything else, like `default`
            return "Unknown Status"

for status in [200, 404, 502, 999]:
    print(status, "->", http_status_message(status))

def describe_point(point):
    match point:
        case (0, 0):
            return "Origin"
        case (x, 0):  # binds x, matches any point on the x-axis
            return f"On x-axis at x={x}"
        case (0, y):
            return f"On y-axis at y={y}"
        case (x, y) if x == y:  # guard clause - extra condition
            return f"On diagonal at ({x}, {y})"
        case (x, y):
            return f"Point at ({x}, {y})"
        case _:
            return "Not a point"

for pt in [(0, 0), (5, 0), (0, 3), (2, 2), (1, 4)]:
    print(pt, "->", describe_point(pt))

def describe_command(command):
    match command.split():
        case ["go", direction]:  # unpacks a list of a specific length
            return f"Moving {direction}"
        case ["go", *rest]:  # * captures remaining items
            return f"Invalid direction(s): {rest}"
        case []:
            return "Empty command"
        case _:
            return "Unrecognized command"

for cmd in ["go north", "go up down", ""]:
    print(repr(cmd), "->", describe_command(cmd))

# 07. Breaking Out of Nested Loops
# ------------------------------------
# - Python has no `break 2` / labeled loops like some other languages.
# - Common workarounds:
#   1. A flag variable checked by the outer loop.
#   2. Wrap the loops in a function and `return` (cleanest, most common).
#   3. itertools.product() to flatten nested iteration into a single loop.

print("\n# 07. Breaking Out of Nested Loops")
print("# ------------------------------------")

# a) Flag variable
print("\na) Flag variable:")
found = False
for i in range(3):
    for j in range(3):
        if i == 1 and j == 1:
            found = True
            break   # only breaks the inner loop
        print(f"   checking ({i}, {j})")
    if found:        # outer loop checks the flag to break too
        break
print("   stopped at i=1, j=1 using a flag")

# b) Function + return - the cleanest workaround
print("\nb) Function + return:")
def find_pair(target_i, target_j):
    for i in range(3):
        for j in range(3):
            if i == target_i and j == target_j:
                return (i, j)   # exits BOTH loops immediately
    return None

print("   find_pair(1, 1) ->", find_pair(1, 1))

# c) itertools.product() - flattens nested loops into one
print("\nc) itertools.product():")
import itertools
for i, j in itertools.product(range(3), range(3)):
    if i == 1 and j == 1:
        print(f"   found ({i}, {j}) with a single loop, breaking")
        break

# 08. Ternary (Conditional) Expression Chaining
# ------------------------------------
# - The ternary form `value_if_true if condition else value_if_false` can be
#   chained to emulate an if/elif/elif/.../else ladder in one expression.
# - Readable for 2-3 branches; prefer a normal if/elif chain beyond that.

print("\n# 08. Ternary Expression Chaining")
print("# ------------------------------------")

for score in [95, 82, 71, 50]:
    grade = "A" if score >= 90 else "B" if score >= 80 else "C" if score >= 70 else "F"
    print(f"   score={score} -> grade={grade}")

# 09. any() and all() - Short-Circuit Behavior
# ------------------------------------
# - any(iterable): True if AT LEAST ONE element is truthy. Stops at the
#   first truthy value (short-circuits).
# - all(iterable): True only if EVERY element is truthy. Stops at the
#   first falsy value (short-circuits).
# - Both work lazily with generator expressions, so they avoid computing
#   items past the point the answer is already decided.

print("\n# 09. any() and all() - Short-Circuit Behavior")
print("# ------------------------------------")

numbers = [2, 4, 6, 7, 8]

def is_even_noisy(n):
    print(f"   checking {n}")
    return n % 2 == 0

print("any(even) - stops once it finds one:")
print("  result:", any(is_even_noisy(n) for n in numbers))   # stops at 2

print("\nall(even) - stops at the first odd number:")
print("  result:", all(is_even_noisy(n) for n in numbers))   # stops at 7

# 10. zip() with strict= (Python 3.10+)
# ------------------------------------
# - By default zip() silently stops at the shortest iterable - this can
#   hide bugs when lists are accidentally mismatched in length.
# - strict=True raises a ValueError if the iterables aren't the same length.

print("\n# 10. zip() with strict= (Python 3.10+)")
print("# ------------------------------------")

names = ["Alice", "Bob", "Charlie"]
ages = [25, 30]   # one short - a likely bug

print("Default zip() silently truncates:")
for name, age in zip(names, ages):
    print(f"   {name}: {age}")

print("\nzip(..., strict=True) catches the mismatch instead:")
try:
    list(zip(names, ages, strict=True))
except ValueError as e:
    print("   ValueError:", e)

# 11. range() is Lazy vs list(range())
# ------------------------------------
# - range() returns a lightweight lazy sequence object - it computes values
#   on demand and takes constant memory regardless of size.
# - list(range()) eagerly materializes every value into memory upfront.
# - For simple iteration, prefer range() directly - never wrap it in list()
#   just to loop over it.

print("\n# 11. range() is Lazy vs list(range())")
print("# ------------------------------------")

import sys
lazy_range = range(1_000_000)
eager_list = list(range(1_000_000))
print("sys.getsizeof(range(1_000_000)) :", sys.getsizeof(lazy_range), "bytes (constant, no matter the size)")
print("sys.getsizeof(list(range(...))) :", sys.getsizeof(eager_list), "bytes (grows with size)")
print("# Use range() directly in loops; only build list(range()) if you need")
print("# actual list operations (indexing repeatedly, slicing, mutating).")

print("\n# End of Control Flow Explanation")

