## 0. Characteristics of {String}
## 1. Creating {String}
## 2. Acessing {String}
## 3. Adding {String}
## 4. Editing {String}
## 5. Deleting {String}
## 6. Operations on {String}: arithmatic/relational operations/logical/membership/ loop
## 7. {String} Specific Methods: len/sum/min/max/sorted
## 8. Advancaed Topics: String Specific Functions

# Python String Explanation

# 0. Characteristics of String
# ------------------------------------
# - Strings are used to represent text data.
# - Strings are sequences of characters.
# - Strings are immutable (unchangeable). Once a string is created, its value cannot be altered.
# - Strings are ordered, meaning the characters have a defined order, and you can access them by their position (index).
# - Strings are indexed, starting from 0 for the first character.
# - Strings can be enclosed in single quotes (' '), double quotes (" "), or triple quotes (''' ''' or """ """). Triple quotes are used for multi-line strings.

print("\n# 0. Characteristics of String")
print("# ------------------------------------")
print("# - Sequences of characters, immutable, ordered, indexed.")

# 1. Creating String
# ------------------------------------
# - Strings can be created using single quotes, double quotes, or triple quotes.
# - The str() constructor can also be used to create strings from other data types.

print("\n# 1. Creating String")
print("# ------------------------------------")

# a) Single quotes
single_quoted_string = 'Hello'
print("a) Single quotes:", single_quoted_string, type(single_quoted_string))

# b) Double quotes
double_quoted_string = "World"
print("b) Double quotes:", double_quoted_string, type(double_quoted_string))

# c) Triple single quotes - for multi-line strings
triple_single_quoted_string = '''This is a
multi-line string
using triple single quotes.'''
print("c) Triple single quotes:\n", triple_single_quoted_string)

# d) Triple double quotes - also for multi-line strings
triple_double_quoted_string = """This is another
multi-line string
using triple double quotes."""
print("d) Triple double quotes:\n", triple_double_quoted_string)

# e) str() constructor - convert other types to string
number = 123
string_from_number = str(number)
print("e) str() constructor from number:", string_from_number, type(string_from_number))

boolean_value = True
string_from_boolean = str(boolean_value)
print("   str() constructor from boolean:", string_from_boolean, type(string_from_boolean))

# 2. Accessing String
# ------------------------------------
# - Characters in a string can be accessed by their index.
# - Indexing starts from 0.
# - Negative indexing can be used to access characters from the end of the string.
# - Slicing can be used to extract substrings.

print("\n# 2. Accessing String")
print("# ------------------------------------")

example_string = "PythonString"
print("Original String:", example_string)

# a) Accessing by index
first_char = example_string[0]
print("a) Accessing first character [0]:", first_char)

seventh_char = example_string[6]
print("   Accessing seventh character [6]:", seventh_char)

last_char = example_string[-1]
print("   Accessing last character [-1]:", last_char)

second_last_char = example_string[-2]
print("   Accessing second last character [-2]:", second_last_char)

# b) Slicing - extract substrings
substring_1_4 = example_string[1:5] # Characters from index 1 up to (but not including) 5
print("\nb) Slicing [1:5]:", substring_1_4)

substring_start_5 = example_string[5:] # Characters from index 5 to the end
print("   Slicing [5:]:", substring_start_5)

substring_start_end = example_string[:] # Copy of the entire string
print("   Slicing [:] (copy):", substring_start_end)

substring_step_2 = example_string[::2] # Every other character from the start
print("   Slicing [::2] (step of 2):", substring_step_2)

# 3. Adding String (Concatenation)
# ------------------------------------
# - Strings are immutable, so you cannot "add" to an existing string in place.
# - Instead, you can create a new string by concatenating existing strings using the + operator or the join() method.

print("\n# 3. Adding String (Concatenation)")
print("# ------------------------------------")

string1 = "Hello"
string2 = "World"
print("String 1:", string1)
print("String 2:", string2)

# a) Concatenation using + operator
concatenated_string = string1 + " " + string2 # Creating a new string
print("a) Concatenation using +:", concatenated_string)
print("   Original string1 remains unchanged:", string1)

# b) Concatenation using += operator (re-assignment, not in-place modification)
string1 += "!" # Re-assign string1 to a new string (string1 + "!")
print("b) Concatenation using +=:", string1) # string1 is now a new string
string1 = "Hello" # Reset string1 for further examples

# c) Using join() method - efficient for concatenating many strings from an iterable
words = ["This", "is", "a", "sentence."]
joined_string = " ".join(words) # " " is the separator, words is the iterable
print("\nc) Using join() method:", joined_string)

# 4. Editing String (Immutability)
# ------------------------------------
# - Strings are immutable, so you cannot change individual characters or substrings directly.
# - "Editing" a string means creating a new string that is based on the original with the desired modifications.
# - You can use slicing and concatenation to achieve the effect of editing, or string methods that return new strings.

print("\n# 4. Editing String (Immutability)")
print("# ------------------------------------")

original_string = "Hello, World!"
print("Original String:", original_string)

# a) Attempting to change a character directly will raise TypeError
# original_string[0] = 'J' # This will cause TypeError: 'str' object does not support item assignment

# b) 'Editing' by slicing and concatenation to replace a substring
modified_string_replace = original_string[:7] + "Python" + original_string[12:] # "Hello, " + "Python" + "!"
print("b) 'Editing' by slicing and concatenation:", modified_string_replace)
print("   Original string remains unchanged:", original_string)

# c) Using replace() method - returns a new string with replacements
modified_string_replace_method = original_string.replace("World", "Python")
print("c) Using replace() method:", modified_string_replace_method)
print("   Original string remains unchanged:", original_string)

# 5. Deleting String
# ------------------------------------
# - Strings are immutable, you cannot delete individual characters from a string.
# - You can delete an entire string variable using the 'del' keyword.

print("\n# 5. Deleting String")
print("# ------------------------------------")

string_to_delete = "StringToDel"
print("String before deletion:", string_to_delete)

# a) Attempting to delete a character by index will raise TypeError
# del string_to_delete[0] # This will cause TypeError: 'str' object doesn't support item deletion

# b) Deleting the entire string variable
del string_to_delete
# print("b) del string_to_delete: (string_to_delete no longer exists)")
# try:
#     print(string_to_delete) # This will cause NameError if string is deleted
# except NameError as e:
#     print("   Error:", e)

# For demonstration purposes, let's re-initialize a string for further examples
example_string = "PythonString"

# 6. Operations on String: arithmetic/relational/logical/membership/loop
# ------------------------------------

print("\n# 6. Operations on String: arithmetic/relational/logical/membership/ loop")
print("# ------------------------------------")

string_op1 = "Apple"
string_op2 = "Banana"
print("String op 1:", string_op1)
print("String op 2:", string_op2)

# a) Arithmetic operations - concatenation and repetition
concatenated_string_op = string_op1 + string_op2 # Concatenation
print("\na) Arithmetic - concatenation:", concatenated_string_op)

repeated_string_op = string_op1 * 3 # Repetition
print("   Arithmetic - repetition:", repeated_string_op)

# b) Relational operations - comparison (lexicographical order)
print("\nb) Relational operations (comparison):")
print("   string_op1 == 'Apple':", string_op1 == 'Apple')
print("   string_op1 == string_op2:", string_op1 == string_op2)
print("   string_op1 != string_op2:", string_op1 != string_op2)
print("   string_op1 < string_op2:", string_op1 < string_op2) # 'Apple' < 'Banana' lexicographically
print("   string_op1 > string_op2:", string_op1 > string_op2)
print("   string_op1 <= 'Apple':", string_op1 <= 'Apple')
print("   string_op1 >= 'Apple':", string_op1 >= 'Apple')

# c) Logical operations - strings are truthy if not empty, but logical operators are less common directly on strings (usually for boolean context derived from strings)
bool_string_op1 = bool(string_op1) # Non-empty string is True
bool_empty_string = bool("") # Empty string is False
print("\nc) Logical operations (truthiness):")
print("   bool(string_op1):", bool_string_op1)
print("   bool(''):", bool_empty_string)
# Logical operators can be used in conditions based on string truthiness (though less direct string manipulation)

# d) Membership testing - checking if a substring is present
print("\nd) Membership testing:")
print("   'App' in string_op1:", 'App' in string_op1)
print("   'app' in string_op1:", 'app' in string_op1) # Case-sensitive
print("   'Orange' in string_op1:", 'Orange' in string_op1) # Not present
print("   'Orange' not in string_op1:", 'Orange' not in string_op1)

# e) Looping through a string - iterates over characters
print("\ne) Looping through a string:")
for char in string_op1:
    print("   Character:", char)

print("   Looping with index:")
for index in range(len(string_op1)):
    print("   Index:", index, ", Character:", string_op1[index])

# 7. String Specific Methods: len/min/max/sorted

print("\n# 7. String Specific Methods: len/min/max/sorted")
print("# ------------------------------------")

method_string = "exampleString"
print("String for methods:", method_string)

# a) len() - returns the length of the string (number of characters)
print("\na) len(method_string):", len(method_string))

# b) min() - returns the character with the lowest ASCII value
print("b) min(method_string):", min(method_string))

# c) max() - returns the character with the highest ASCII value
print("c) max(method_string):", max(method_string))

# d) sorted(string) - returns a new sorted list of characters
sorted_chars = sorted(method_string)
print("d) sorted(method_string):", sorted_chars, type(sorted_chars))
print("   Original string remains unchanged:", method_string)

# sum() is not typically applicable to strings directly as it requires numeric values.

# 8. Advanced Topics: String Specific Functions (Methods)

print("\n# 8. Advanced Topics: String Specific Functions (Methods)")
print("# ------------------------------------")

advanced_string = "  Python String Methods Example  "
print("Advanced String:", advanced_string)

# a) Case conversion methods
upper_string = advanced_string.upper()
lower_string = advanced_string.lower()
title_string = "hello world".title() # Example on a different string
capitalize_string = "hello world".capitalize() # Example on a different string
swapcase_string = "HeLlO wOrLd".swapcase() # Example on a different string
print("\na) Case conversion methods:")
print("   upper():", upper_string)
print("   lower():", lower_string)
print("   title():", title_string)
print("   capitalize():", capitalize_string)
print("   swapcase():", swapcase_string)

# b) Stripping whitespace methods
stripped_string = advanced_string.strip() # Removes leading/trailing whitespace
lstripped_string = advanced_string.lstrip() # Removes leading whitespace
rstripped_string = advanced_string.rstrip() # Removes trailing whitespace
print("\nb) Stripping whitespace methods:")
print("   strip():", stripped_string)
print("   lstrip():", lstripped_string)
print("   rstrip():", rstripped_string)

# c) Splitting and joining strings
split_string = stripped_string.split(" ") # Splits into a list of words, using space as delimiter
split_commas = "item1,item2,item3".split(",") # Splits using comma
joined_string_method = "-".join(split_string) # Joins list back into string using "-" as separator
print("\nc) Splitting and joining strings:")
print("   split():", split_string)
print("   split(',') on 'item1,item2,item3':", split_commas)
print("   join():", joined_string_method)

# d) Finding substrings
find_index = stripped_string.find("String") # Returns starting index of substring, -1 if not found
find_index_not_found = stripped_string.find("NonExistent")
startswith_check = stripped_string.startswith("Python") # Checks if string starts with prefix
endswith_check = stripped_string.endswith("Example") # Checks if string ends with suffix
print("\nd) Finding substrings:")
print("   find('String'):", find_index)
print("   find('NonExistent'):", find_index_not_found)
print("   startswith('Python'):", startswith_check)
print("   endswith('Example'):", endswith_check)

# e) Replacing substrings
replaced_string = stripped_string.replace("String", "Text") # Replaces all occurrences
replaced_one_occurrence = stripped_string.replace("Methods", "Functions", 1) # Replace only the first occurrence
print("\ne) Replacing substrings:")
print("   replace('String', 'Text'):", replaced_string)
print("   replace('Methods', 'Functions', 1):", replaced_one_occurrence)

# f) Counting substrings
count_substring = stripped_string.count("e") # Counts occurrences of 'e'
print("\nf) Counting substrings:")
print("   count('e'):", count_substring)

# g) Formatting strings - f-strings (formatted string literals)
name = "Alice"
age = 30
formatted_fstring = f"Name: {name}, Age: {age}" # Using f-string for easy formatting
print("\ng) Formatting strings (f-strings):", formatted_fstring)

# 9. String Interning & Concatenation Performance
# ------------------------------------
# - Strings are immutable, so `s += "x"` in a loop does NOT modify s in
#   place - it builds a brand new string each time, copying all previous
#   characters. Repeating that n times costs O(n^2) total.
# - ''.join(list_of_strings) builds the result once, in O(n) total.
# - Interning: CPython caches short/identifier-like string literals so
#   equal literals may share the same object (see 'is' vs '==' in Fundamentals).

print("\n# 9. String Interning & Concatenation Performance")
print("# ------------------------------------")

import time

n = 20_000

start = time.perf_counter()
result = ""
for i in range(n):
    result += "x"        # O(n^2): new string object allocated every iteration
concat_time = time.perf_counter() - start

start = time.perf_counter()
result_join = "".join("x" for _ in range(n))   # O(n): single pass, single allocation
join_time = time.perf_counter() - start

print(f"'+=' loop concatenation ({n} iterations): {concat_time:.4f}s")
print(f"''.join() equivalent               : {join_time:.4f}s")
print("# join() is dramatically faster for large numbers of concatenations.")

interned_a = "hello"
interned_b = "hello"
print("\n'hello' is 'hello' (interned):", interned_a is interned_b)

# 10. Unicode & Encoding
# ------------------------------------
# - Python str is a sequence of Unicode code points (text).
# - bytes is a sequence of raw 8-bit values (binary data).
# - .encode(encoding) converts str -> bytes; .decode(encoding) converts bytes -> str.
# - UTF-8 is the dominant encoding: ASCII-compatible, variable-width (1-4 bytes/char).

print("\n# 10. Unicode & Encoding")
print("# ------------------------------------")

text = "café ✓"
utf8_bytes = text.encode("utf-8")
utf16_bytes = text.encode("utf-16")
print("text:", text)
print("encode('utf-8') :", utf8_bytes, "-", len(utf8_bytes), "bytes")
print("encode('utf-16'):", utf16_bytes, "-", len(utf16_bytes), "bytes")
print("decode back      :", utf8_bytes.decode("utf-8"))

try:
    "café".encode("ascii")   # 'é' has no ASCII representation
except UnicodeEncodeError as e:
    print("\nencode('ascii') on 'café' fails:", e)

# 11. String Formatting Mini-Language
# ------------------------------------
# - The format spec `{:[fill][align][sign][width][,][.precision][type]}`
#   controls how a value is rendered inside f-strings / str.format().
# - Common specs: '>10' (right-align, width 10), '.2f' (2 decimal places),
#   ',' (thousands separator), '>10.2f' (combine width + precision).

print("\n# 11. String Formatting Mini-Language")
print("# ------------------------------------")

value = 1234567.891
print(f"'{{:>15}}'  right-align width 15 : '{value:>15}'")
print(f"'{{:<15}}'  left-align  width 15 : '{value:<15}'")
print(f"'{{:^15}}'  center      width 15 : '{value:^15}'")
print(f"'{{:.2f}}'  2 decimal places      : '{value:.2f}'")
print(f"'{{:,}}'    thousands separator   : '{value:,}'")
print(f"'{{:,.2f}}' combine both          : '{value:,.2f}'")
print(f"'{{:08.2f}}' zero-padded width 8  : '{value:08.2f}'")
print(f"'{{:+.2f}}' force sign            : '{value:+.2f}'")
print(f"'{{:.1%}}'  percentage            : '{0.4567:.1%}'")
print(f"'{{:x}}'    hexadecimal (int)     : '{255:x}'")

# 12. str.translate() and str.maketrans()
# ------------------------------------
# - translate() replaces characters using a mapping table built by
#   maketrans(), doing many single-character substitutions in one pass -
#   faster and cleaner than chaining multiple .replace() calls.

print("\n# 12. str.translate() and str.maketrans()")
print("# ------------------------------------")

translation_table = str.maketrans("aeiou", "AEIOU")   # map each vowel to its uppercase
translated = "hello world".translate(translation_table)
print("maketrans('aeiou', 'AEIOU') applied to 'hello world':", translated)

# maketrans can also DELETE characters via a third argument
remove_table = str.maketrans("", "", "aeiou")   # delete all vowels
print("Deleting vowels:", "hello world".translate(remove_table))

# 13. Raw Strings vs Regular Strings
# ------------------------------------
# - A raw string (prefix r"...") treats backslashes literally - no escape
#   sequence processing. Essential for regex patterns and Windows file paths,
#   where backslashes are meaningful characters, not escape introducers.

print("\n# 13. Raw Strings vs Regular Strings")
print("# ------------------------------------")

regular_string = "C:\\Users\\name"    # backslashes must be escaped manually
raw_string = r"C:\Users\name"         # backslashes are literal, no escaping needed
print("regular_string:", regular_string)
print("raw_string    :", raw_string)
print("Equal:", regular_string == raw_string)

import re
pattern = r"\d+"   # raw string - \d means 'digit' to re, not an escape sequence
match = re.search(pattern, "Room 42")
print("\nre.search(r'\\d+', 'Room 42'):", match.group() if match else None)

# 14. Alignment & Padding Methods: ljust / rjust / center / zfill
# ------------------------------------
# - Padding makes text line up in columns. WHY: terminal output, reports and
#   fixed-width files only look right when every value takes the same width.
# - ljust(w)/rjust(w)/center(w) pad to width w using a fill character (space
#   by default). They NEVER cut text - if the string is already >= w it is
#   returned unchanged.
# - zfill(w) pads with '0' on the left and is sign-aware.

print("\n# 14. Alignment & Padding Methods: ljust / rjust / center / zfill")
print("# ------------------------------------")

s = "py"
print(f"ljust(8)       : '{s.ljust(8)}'")
print(f"rjust(8)       : '{s.rjust(8)}'")
print(f"center(8)      : '{s.center(8)}'")
print(f"ljust(8, '.')  : '{s.ljust(8, '.')}'     (second argument = fillchar)")
print(f"rjust(8, '-')  : '{s.rjust(8, '-')}'")
print(f"center(9, '*') : '{s.center(9, '*')}'")
print(f"center(8,'*') with an odd gap: '{'abc'.center(8, '*')}'  (extra char goes to one side)")

print("\nzfill - zero pad on the left, handles the sign for you:")
print("'42'.zfill(5)   :", "42".zfill(5))
print("'-42'.zfill(5)  :", "-42".zfill(5), " (zeros go AFTER the minus)")
print("'+7'.zfill(4)   :", "+7".zfill(4))
print("'-42'.rjust(5, '0'):", "-42".rjust(5, "0"), " (rjust is NOT sign-aware - gotcha!)")

# Gotcha: padding never truncates, and fillchar must be exactly ONE character
print("\n'too long'.ljust(3) :", repr("too long".ljust(3)), "(unchanged, never truncated)")
try:
    "x".ljust(5, "ab")
except TypeError as e:
    print("ljust with 2-char fillchar ->", type(e).__name__ + ":", e)

# 15. The Same Alignment via the Format Spec
# ------------------------------------
# - Spec shape: {value:[fill][align][width]} with align < (left) > (right)
#   ^ (center). Default align: text -> left, numbers -> right.
# - '0' before width means "zero pad, sign-aware" (like zfill, but for ints).

print("\n# 15. The Same Alignment via the Format Spec")
print("# ------------------------------------")

print(f"'{{:<10}}'   : '{'py':<10}'")
print(f"'{{:>10}}'   : '{'py':>10}'")
print(f"'{{:^10}}'   : '{'py':^10}'")
print(f"'{{:*^10}}'  : '{'py':*^10}'   (fill char BEFORE the align symbol)")
print(f"'{{:-<10}}'  : '{'py':-<10}'")
print(f"'{{:010d}}'  : '{42:010d}'")
print(f"'{{:010d}}'  : '{-42:010d}'  (sign handled)")
print(f"'{{:=+8d}}'  : '{42:=+8d}'  ('=' puts padding between sign and digits)")
print("Defaults -> text left-aligned:", f"'{'ab':6}'", " number right-aligned:", f"'{12:6}'")

# 16. Truncating Long Strings (and Combining Truncate + Pad)
# ------------------------------------
# - Padding makes short text longer; to make long text SHORTER you must cut it.
# - Slicing s[:n] cuts to n chars. In a format spec, '.N' on a STRING means
#   "max N characters" (precision) - on floats it means decimals.
# - Truncate + pad together gives strict fixed-width columns.

print("\n# 16. Truncating Long Strings (and Combining Truncate + Pad)")
print("# ------------------------------------")

title = "Introduction to Python Programming"
print("title[:12]        :", title[:12])
print(f"'{{:.12}}'        :", f"{title:.12}")

def shorten(text, n):
    """Cut text to at most n chars; mark the cut with an ellipsis (3 dots = '...')."""
    if len(text) <= n:
        return text
    return text[: max(n - 3, 0)] + "..."

print("shorten(title, 15):", shorten(title, 15))
print("shorten('short', 15):", shorten("short", 15))

print("\nTruncate + pad in ONE spec - {:<10.5} = left-align, width 10, max 5 chars:")
print(f"'{'abcdefghij':<10.5}'")
print(f"'{'hi':<10.5}'   (short text is only padded)")

w, p = 12, 6   # nested width fields: the {w} and {p} are replaced FIRST
print(f"nested fields, width={w} precision={p}: '{title:<{w}.{p}}'")
print(f"nested + ellipsis helper               : '{shorten(title, w):<{w}}'")

# 17. Number Formatting Codes
# ------------------------------------
# - Spec for numbers: [sign][#][0][width][, or _][.precision][type]
# - Types: f fixed, e scientific, % percent, b/o/x/X binary/octal/hex.

print("\n# 17. Number Formatting Codes")
print("# ------------------------------------")

big = 1234567.891
print(f"',' thousands      : {big:,}")
print(f"'_' thousands      : {1234567:_}      (underscore style, also valid Python literal)")
print(f"'_' on binary (groups of 4): {255:_b}")
print(f".2f                : {big:.2f}")
print(f",.2f               : {big:,.2f}")
print(f".3e (scientific)   : {big:.3e}")
print(f".1% (percent)      : {0.256:.1%}   (multiplies by 100 and adds %)")

n = 255
print(f"\nb / o / x / X      : {n:b}  {n:o}  {n:x}  {n:X}")
print(f"with # prefix      : {n:#b}  {n:#o}  {n:#x}  {n:#X}")
print(f"padded binary      : {5:08b}   (8 bits, zero-filled)")
print(f"padded #hex        : {n:#06x}   (width counts the 0x prefix too)")

print(f"\nsign '+'           : {5:+d} {-5:+d}")
print(f"sign ' ' (space)   : '{5: d}' '{-5: d}'   (space keeps columns aligned with negatives)")
print(f"sign '-' (default) : {5:-d} {-5:-d}")

# Gotcha: rounding is on the binary float, so some halves round 'wrong'
print(f"\nGotcha: {0.125:.2f} (exact half -> banker's rounding),  {2.675:.2f} (2.675 is really 2.67499999...)")

# 18. Dynamic Widths, the = Debug Specifier, and !r / !s / !a
# ------------------------------------
# - Any part of the spec can itself be a {field}, so width/precision can be
#   variables.
# - f"{x=}" (3.8+) prints the expression text AND its value - perfect for
#   quick debugging; it uses repr() by default.
# - Conversions: !s -> str(), !r -> repr(), !a -> ascii() (escapes non-ASCII).

print("\n# 18. Dynamic Widths, the = Debug Specifier, and !r / !s / !a")
print("# ------------------------------------")

for width in (6, 10):
    print(f"width={width:<2} -> '{'ok':^{width}}'")

value, decimals = 3.14159265, 3
print(f"dynamic precision: {value:.{decimals}f}   {value:{10}.{decimals}f}")

x = 7
name = "Ada"
print(f"\n{x=}")
print(f"{name=}")
print(f"{x * 2 + 1=}")
print(f"{x * 2 = }   <- spaces around '=' are kept, so you can style it")
print(f"{x=:05d}   <- '=' can be combined with a format spec")
print(f"{name=!s}   {name=!r}")

text = "café\n"
print(f"\n!s : {text!s}", end="")
print(f"!r : {text!r}      (shows quotes + escapes; best for debugging)")
print(f"!a : {text!a}     (non-ASCII becomes \\xe9)")
print("Why !r matters - the string '5' and the int 5 print the same, repr tells them apart:", f"{'5'} {5}  ->  {'5'!r} {5!r}")

# 19. Old-style %, str.format() and f-strings
# ------------------------------------
# - You will meet all three in real code, so read all three.
# - % style: '%s' any object via str, '%d' int, '%.2f' float, '%05d' zero pad,
#   '%(name)s' pulls from a dict. Operands go in a tuple (a single non-tuple is OK).

print("\n# 19. Old-style %, str.format() and f-strings")
print("# ------------------------------------")

user, age, price = "Asha", 31, 49.5
print("%s is %d years old"            % (user, age))
print("price: %.2f | id: %05d"       % (price, 42))
print("%(n)s owes %(amt).2f"         % {"n": user, "amt": price})
print("percent sign needs doubling: %d%%" % 90)
print("{} is {} years old".format(user, age))
print("{0} {1} {0}  (positional, reusable)".format("a", "b"))
print("{n} owes {amt:.2f}  (named)".format(n=user, amt=price))
print(f"{user} is {age} years old   (f-string)")

# Gotcha with %: a tuple argument must be wrapped in another tuple
point = (3, 4)
try:
    print("point = %s" % point)
except TypeError as e:
    print("'%s' % tuple ->", type(e).__name__ + ":", e)
print("fix: '%s' % (point,) ->", "point = %s" % (point,))

print("""
Which to use?
- f-strings  : default for new code - shortest, fastest, expressions inline.
- .format()  : when the template is stored separately / reused / built at
               runtime (an f-string is evaluated immediately, a template is not).
- % style    : know it to read old code and logging ('logging.info("x=%s", x)'
               defers formatting until needed). Avoid in new code.""")

# 20. Printing an Aligned Table from a List of Dicts
# ------------------------------------
# - Compute each column width from the data (max of header and values), then
#   use nested width fields. No hard-coded widths -> never breaks on new data.

print("\n# 20. Printing an Aligned Table from a List of Dicts")
print("# ------------------------------------")

rows = [
    {"name": "Apple",        "qty": 3,   "price": 1.5},
    {"name": "Watermelon",   "qty": 12,  "price": 120.25},
    {"name": "Fig",          "qty": 100, "price": 0.75},
]
cols = list(rows[0])
widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}

header = "  ".join(f"{c.title():<{widths[c]}}" if c == "name" else f"{c.title():>{widths[c]}}" for c in cols)
print(header)
print("  ".join("-" * widths[c] for c in cols))
for r in rows:
    print(f"{r['name']:<{widths['name']}}  {r['qty']:>{widths['qty']}}  {r['price']:>{widths['price']}.2f}")
print("Text is left-aligned, numbers right-aligned - the usual table convention.")

# 21. str.expandtabs()
# ------------------------------------
# - A tab '\t' jumps to the next tab stop (multiples of 8 by default), so the
#   gap it makes depends on where it appears. expandtabs(n) replaces each tab
#   with spaces so the text is predictable (tab stops every n columns).

print("\n# 21. str.expandtabs()")
print("# ------------------------------------")

line = "a\tbb\tccc\td"
print("repr  :", repr(line))
print("tabs=8:", repr(line.expandtabs()))
print("tabs=4:", repr(line.expandtabs(4)))
print("tabs=4 printed:\n" + line.expandtabs(4))
print("Note: 'a' + tab and 'ccc' + tab fill DIFFERENT numbers of spaces - they align to a stop.")

# 22. f-string Quoting Rules (Before vs After 3.12) and Brace Escaping
# ------------------------------------
# - Before 3.12 you could NOT reuse the same quote type inside an f-string
#   replacement field, and could not put a backslash there. 3.12 (PEP 701)
#   removed those limits.
# - To print a literal { or } double it: {{ and }}.

print("\n# 22. f-string Quoting Rules (Before vs After 3.12) and Brace Escaping")
print("# ------------------------------------")

import sys

d = {"k": "v"}
print("Works on every version - use a DIFFERENT quote inside:", f"{d['k']}")
if sys.version_info >= (3, 12):
    # Compiled from a string so older interpreters don't hit a SyntaxError on import
    code = 'f"{d["k"]}  <- same quotes reused inside (3.12+ only)"'
    print(eval(code))
    code2 = r"""f"{'-'.join(['a', 'b'])} and {'\n'.join(['l1', 'l2'])!r}  <- backslash inside the braces (3.12+ only)" """
    print(eval(code2))
else:
    print("Skipped: same-quote reuse and backslashes inside {} need Python 3.12+ (SyntaxError before).")

print(f"{{literal braces}} and a value in them: {{{x}}}")
print("same with .format():", "{{{}}}".format(x))
print("Gotcha: '%' formatting has no brace problem; .format() and f-strings DO, so double them.")

print("\n# End of String Explanation")

