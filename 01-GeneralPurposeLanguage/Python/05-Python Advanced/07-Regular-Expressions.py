import re

# 01. Regular Expressions - Introduction
# ------------------------------------
# - The `re` module lets you search, match, and manipulate strings using
#   patterns (regex) - useful for validation, extraction, and text processing.

print("# 01. Regular Expressions - Introduction")
print("# ------------------------------------")

# 02. re.match() - Match at the Start of a String
# ------------------------------------
result = re.match(r"Hello", "Hello, World!")
print("\n# 02. re.match()")
print(result)
print("matched text:", result.group() if result else None)

# 03. re.search() - Search Anywhere in a String
# ------------------------------------
result = re.search(r"World", "Hello, World!")
print("\n# 03. re.search()")
print("found:", result.group() if result else None)

# 04. re.findall() - Find All Non-Overlapping Matches
# ------------------------------------
text = "My numbers are 42, 17, and 8."
numbers = re.findall(r"\d+", text)
print("\n# 04. re.findall()")
print(numbers)

# 05. re.finditer() - Iterator of Match Objects (with positions)
# ------------------------------------
print("\n# 05. re.finditer()")
for match in re.finditer(r"\d+", text):
    print(f"matched '{match.group()}' at position {match.span()}")

# 06. re.sub() - Search and Replace
# ------------------------------------
censored = re.sub(r"\d+", "#", text)
print("\n# 06. re.sub()")
print(censored)

# 07. Common Pattern Building Blocks
# ------------------------------------
print("\n# 07. Common Pattern Building Blocks")
print("# \\d digit, \\w word char, \\s whitespace, . any char")
print("# +  one or more, * zero or more, ? optional, {n,m} range")
print("# ^  start of string, $ end of string")
print(re.findall(r"\w+", "Python is fun!"))       # words
print(re.findall(r"^\w+", "Python is fun!"))       # first word only
print(re.findall(r"\w+$", "Python is fun"))         # last word only (no trailing !)

# 08. Groups - Capturing Parts of a Match
# ------------------------------------
match = re.match(r"(\w+)@(\w+)\.com", "user@example.com")
print("\n# 08. Groups")
if match:
    print("full match:", match.group(0))
    print("username:", match.group(1))
    print("domain:", match.group(2))

# 09. Named Groups
# ------------------------------------
match = re.match(r"(?P<username>\w+)@(?P<domain>\w+)\.com", "admin@python.com")
print("\n# 09. Named Groups")
if match:
    print(match.groupdict())

# 10. Compiling Patterns for Reuse
# ------------------------------------
# - re.compile() precompiles a pattern for efficient repeated use.
email_pattern = re.compile(r"^[\w.\-]+@[\w\-]+\.\w+$")
print("\n# 10. Compiling Patterns for Reuse")
for email in ["good@example.com", "not-an-email", "also.good@sub.example.com"]:
    is_valid = bool(email_pattern.match(email))
    print(f"{email}: {'valid' if is_valid else 'invalid'}")

# 11. Splitting Strings with re.split()
# ------------------------------------
parts = re.split(r"[,;]\s*", "apple, banana; cherry,  date")
print("\n# 11. re.split()")
print(parts)

# 12. Greedy vs Non-Greedy Quantifiers
# ------------------------------------
# - By default, quantifiers (*, +, ?, {n,m}) are GREEDY - they match as
#   much text as possible. Adding a `?` after them makes them NON-GREEDY
#   (a.k.a. lazy) - they match as LITTLE text as possible.
html_like = "<b>bold</b> and <i>italic</i>"
print("\n# 12. Greedy vs Non-Greedy Quantifiers")
print("greedy    .* :", re.findall(r"<.*>", html_like))    # spans from first < to LAST >
print("non-greedy .*?:", re.findall(r"<.*?>", html_like))  # stops at the FIRST >

# 13. Lookahead and Lookbehind Assertions
# ------------------------------------
# - These check for a pattern WITHOUT including it in the match.
# - (?=...)  positive lookahead:  followed by ...
# - (?!...)  negative lookahead:  NOT followed by ...
# - (?<=...) positive lookbehind: preceded by ...
# - (?<!...) negative lookbehind: NOT preceded by ...
print("\n# 13. Lookahead / Lookbehind Assertions")
prices = "apples: $5, oranges: 3, pears: $12"
print("numbers preceded by $ (lookbehind):", re.findall(r"(?<=\$)\d+", prices))
print("digits followed by comma (lookahead):", re.findall(r"\d+(?=,)", prices))
print("word 'cat' NOT followed by 'nap':", re.findall(r"cat(?!nap)", "cat catnap category"))
print("word 'foo' NOT preceded by 'not':", re.findall(r"(?<!not )foo", "foo and not foo"))

# 14. Backreferences - Matching Repeated Text
# ------------------------------------
# - \1, \2, ... refer back to whatever an earlier group captured, letting
#   you match REPEATED text (like accidental doubled words).
print("\n# 14. Backreferences (\\1) - Repeated Words")
doubled_words_text = "this this is is a a test sentence"
print("repeated words found:", re.findall(r"\b(\w+)\s+\1\b", doubled_words_text))

# 15. Named Group Backreferences
# ------------------------------------
# - The same idea, but referencing a NAMED group with (?P=name) instead of
#   a numbered \1 - more readable in complex patterns.
print("\n# 15. Named Group Backreferences")
tag_text = "<div>content</div>"
tag_match = re.match(r"<(?P<tag>\w+)>.*</(?P=tag)>", tag_text)
print("matching open/close tag pair:", tag_match.group() if tag_match else None)
mismatched = re.match(r"<(?P<tag>\w+)>.*</(?P=tag)>", "<div>content</span>")
print("mismatched tags (no match):", mismatched)

# 16. Catastrophic Backtracking (conceptual warning)
# ------------------------------------
# - Nested quantifiers like (a+)+ can cause the regex engine to try an
#   EXPONENTIAL number of ways to split the input among the repeated
#   groups when the overall match ultimately fails. On a long enough
#   input this can hang a program for minutes or longer.
# - This demo does NOT actually run the slow pattern - it only explains
#   why `(a+)+b` against a long run of "a"s (with no trailing "b") is
#   dangerous, and shows the safe, non-backtracking equivalent.
print("\n# 16. Catastrophic Backtracking (conceptual, not executed)")
print("# DANGEROUS: re.match(r'(a+)+b', 'a' * 30)  <- can take exponential time to fail")
print("# WHY: (a+)+ can split N a's into groups in ~2^N different ways before giving up")
print("# SAFER equivalent (no nested quantifier ambiguity):")
safe_pattern = re.compile(r"a+b")
print("re.match(r'a+b', 'aaab'):", bool(safe_pattern.match("aaab")))
print("re.match(r'a+b', 'aaa') (fails fast, no ambiguity to backtrack through):",
      bool(safe_pattern.match("aaa")))

# 17. re.VERBOSE - Readable Multi-line Patterns
# ------------------------------------
# - re.VERBOSE (or re.X) lets you spread a pattern across multiple lines
#   with comments and insignificant whitespace, ignored at match time.
#   Use \s or [ ] to match an actual literal space.
print("\n# 17. re.VERBOSE for Readable Patterns")
verbose_email_pattern = re.compile(r"""
    ^                   # start of string
    [\w.\-]+            # username part
    @                   # the @ symbol
    [\w\-]+             # domain name
    \.\w+               # .com / .org / etc.
    $                   # end of string
""", re.VERBOSE)
print("verbose pattern matches 'good@example.com':", bool(verbose_email_pattern.match("good@example.com")))
