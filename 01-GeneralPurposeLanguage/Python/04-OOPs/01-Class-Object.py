## 01. OOPs Introduction
## 02. Importance of OOPs
## 03. Class and Object Definitions, Relationship, Differences 
## 04. Create a Class
## 05. Create a Object
## 06. Magic Methods
## 07. Self Parameter
## 08. Class and Instance Variables
## 09. Reference Variables, Pass By Reference
## 10. Modify and Delete Object Properties, Objects 

# 01. OOPs Introduction
# ------------------------------------
# - OOPs stands for Object-Oriented Programming System.
# - It is a programming paradigm based on the concept of "objects," which can contain data, in the form of fields (attributes or properties), and code, in the form of procedures (methods).
# - OOPs focuses on creating reusable code by grouping related data and functions into objects.
# - Key concepts in OOPs include: Classes, Objects, Encapsulation, Inheritance, Polymorphism, Abstraction.

print("# 01. OOPs Introduction")
print("# ------------------------------------")
print("# - Object-Oriented Programming System.")
print("# - Paradigm based on 'objects' with data (attributes) and code (methods).")
print("# - Focuses on reusable code through object composition.")
print("# - Key concepts: Classes, Objects, Encapsulation, Inheritance, Polymorphism, Abstraction.")

# 02. Importance of OOPs
# ------------------------------------
# - Modularity: OOPs encourages breaking down complex problems into smaller, manageable objects, making code easier to organize and understand.
# - Reusability: Classes and objects can be reused in different parts of the application and in other projects, reducing code duplication and development time.
# - Encapsulation: Bundling data and methods that operate on that data within objects protects data from accidental modification and simplifies interfaces.
# - Abstraction: Hiding complex implementation details and showing only necessary information to the user simplifies interaction with objects.
# - Inheritance: Allows creating new classes (child classes) based on existing classes (parent classes), promoting code reuse and establishing relationships between objects.
# - Polymorphism: Enables objects of different classes to be treated as objects of a common type, simplifying code and enhancing flexibility.
# - Maintainability: OOPs code is typically easier to maintain and debug due to its modular structure and clear object boundaries.

print("\n# 02. Importance of OOPs")
print("# ------------------------------------")
print("# - Modularity: Breaks down problems, easier organization.")
print("# - Reusability: Classes/objects reusable, reduces duplication.")
print("# - Encapsulation: Protects data, simplifies interfaces.")
print("# - Abstraction: Hides complexity, simplifies object interaction.")
print("# - Inheritance: Code reuse, establishes relationships.")
print("# - Polymorphism: Flexibility, objects of different classes treated uniformly.")
print("# - Maintainability: Easier to maintain and debug.")

# 03. Class and Object Definitions, Relationship, Differences
# ------------------------------------
# - Class: A blueprint or template for creating objects. It defines the attributes (data) and methods (behavior) that objects of that class will have.
# - Object: An instance of a class. It is a concrete entity created based on the class blueprint. Each object has its own data but shares the methods defined by the class.
# - Relationship: Objects are created from classes. A class is like a factory, and objects are the products made by that factory.
# - Differences:
#   - Class is a logical entity, object is a physical entity (in memory).
#   - Class is a template/blueprint, object is an instance/realization of the class.
#   - Class is defined once, objects can be multiple based on a single class.

print("\n# 03. Class and Object Definitions, Relationship, Differences")
print("# ------------------------------------")
print("# - Class: Blueprint/template, defines attributes (data) and methods (behavior).")
print("# - Object: Instance of a class, concrete entity with its own data, shares class methods.")
print("# - Relationship: Objects created from classes (Class is blueprint, Object is instance).")
print("# - Differences:")
print("#   - Class: Logical entity, Object: Physical entity (in memory).")
print("#   - Class: Template/blueprint, Object: Instance/realization.")
print("#   - Class: Defined once, Objects: Multiple instances from a class.")

# 04. Create a Class
# ------------------------------------
# - In Python, a class is created using the `class` keyword, followed by the class name and a colon `:`.
# - Class names are typically written in PascalCase (CapWords).
# - Classes can contain:
#   - Attributes (variables): To store data.
#   - Methods (functions): To define behavior.
# - The `__init__` method is a special method (constructor) that is automatically called when an object is created from the class. It is used to initialize object attributes.

print("\n# 04. Create a Class")
print("# ------------------------------------")
print("# - Use 'class' keyword, followed by ClassName:.")
print("# - Class names in PascalCase (CapWords).")
print("# - Can contain attributes (variables) and methods (functions).")
print("# - __init__ method (constructor) to initialize object attributes.")

# Example of creating a class
print("\n# Example - Creating a Class:")
print("class Dog:")
print("    def __init__(self, name, breed):")
print("        self.name = name")
print("        self.breed = breed")
print("    def bark(self):")
print("        print(\"Woof!\")")

class Dog:
    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        print("Woof!")

print("# Class 'Dog' created successfully.")

# 05. Create an Object
# ------------------------------------
# - To create an object (instance) of a class, you call the class name as if it were a function, passing any required arguments to the class constructor (`__init__` method).
# - Each object created will be an independent instance of the class, with its own set of attribute values.

print("\n# 05. Create an Object")
print("# ------------------------------------")
print("# - Call ClassName() to create an object, passing constructor arguments.")
print("# - Each object is an independent instance with its own attributes.")

# Example of creating objects
print("\n# Example - Creating Objects:")
print("my_dog = Dog(\"Buddy\", \"Golden Retriever\")")
print("another_dog = Dog(\"Lucy\", \"Labrador\")")

my_dog = Dog("Buddy", "Golden Retriever")
another_dog = Dog("Lucy", "Labrador")

print("# Objects 'my_dog' and 'another_dog' created from class 'Dog'.")
print("print(\"my_dog is an instance of Dog:\", isinstance(my_dog, Dog))")
print("print(\"another_dog is an instance of Dog:\", isinstance(another_dog, Dog))")
print("print(\"my_dog's name:\", my_dog.name)")
print("print(\"another_dog's breed:\", another_dog.breed)")
print("my_dog.bark()")
print("another_dog.bark()")

print("\n# Output from Object Creation & Usage:")
print("my_dog is an instance of Dog:", isinstance(my_dog, Dog))
print("another_dog is an instance of Dog:", isinstance(another_dog, Dog))
print("my_dog's name:", my_dog.name)
print("another_dog's breed:", another_dog.breed)
my_dog.bark()
another_dog.bark()

# 06. Magic Methods
# ------------------------------------
# - Magic methods (or special methods) in Python are methods that have double underscores at the beginning and end of their names (e.g., `__init__`, `__str__`).
# - They are used to implement special behaviors in classes, such as object initialization (`__init__`), string representation (`__str__`, `__repr__`), operator overloading, and more.
# - `__init__(self, ...)`: Constructor, called when an object is created.
# - `__str__(self)`: Should return a user-friendly string representation of the object, called by `str()` and `print()`.
# - `__repr__(self)`: Should return a detailed string representation of the object, ideally one that could recreate the object, used for debugging and development.

print("\n# 06. Magic Methods")
print("# ------------------------------------")
print("# - Special methods with double underscores (e.g., __init__, __str__).")
print("# - Implement special behaviors like initialization, string representation, operators.")
print("# - __init__(self, ...): Constructor, object initialization.")
print("# - __str__(self): User-friendly string representation (for print(), str()).")
print("# - __repr__(self): Detailed string representation (for debugging, object recreation).")

# Example of Magic Methods in a Class
print("\n# Example - Magic Methods:")
print("class Book:")
print("    def __init__(self, title, author, pages):")
print("        self.title = title")
print("        self.author = author")
print("        self.pages = pages")
print("    def __str__(self):")
print("        return f\"{self.title} by {self.author}\"")
print("    def __repr__(self):")
print("        return f\"Book(title='{self.title}', author='{self.author}', pages={self.pages})\"")

class Book:
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages

    def __str__(self):
        return f"{self.title} by {self.author}"

    def __repr__(self):
        return f"Book(title='{self.title}', author='{self.author}', pages={self.pages})"

my_book = Book("The Hitchhiker's Guide to the Galaxy", "Douglas Adams", 224)
print("# Class 'Book' with __init__, __str__, __repr__ methods created.")
print("print(\"String representation (__str__):\", str(my_book))")
print("print(\"Representation for debugging (__repr__):\", repr(my_book))")
print("print(\"Direct printing (__str__ is implicitly called):\", my_book)")
print("print(\"Evaluating the object in REPL would use __repr__ (demonstration with repr()):\", eval(repr(my_book)))") # eval(repr(my_book)) demonstrates the recreatable nature of __repr__ for simple cases

print("\n# Output from Magic Methods:")
print("String representation (__str__):", str(my_book))
print("Representation for debugging (__repr__):", repr(my_book))
print("Direct printing (__str__ is implicitly called):", my_book)
# print("Evaluating the object in REPL would use __repr__ (demonstration with repr()):", eval(repr(my_book)))

# 07. Self Parameter
# ------------------------------------
# - `self` is a convention in Python, the first parameter in instance methods.
# - It refers to the instance of the object itself. When you call a method on an object, Python automatically passes the object itself as the first argument, which is conventionally named `self`.
# - `self` allows you to access instance variables and call other instance methods within the class.
# - It is essential to include `self` as the first parameter in any method that operates on the instance of the class.

print("\n# 07. Self Parameter")
print("# ------------------------------------")
print("# - First parameter in instance methods, convention is 'self'.")
print("# - Refers to the instance of the object itself.")
print("# - Python passes the object as first argument to methods, bound to 'self'.")
print("# - Allows access to instance variables and methods within the class.")
print("# - Essential for instance methods.")

# Example demonstrating self parameter
print("\n# Example - Self Parameter:")
print("class Car:")
print("    def __init__(self, model_name):")
print("        self.model = model_name") # self.model is instance variable
print("    def display_model(self):")
print("        print(\"Car model is:\", self.model)") # Accessing instance variable using self

class Car:
    def __init__(self, model_name):
        self.model = model_name # self.model is instance variable

    def display_model(self):
        print("Car model is:", self.model) # Accessing instance variable using self

my_car = Car("Tesla Model S")
print("# Class 'Car' with methods using 'self' parameter.")
print("my_car.display_model()") # 'my_car' object is implicitly passed as 'self' in display_model

print("\n# Output from Self Parameter Example:")
my_car.display_model()

# 08. Class and Instance Variables
# ------------------------------------
# - Class Variables: Variables that are shared by all instances (objects) of a class. They are defined within the class but outside of any methods. Class variables are accessed using the class name or instance names.
# - Instance Variables: Variables that are unique to each instance of a class. They are defined inside methods and are owned by the specific instance of the object. Instance variables are accessed using the instance name.

print("\n# 08. Class and Instance Variables")
print("# ------------------------------------")
print("# - Class Variables: Shared among all instances, defined in class, accessed by ClassName or instance.")
print("# - Instance Variables: Unique to each instance, defined in methods (often __init__), accessed by instance name.")
print("# - Class variables for data shared across objects, instance variables for object-specific data.")

# Example of Class and Instance Variables
print("\n# Example - Class and Instance Variables:")
print("class Employee:")
print("    company_name = \"TechCorp\" # Class Variable")
print("    def __init__(self, name, employee_id):")
print("        self.name = name # Instance Variable")
print("        self.id = employee_id # Instance Variable")
print("    def display_employee(self):")
print("        print(f\"Employee: {self.name}, ID: {self.id}, Company: {Employee.company_name}\") # Accessing class variable using ClassName")

class Employee:
    company_name = "TechCorp" # Class Variable

    def __init__(self, name, employee_id):
        self.name = name # Instance Variable
        self.id = employee_id # Instance Variable

    def display_employee(self):
        print(f"Employee: {self.name}, ID: {self.id}, Company: {Employee.company_name}") # Accessing class variable using ClassName

emp1 = Employee("Alice", 101)
emp2 = Employee("Bob", 102)

print("# Class 'Employee' with class variable 'company_name' and instance variables 'name', 'id'.")
print("emp1.display_employee()")
print("emp2.display_employee()")
print("print(\"Company name accessed via ClassName:\", Employee.company_name)")
print("print(\"Company name accessed via Instance emp1:\", emp1.company_name, \"(Note: Access via instance, but it's still class variable)\")")

print("\n# Output from Class and Instance Variables:")
emp1.display_employee()
emp2.display_employee()
print("Company name accessed via ClassName:", Employee.company_name)
print("Company name accessed via Instance emp1:", emp1.company_name, "(Note: Access via instance, but it's still class variable)")

# 09. Reference Variables, Pass By Reference
# ------------------------------------
# - In Python, variables that hold objects are reference variables. They do not store the object's value directly but rather a reference (memory address) to where the object is stored in memory.
# - Python uses a mechanism often described as "pass-by-object-reference." When you pass an object to a function or assign one object variable to another, you are passing/copying references, not the actual object itself.
# - This means if you modify an object through one reference variable, the changes are reflected when accessing the same object through any other reference variable pointing to it.

print("\n# 09. Reference Variables, Pass By Reference")
print("# ------------------------------------")
print("# - Variables holding objects are reference variables (store memory address).")
print("# - Python uses 'pass-by-object-reference'.")
print("# - Passing/copying references, not objects themselves.")
print("# - Modifying object via one reference affects all references to the same object.")

# Example of Reference Variables and Pass by Reference behavior
print("\n# Example - Reference Variables and Pass By Reference:")
print("class Data:")
print("    def __init__(self, value):")
print("        self.value = value")
print("data1 = Data([1, 2, 3])")
print("data2 = data1 # data2 now references the same object as data1")
print("print(\"data1.value:\", data1.value)")
print("print(\"data2.value:\", data2.value)")
print("data2.value.append(4) # Modifying via data2")
print("print(\"After modification via data2:\")")
print("print(\"data1.value:\", data1.value, \"(data1 also reflects the change)\")")
print("print(\"data2.value:\", data2.value)")

class Data:
    def __init__(self, value):
        self.value = value

data1 = Data([1, 2, 3])
data2 = data1 # data2 now references the same object as data1

print("# Class 'Data' and example of reference variables.")
print("print(\"Initial data1.value:\", data1.value)")
print("print(\"Initial data2.value:\", data2.value)")

data2.value.append(4) # Modifying the object via data2

print("# After modification via data2:")
print("print(\"data1.value:\", data1.value, \"(data1 reflects the change)\")")
print("print(\"data2.value:\", data2.value)")

print("\n# Output from Reference Variable Example:")
print("Initial data1.value:", data1.value)
print("Initial data2.value:", data2.value)
print("After modification via data2:")
print("data1.value:", data1.value, "(data1 also reflects the change)")
print("data2.value:", data2.value)

# 10. Modify and Delete Object Properties, Objects
# ------------------------------------
# - Modify Object Properties: Object attributes can be modified after object creation by directly accessing them using dot notation and assigning a new value.
# - Delete Object Properties: Use the `del` keyword to delete an object property (attribute). `del object.attribute`.
# - Delete Objects: Use the `del` keyword to delete an entire object. `del object`. Once an object is deleted, it can no longer be accessed. Python's garbage collection will eventually reclaim the memory.

print("\n# 10. Modify and Delete Object Properties, Objects")
print("# ------------------------------------")
print("# - Modify Object Properties: Direct access via dot notation (object.attribute = new_value).")
print("# - Delete Object Properties: 'del object.attribute'.")
print("# - Delete Objects: 'del object'. Memory reclaimed by garbage collection.")

# Example of Modifying and Deleting Object Properties and Objects
print("\n# Example - Modify and Delete Object Properties, Objects:")
print("class Person:")
print("    def __init__(self, name, age):")
print("        self.name = name")
print("        self.age = age")
print("person1 = Person(\"John\", 30)")
print("print(\"Initial person1 attributes:\", person1.name, person1.age)")
print("person1.age = 31 # Modifying attribute")
print("print(\"Modified person1.age:\", person1.age)")
print("del person1.age # Deleting attribute")
print("# print(\"Trying to access deleted attribute person1.age:\", person1.age) # This would cause AttributeError")
print("del person1 # Deleting object")
print("# print(\"Trying to access deleted object person1:\", person1) # This would cause NameError")
print("print(\"Object person1 and its attribute 'age' deleted.\")")

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

person1 = Person("John", 30)
print("# Class 'Person' and demonstration of modifying/deleting object properties and objects.")
print("print(\"Initial person1 attributes:\", person1.name, person1.age)")

person1.age = 31 # Modifying object property
print("print(\"Modified person1.age:\", person1.age)")

del person1.age # Deleting object property
print("# del person1.age executed.")
# Attempting to access person1.age now would raise AttributeError
# print("print(\"Trying to access deleted attribute person1.age:\", person1.age)")

del person1 # Deleting object
print("# del person1 executed.")
# Attempting to access person1 now would raise NameError
# print("print(\"Trying to access deleted object person1:\", person1)")
print("print(\"Object person1 and its attribute 'age' deleted.\")")

print("\n# End of OOPs Fundamentals Explanation")

# 11. __slots__ for Memory Savings
# ------------------------------------
# - By default, every instance gets a __dict__ to store its attributes, which
#   costs memory and allows adding arbitrary new attributes at any time.
# - `__slots__` declares a fixed set of attribute names, so instances skip
#   __dict__ entirely - less memory per instance, and slightly faster attribute
#   access, but no dynamic attributes can be added afterward.

print("\n# 11. __slots__ for Memory Savings")
print("# ------------------------------------")
print("# - Default: each instance has a __dict__ for attributes.")
print("# - __slots__ = ('a', 'b'): fixed attributes, no __dict__, less memory.")
print("# - Tradeoff: can no longer add new attributes dynamically.")

class PointNoSlots:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class PointWithSlots:
    __slots__ = ('x', 'y') # only these attributes are allowed
    def __init__(self, x, y):
        self.x = x
        self.y = y

print("\n# Example - __slots__:")
print("class PointNoSlots:")
print("    def __init__(self, x, y): self.x, self.y = x, y")
print("class PointWithSlots:")
print("    __slots__ = ('x', 'y')")
print("    def __init__(self, x, y): self.x, self.y = x, y")

no_slots = PointNoSlots(1, 2)
with_slots = PointWithSlots(1, 2)
print("# Output:")
print("hasattr(no_slots, '__dict__'):", hasattr(no_slots, "__dict__"))
print("hasattr(with_slots, '__dict__'):", hasattr(with_slots, "__dict__"))
no_slots.z = 99 # works fine - __dict__ allows any new attribute
print("no_slots.z = 99 -> allowed:", no_slots.z)
try:
    with_slots.z = 99 # fails - 'z' is not in __slots__
except AttributeError as e:
    print("with_slots.z = 99 -> AttributeError:", e)

# 12. Class Variable Mutable-Default Gotcha
# ------------------------------------
# - A mutable object (list, dict) assigned as a class variable is ONE object
#   shared by the class and every instance - mutating it through one instance
#   mutates it for all of them, since none of them have their own copy.
# - Fix: create the mutable object inside __init__ so each instance gets its own.

print("\n# 12. Class Variable Mutable-Default Gotcha")
print("# ------------------------------------")
print("# - A list/dict as a class variable is shared by ALL instances.")
print("# - Fix: initialize mutable state inside __init__ instead.")

class ShoppingCartBuggy:
    items = [] # DANGER: one list shared by every ShoppingCartBuggy instance
    def add(self, item):
        self.items.append(item)

class ShoppingCartFixed:
    def __init__(self):
        self.items = [] # each instance gets its own list
    def add(self, item):
        self.items.append(item)

print("\n# Example - The Bug:")
print("class ShoppingCartBuggy:")
print("    items = []  # shared class variable")
print("    def add(self, item): self.items.append(item)")

cart1_buggy = ShoppingCartBuggy()
cart2_buggy = ShoppingCartBuggy()
cart1_buggy.add("apple")
print("# Output:")
print("cart1_buggy.items:", cart1_buggy.items)
print("cart2_buggy.items:", cart2_buggy.items, "(bug: cart2 sees cart1's item!)")

print("\n# Example - The Fix:")
print("class ShoppingCartFixed:")
print("    def __init__(self): self.items = []  # own list per instance")

cart1_fixed = ShoppingCartFixed()
cart2_fixed = ShoppingCartFixed()
cart1_fixed.add("apple")
print("# Output:")
print("cart1_fixed.items:", cart1_fixed.items)
print("cart2_fixed.items:", cart2_fixed.items, "(no leak)")

# 13. __new__ vs __init__
# ------------------------------------
# - `__new__(cls, ...)` is the actual object CREATOR - it allocates and returns
#   a new (unpopulated) instance. It's a staticmethod (implicitly).
# - `__init__(self, ...)` is the object INITIALIZER - it receives the instance
#   __new__ already created and sets up its attributes. It returns None.
# - `__new__` runs first, then Python calls `__init__` on the object it returned.
# - Overriding __new__ is rare - mostly used for singletons or immutable types.

print("\n# 13. __new__ vs __init__")
print("# ------------------------------------")
print("# - __new__: creates and returns the instance (runs first).")
print("# - __init__: initializes the already-created instance (runs second).")

class Singleton:
    _instance = None
    def __new__(cls, *args, **kwargs):
        print("__new__ called - creating (or reusing) the instance")
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    def __init__(self, value):
        print("__init__ called - setting value")
        self.value = value

print("\n# Example - __new__ vs __init__ (Singleton):")
print("class Singleton:")
print("    _instance = None")
print("    def __new__(cls, *args, **kwargs):")
print("        if cls._instance is None:")
print("            cls._instance = super().__new__(cls)")
print("        return cls._instance")
print("    def __init__(self, value):")
print("        self.value = value")

s1 = Singleton(1)
s2 = Singleton(2) # __new__ reuses s1's object, but __init__ still runs and overwrites value
print("# Output:")
print("s1 is s2:", s1 is s2)
print("s1.value:", s1.value, "(overwritten by second __init__ call)")

# 14. Metaclasses - A Brief Intro
# ------------------------------------
# - A class is itself an instance of something - by default, `type`.
#   `type` is the metaclass of every ordinary Python class.
# - A metaclass controls how classes themselves are CREATED, the same way a
#   class controls how instances are created.
# - You almost never need a custom metaclass - this is here for awareness,
#   not as a pattern to reach for.

print("\n# 14. Metaclasses - A Brief Intro")
print("# ------------------------------------")
print("# - type(SomeClass) is 'type' - the default metaclass of every class.")
print("# - A custom metaclass (class Meta(type)) can customize class CREATION.")

class RegularClass:
    pass

print("\n# Example - type as the default metaclass:")
print("print(type(RegularClass))  # <class 'type'>")
print("print(type(RegularClass())) # <class '__main__.RegularClass'>")
print("# Output:")
print("type(RegularClass):", type(RegularClass))
print("type(RegularClass()):", type(RegularClass()))

# A minimal custom metaclass that logs every class it creates
class LoggingMeta(type):
    def __new__(mcs, name, bases, namespace):
        print(f"LoggingMeta creating class: {name}")
        return super().__new__(mcs, name, bases, namespace)

class Widget(metaclass=LoggingMeta): # LoggingMeta.__new__ fires when this class is defined
    pass

print("\n# Example - Custom Metaclass:")
print("class LoggingMeta(type):")
print("    def __new__(mcs, name, bases, namespace):")
print("        print(f\"LoggingMeta creating class: {name}\")")
print("        return super().__new__(mcs, name, bases, namespace)")
print("class Widget(metaclass=LoggingMeta): pass")
print("# Output: (class creation message printed above, at class-definition time)")
print("type(Widget):", type(Widget))

# 15. __repr__ vs __str__ Contract
# ------------------------------------
# - __str__: for END USERS - readable, friendly. Used by print() and str().
# - __repr__: for DEVELOPERS - unambiguous. Ideally `eval(repr(obj)) == obj`,
#   i.e. it should look like valid Python that recreates the object.
# - If __str__ is missing, Python falls back to __repr__ for print()/str().
# - Every class should define __repr__; __str__ is optional (only needed if
#   you want a different, friendlier display for end users).

print("\n# 15. __repr__ vs __str__ Contract")
print("# ------------------------------------")
print("# - __str__: friendly, for end users (print(), str()).")
print("# - __repr__: unambiguous, ideally eval-able, for developers/debugging.")
print("# - No __str__ defined -> print()/str() fall back to __repr__.")

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __repr__(self):
        return f"Coordinate({self.x!r}, {self.y!r})" # looks like valid Python

class CoordinateFriendly(Coordinate):
    def __str__(self):
        return f"({self.x}, {self.y})" # friendlier display for end users

print("\n# Example - __repr__ vs __str__:")
print("class Coordinate:")
print("    def __repr__(self): return f\"Coordinate({self.x!r}, {self.y!r})\"")
print("class CoordinateFriendly(Coordinate):")
print("    def __str__(self): return f\"({self.x}, {self.y})\"")

point = Coordinate(3, 4)
friendly_point = CoordinateFriendly(3, 4)
print("# Output:")
print("repr(point):", repr(point))
print("str(point) (falls back to __repr__, no __str__ defined):", str(point))
print("str(friendly_point) (uses its own __str__):", str(friendly_point))
recreated = eval(repr(point)) # demonstrates repr is valid, eval-able Python
print("eval(repr(point)) recreates an equal object:", recreated.x == point.x and recreated.y == point.y)

