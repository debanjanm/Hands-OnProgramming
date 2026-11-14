## 0. Characteristics of {List}
## 1. Creating {List}
## 2. Acessing {List}
## 3. Adding {List}
## 4. Editing {List}
## 5. Deleting {List}
## 6. Operations on {List}: arithmatic/membership/ loop
## 7. {List} Specific Methods: len/sum/min/max count index reverse sort/sorted copy
## 8. Advancaed Topics: List Comprehension, Traverse List, Zip

# Python List Explanation

# 0. Characteristics of List
# ------------------------------------
# - Lists are used to store multiple items in a single variable.
# - Lists are ordered, mutable (changeable), and allow duplicate values.
# - List items are indexed, the first item has index [0], the second item has index [1] etc.
# - Lists are created using square brackets [].

print("\n# 0. Characteristics of List")
print("# ------------------------------------")
print("# - Ordered, mutable, allows duplicates, indexed.")

# 1. Creating List
# ------------------------------------
# - Lists can be created using square brackets [] or the list() constructor.

print("\n# 1. Creating List")
print("# ------------------------------------")

# a) Empty List
empty_list = []
print("a) Empty List:", empty_list, type(empty_list))

empty_list_constructor = list()
print("   Using list() constructor:", empty_list_constructor, type(empty_list_constructor))

# b) List with initial values
fruit_list = ["apple", "banana", "cherry"]
print("\nb) List with initial values:", fruit_list)

number_list = [1, 2, 3, 4, 5]
print("   List of numbers:", number_list)

mixed_list = [1, "apple", True, 3.14]
print("   List with mixed data types:", mixed_list)

# c) Creating list from other iterables (e.g., tuple, string)
tuple_data = (10, 20, 30)
list_from_tuple = list(tuple_data)
print("\nc) List from tuple:", list_from_tuple)

string_data = "hello"
list_from_string = list(string_data)
print("   List from string:", list_from_string)

# 2. Accessing List Items
# ------------------------------------
# - List items are accessed by referring to the index number.
# - Indexing starts from 0.
# - Negative indexing means start from the end, -1 refers to the last item, -2 refers to the second last item etc.
# - Slicing can be used to access a range of items.

print("\n# 2. Accessing List Items")
print("# ------------------------------------")

print("Original List:", fruit_list)

# a) Accessing by index
first_fruit = fruit_list[0]
print("a) Accessing first item [0]:", first_fruit)

second_fruit = fruit_list[1]
print("   Accessing second item [1]:", second_fruit)

last_fruit = fruit_list[-1]
print("   Accessing last item [-1]:", last_fruit)

# b) Slicing - get a range of items
slice_list_1_3 = fruit_list[1:3] # Items from index 1 to 2 (not including 3)
print("\nb) Slicing [1:3]:", slice_list_1_3)

slice_list_start_2 = fruit_list[2:] # Items from index 2 to the end
print("   Slicing [2:]:", slice_list_start_2)

slice_list_start_end = fruit_list[:] # Copy of the entire list
print("   Slicing [:] (copy):", slice_list_start_end)

# 3. Adding List Items
# ------------------------------------
# - Items can be added to the end of the list using append().
# - Items can be inserted at a specific position using insert().
# - To append elements from another list to the current list, use extend().

print("\n# 3. Adding List Items")
print("# ------------------------------------")

print("Initial List:", fruit_list)

# a) append() - add item to the end
fruit_list.append("orange")
print("a) append('orange'):", fruit_list)

# b) insert() - add item at a specific index
fruit_list.insert(1, "mango") # Insert 'mango' at index 1
print("b) insert(1, 'mango'):", fruit_list)

# c) extend() - add elements of another list to the current list
more_fruits = ["grape", "kiwi"]
fruit_list.extend(more_fruits)
print("c) extend(['grape', 'kiwi']):", fruit_list)

# 4. Editing List Items
# ------------------------------------
# - Items can be edited by referring to the index.
# - Slicing can be used to edit a range of items.

print("\n# 4. Editing List Items")
print("# ------------------------------------")

print("List before editing:", fruit_list)

# a) Editing item by index
fruit_list[0] = "apple_edited"
print("a) Editing index [0]:", fruit_list)

# b) Editing a range of items using slicing
fruit_list[1:3] = ["mango_edited", "banana_edited"] # Replace items at index 1 and 2
print("b) Editing slice [1:3]:", fruit_list)

# c) Inserting items using slicing (replacing 0 items effectively inserting)
fruit_list[3:3] = ["inserted_fruit"] # Insert 'inserted_fruit' at index 3 without removing any existing items
print("c) Inserting with slice [3:3]:", fruit_list)

# 5. Deleting List Items
# ------------------------------------
# - remove(item): Removes the first occurrence of the specified value.
# - pop(index): Removes the item at the specified index (or the last item if index is not specified) and returns the removed item.
# - del keyword: Deletes an item at a specific index, or slices, or the entire list.
# - clear(): Empties the list.

print("\n# 5. Deleting List Items")
print("# ------------------------------------")

print("List before deletion:", fruit_list)

# a) remove(item) - remove by value
fruit_list.remove("banana_edited") # Removes the first 'banana_edited'
print("a) remove('banana_edited'):", fruit_list)

# b) pop(index) - remove by index, returns removed item
removed_fruit = fruit_list.pop(2) # Removes item at index 2
print("b) pop(2):", fruit_list, "Removed item:", removed_fruit)

removed_last_fruit = fruit_list.pop() # Removes the last item if index is not specified
print("   pop() (last item):", fruit_list, "Removed last item:", removed_last_fruit)

# c) del keyword - delete by index
del fruit_list[0] # Delete item at index 0
print("c) del fruit_list[0]:", fruit_list)

# d) del keyword - delete a slice
del fruit_list[0:2] # Delete items from index 0 to 1
print("   del fruit_list[0:2]:", fruit_list)

# e) del keyword - delete entire list
# del fruit_list
# print("e) del fruit_list: (fruit_list no longer exists)")
# try:
#     print(fruit_list) # This will cause NameError if list is deleted
# except NameError as e:
#     print("   Error:", e)

# f) clear() - empty the list
fruit_list.clear()
print("f) clear():", fruit_list)

# Reset fruit_list for further examples
fruit_list = ["apple", "banana", "cherry", "date"]

# 6. Operations on List: arithmetic/membership/ loop
# ------------------------------------

print("\n# 6. Operations on List: arithmetic/membership/ loop")
print("# ------------------------------------")

print("List for operations:", fruit_list)

# a) Arithmetic operations - concatenation and repetition
list1 = [1, 2, 3]
list2 = [4, 5, 6]

concatenated_list = list1 + list2 # List concatenation
print("\na) Arithmetic - concatenation:")
print("   list1 + list2:", concatenated_list)

repeated_list = list1 * 3 # List repetition
print("\n   Arithmetic - repetition:")
print("   list1 * 3:", repeated_list)

# b) Membership testing (checking if an item exists)
print("\nb) Membership testing:")
print("'apple' in fruit_list:", "apple" in fruit_list)
print("'banana' in fruit_list:", "banana" in fruit_list)
print("'orange' in fruit_list:", "orange" in fruit_list) # Item does not exist
print("'orange' not in fruit_list:", "orange" not in fruit_list)

# c) Looping through a list
print("\nc) Looping through a list:")

print("   - Looping through elements:")
for fruit in fruit_list:
    print("     Fruit:", fruit)

print("   - Looping through index and elements using enumerate():")
for index, fruit in enumerate(fruit_list):
    print("     Index:", index, ", Fruit:", fruit)

print("   - Looping using index range:")
for i in range(len(fruit_list)):
    print("     Index:", i, ", Fruit:", fruit_list[i])

# 7. List Specific Methods: len/sum/min/max/count/index/reverse/sort/sorted/copy

print("\n# 7. List Specific Methods: len/sum/min/max/count/index/reverse/sort/sorted/copy")
print("# ------------------------------------")

number_list_methods = [5, 2, 8, 1, 8, 3]
print("List for methods:", number_list_methods)

# a) len() - number of items in the list
print("\na) len(number_list_methods):", len(number_list_methods))

# b) sum() - sum of all items in the list (numeric list)
print("b) sum(number_list_methods):", sum(number_list_methods))

# c) min() and max() - min/max item in the list
print("c) min(number_list_methods):", min(number_list_methods), ", max(number_list_methods):", max(number_list_methods))

# d) count(item) - count occurrences of an item
print("d) count(8):", number_list_methods.count(8))
print("   count(4):", number_list_methods.count(4))

# e) index(item) - returns index of the first occurrence of an item
print("e) index(8):", number_list_methods.index(8))
# print("   index(4):", number_list_methods.index(4)) # ValueError: 4 is not in list

# f) reverse() - reverses the list in place (modifies original list)
list_to_reverse = number_list_methods.copy() # Operate on a copy to keep original
list_to_reverse.reverse()
print("\nf) reverse(): Original:", number_list_methods, ", Reversed copy:", list_to_reverse)

# g) sort() - sorts the list in place (modifies original list) - ascending by default
list_to_sort = number_list_methods.copy() # Operate on a copy
list_to_sort.sort()
print("\ng) sort(): Original:", number_list_methods, ", Sorted copy (ascending):", list_to_sort)

list_to_sort_descending = number_list_methods.copy() # Operate on a copy
list_to_sort_descending.sort(reverse=True) # Sort in descending order
print("   sort(reverse=True): Original:", number_list_methods, ", Sorted copy (descending):", list_to_sort_descending)

# h) sorted(list) - returns a new sorted list (does not modify original)
sorted_list_ascending = sorted(number_list_methods)
print("\nh) sorted(): Original:", number_list_methods, ", Sorted new list (ascending):", sorted_list_ascending)

sorted_list_descending = sorted(number_list_methods, reverse=True)
print("   sorted(reverse=True): Original:", number_list_methods, ", Sorted new list (descending):", sorted_list_descending)

# i) copy() - returns a shallow copy of the list
copied_list = number_list_methods.copy()
print("\ni) copy(): Original:", number_list_methods, ", Copied list:", copied_list)
print("   copied_list is number_list_methods:", copied_list is number_list_methods) # Check if it is the same object (should be False)
print("   copied_list == number_list_methods:", copied_list == number_list_methods) # Check if values are the same (should be True)

# 8. Advanced Topics: List Comprehension, Traverse List, Zip

print("\n# 8. Advanced Topics: List Comprehension, Traverse List, Zip")
print("# ------------------------------------")

# a) List Comprehension - concise way to create lists

print("\na) List Comprehension:")

# Example 1: Create a list of squares of numbers 0-9
squares_list = [x**2 for x in range(10)]
print("   Example 1: Squares of numbers 0-9:", squares_list)

# Example 2: Create a list of even numbers from 0-9
even_numbers_list = [x for x in range(10) if x % 2 == 0]
print("   Example 2: Even numbers from 0-9:", even_numbers_list)

# Example 3: Conditional expressions in list comprehension
fruit_status = ["Fresh" if fruit in ["apple", "banana"] else "Stale" for fruit in fruit_list]
print("   Example 3: Conditional status for fruits:", fruit_status)

# b) Traverse List - different ways to iterate

print("\nb) Traverse List:")

print("   - Basic for loop (element-wise):")
for fruit in fruit_list:
    print("     Fruit:", fruit)

print("   - Index-based loop:")
for i in range(len(fruit_list)):
    print("     Index:", i, ", Fruit:", fruit_list[i])

print("   - Using enumerate() for index and element:")
for index, fruit in enumerate(fruit_list):
    print("     Index:", index, ", Fruit:", fruit)

# c) Zip function - combining multiple lists element-wise

print("\nc) Zip Function:")

list_names = ["Alice", "Bob", "Charlie"]
list_ages = [25, 30, 28]
list_cities = ["New York", "London", "Paris"]

# Example 1: Zip two lists - create pairs
zipped_pairs = zip(list_names, list_ages)
print("   Example 1: zip(list_names, list_ages):", list(zipped_pairs))

# Example 2: Zip three lists - create tuples of three
zipped_triples = zip(list_names, list_ages, list_cities)
print("   Example 2: zip(list_names, list_ages, list_cities):", list(zipped_triples))

# Example 3: Iterate through zipped lists
print("   Example 3: Iterating through zipped lists:")
for name, age, city in zip(list_names, list_ages, list_cities):
    print(f"     Name: {name}, Age: {age}, City: {city}")

# Example 4: Creating dictionary using zip (keys and values from lists)
name_age_dict = dict(zip(list_names, list_ages))
print("   Example 4: Creating dictionary using zip:", name_age_dict)

# 9. List Over-Allocation & Amortized O(1) Append
# ------------------------------------
# - Lists are backed by a contiguous array. To avoid resizing (and copying
#   every element) on every single append, CPython over-allocates extra
#   capacity when it does need to grow.
# - Most append() calls just write into unused capacity - O(1). Occasionally
#   the array is full and must be reallocated/copied - O(n) that one time.
# - Averaged ("amortized") over many appends, this works out to O(1) per append.

print("\n# 9. List Over-Allocation & Amortized O(1) Append")
print("# ------------------------------------")

import sys
growing_list = []
previous_size = sys.getsizeof(growing_list)
for i in range(10):
    growing_list.append(i)
    current_size = sys.getsizeof(growing_list)
    if current_size != previous_size:
        print(f"   len={len(growing_list):>2} -> reallocated, size in bytes: {current_size}")
        previous_size = current_size
print("# Notice capacity jumps in chunks, not one slot per append -")
print("# that's the over-allocation strategy paying off.")

# 10. Shallow Copy vs Deep Copy
# ------------------------------------
# - A shallow copy (list.copy(), list[:], or copy.copy()) creates a new
#   outer list, but nested mutable objects inside it are still SHARED
#   with the original - mutating a nested list affects both.
# - copy.deepcopy() recursively copies everything, so nested objects are
#   fully independent too.

print("\n# 10. Shallow Copy vs Deep Copy")
print("# ------------------------------------")

original_nested = [[1, 2], [3, 4]]
shallow = original_nested.copy()
shallow[0].append("oops")   # mutates the SAME inner list as original_nested[0]
print("After shallow copy + shallow[0].append('oops'):")
print("   original_nested:", original_nested, "(inner list changed too!)")
print("   shallow        :", shallow)

import copy
original_nested = [[1, 2], [3, 4]]
deep = copy.deepcopy(original_nested)
deep[0].append("safe")      # inner list is an independent copy
print("\nAfter copy.deepcopy() + deep[0].append('safe'):")
print("   original_nested:", original_nested, "(unaffected)")
print("   deep           :", deep)

# 11. List as Stack vs deque as Queue
# ------------------------------------
# - list.append()/list.pop() (no index) both operate at the END - O(1).
#   That makes list a fine stack (LIFO).
# - list.pop(0) or list.insert(0, x) must shift EVERY remaining element -
#   O(n). Using a list as a FIFO queue is slow for large lists.
# - collections.deque supports O(1) appends/pops at BOTH ends - use it
#   for queues.

print("\n# 11. List as Stack vs deque as Queue")
print("# ------------------------------------")

stack = []
stack.append(1); stack.append(2); stack.append(3)
print("Stack (list) after pushes:", stack)
print("stack.pop() (LIFO, O(1)):", stack.pop(), "-> remaining:", stack)

from collections import deque
queue = deque([1, 2, 3])
print("\nQueue (deque):", queue)
print("queue.popleft() (FIFO, O(1)):", queue.popleft(), "-> remaining:", queue)
print("# list.pop(0) would also work but is O(n) - it shifts every remaining item.")

# 12. Sort Stability + key= with itemgetter/attrgetter
# ------------------------------------
# - Python's sort (Timsort) is STABLE: equal elements keep their original
#   relative order - useful for multi-key sorts (sort by secondary key first).
# - operator.itemgetter/attrgetter build a fast key function without a lambda,
#   for sorting sequences of tuples/dicts or objects respectively.

print("\n# 12. Sort Stability + key= with itemgetter/attrgetter")
print("# ------------------------------------")

from operator import itemgetter, attrgetter

people = [("Bob", 25), ("Alice", 30), ("Zoe", 25), ("Amy", 30)]
by_age = sorted(people, key=itemgetter(1))   # sort by age only
print("sorted by age (itemgetter(1)):", by_age)
print("# Bob stayed before Zoe, Alice stayed before Amy -> stability preserved original order for ties.")

class Person:
    def __init__(self, name, age):
        self.name, self.age = name, age
    def __repr__(self):
        return f"Person({self.name!r}, {self.age})"

person_objs = [Person("Bob", 25), Person("Alice", 30)]
by_name_attr = sorted(person_objs, key=attrgetter("name"))
print("sorted objects by attrgetter('name'):", by_name_attr)

# 13. List Comprehension Performance vs map/filter
# ------------------------------------
# - List comprehensions compile to specialized bytecode (LIST_APPEND in a
#   tight loop) and are typically as fast as or faster than map()/filter(),
#   while staying more readable for most cases.

print("\n# 13. List Comprehension Performance vs map/filter")
print("# ------------------------------------")

import timeit

comprehension_time = timeit.timeit("[x * 2 for x in range(1000)]", number=1000)
map_time = timeit.timeit("list(map(lambda x: x * 2, range(1000)))", number=1000)

print(f"List comprehension: {comprehension_time:.4f}s (1000 runs)")
print(f"map() + lambda    : {map_time:.4f}s (1000 runs)")
print("# Comprehensions avoid the overhead of a Python-level function call")
print("# per element that lambda-based map() incurs.")

# 14. Modifying a List While Iterating Over It (the Skipping Bug)
# ------------------------------------
# - A `for` loop over a list walks by INDEX: it keeps an internal position
#   (0, 1, 2, ...) and reads lst[position] each step.
# - If you remove an item, everything after it shifts one slot left, but the
#   loop's position still moves forward by one - so the item that slid into
#   the current slot is never looked at. No error is raised: silent bug.

print("\n# 14. Modifying a List While Iterating Over It (the Skipping Bug)")
print("# ------------------------------------")

nums = [2, 4, 6, 1, 8]          # we want to remove ALL even numbers
for x in nums:
    print(f"  visiting {x}  list now {nums}")
    if x % 2 == 0:
        nums.remove(x)
print("Expected: [1]   Actual:", nums, " <- 4 and 8 survived (skipped)")

# Step by step: idx0 -> 2 (removed, list=[4,6,1,8]); idx1 -> 6 (4 slid into
# idx0 and was skipped; 6 removed -> [4,1,8]); idx2 -> 8 (1 skipped too; 8
# removed -> [4,1]); idx3 is out of range, loop ends. 4 never got checked.

# 15. Safe Patterns (pick the one that fits)
# ------------------------------------
print("\n# 15. Safe Patterns (pick the one that fits)")
print("# ------------------------------------")

def fresh():
    return [2, 4, 6, 1, 8, 3]

# (a) Iterate over a COPY, mutate the original
lst = fresh()
for x in lst[:]:                 # lst[:] is a shallow copy, so removals don't affect the walk
    if x % 2 == 0:
        lst.remove(x)
print("(a) loop over copy lst[:]        :", lst)

# (b) Build a NEW list with a comprehension (usually the best choice)
lst = fresh()
lst = [x for x in lst if x % 2 != 0]
print("(b) comprehension (keep the odds):", lst)

# (b2) ...but if other code holds a reference to the same list, change it in place
lst = fresh()
alias = lst
lst[:] = [x for x in lst if x % 2 != 0]       # slice assignment keeps the SAME object
print("(b2) slice assignment, alias sees:", alias)

# (c) Iterate in reverse - removing at index i only shifts items AFTER i, which
#     a reversed walk has already visited
lst = fresh()
for i in range(len(lst) - 1, -1, -1):
    if lst[i] % 2 == 0:
        del lst[i]
print("(c) reverse index loop           :", lst)

# (d) filter() - returns a lazy iterator, wrap in list()
lst = fresh()
print("(d) list(filter(...))            :", list(filter(lambda v: v % 2, lst)))

# (e) Collect indexes first, delete afterwards (from the highest index down!)
lst = fresh()
to_delete = [i for i, v in enumerate(lst) if v % 2 == 0]
for i in reversed(to_delete):
    del lst[i]
print("(e) collect indexes, then delete :", lst)
print("Gotcha for (e): deleting in ASCENDING order shifts later indexes and kills the wrong items.")

# 16. Inserting While Iterating (Infinite-Loop Risk)
# ------------------------------------
# - Insert/append ahead of the loop position and the loop keeps finding new
#   items forever, because the list grows as fast as the loop eats it.
# - Demonstrated here with a guard so it stops after a few steps.

print("\n# 16. Inserting While Iterating (Infinite-Loop Risk)")
print("# ------------------------------------")

items = [1, 2, 3]
steps = 0
for x in items:
    steps += 1
    items.append(x + 10)         # grows by one every step -> never exhausted
    if steps == 6:               # our safety guard; without it this never ends
        print("  guard hit! list kept growing:", items)
        break

# insert(0, ...) shifts the SAME item into the next slot, so it is visited twice
items = ["a", "b"]
seen = []
for x in items:
    seen.append(x)
    if len(items) < 4:           # guard again
        items.insert(0, "new")
print("insert(0, ..) while looping, items seen:", seen, " ('a' is revisited each time it is shifted right)")

safe = [y for x in [1, 2, 3] for y in (x, x + 10)]   # build the bigger result in a NEW list instead
print("Safe: build a new list instead     :", safe)

# 17. list.sort() Returns None  vs  sorted()
# ------------------------------------
# - Python convention: methods that change an object IN PLACE return None so
#   you can't confuse them with methods that return a new object.

print("\n# 17. list.sort() Returns None vs sorted()")
print("# ------------------------------------")

data = [3, 1, 2]
result = data.sort()
print("x = data.sort()  -> x is", result, "| data is now", data)   # sorted in place, result is None

data = [3, 1, 2]
result = sorted(data)
print("x = sorted(data) -> x is", result, "| data still", data)

try:
    data = [3, 1, 2]
    print("data.sort()[0] ->", data.sort()[0])
except TypeError as e:
    print("chaining on the None ->", type(e).__name__ + ":", e)

print("Same family: reverse(), append(), extend(), insert(), remove() all return None.")
print("sorted() accepts ANY iterable (tuple, set, dict, str) and always returns a list:", sorted("cab"))

# Quick recap of options (full detail in section 12)
words = ["bb", "a", "ccc", "dd"]
print("key + reverse:", sorted(words, key=len, reverse=True), "| stable: 'bb' stays before 'dd' (equal length)")

# 18. Sorting Mixed Types Raises TypeError
# ------------------------------------
# - Sorting needs `<` between items. int < str is undefined in Python 3
#   (Python 2 allowed it - a source of old bugs).

print("\n# 18. Sorting Mixed Types Raises TypeError")
print("# ------------------------------------")

mixed = [3, "apple", 1, "banana"]
try:
    mixed.sort()
except TypeError as e:
    print("sort() on mixed ->", type(e).__name__ + ":", e)
print("list after the failed sort (unchanged):", mixed)

print("Fix 1 - sort by a common key:", sorted(mixed, key=str))
print("Fix 2 - split by type first :", sorted(v for v in mixed if isinstance(v, int)),
      sorted(v for v in mixed if isinstance(v, str)))
print("Also: None breaks sorting -", end=" ")
try:
    sorted([2, None, 1])
except TypeError as e:
    print(e)
print("Fix with a key that ranks None last:", sorted([2, None, 1], key=lambda v: (v is None, v or 0)))

print("\n# End of List Explanation")

