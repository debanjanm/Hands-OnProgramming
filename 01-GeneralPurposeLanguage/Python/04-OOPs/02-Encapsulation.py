## 01. Encapsulation Introduction
## 02. Instance Variables -  Private and Public
## 03. Getters and Setters 
## 04. Static vs Instance Variables
## 05. Statis Methods
## 06. Magic Methods
## 07. Aggregation

# 01. Encapsulation Introduction
# ------------------------------------
# - Encapsulation is one of the fundamental principles of OOP.
# - It is the mechanism of wrapping data (variables) and methods that operate on that data into a single unit (class).
# - Encapsulation also involves the concept of data hiding, which means preventing direct access to internal data of an object and forcing access through well-defined methods.
# - This helps in protecting the integrity of the data and simplifies the interaction with objects, reducing complexity.
# - Encapsulation promotes modularity and maintainability by keeping the internal implementation details of a class hidden from the outside world.

print("# 01. Encapsulation Introduction")
print("# ------------------------------------")
print("# - Fundamental OOP principle: wrapping data and methods into a single unit (class).")
print("# - Includes data hiding: preventing direct access, enforcing access via methods.")
print("# - Protects data integrity, simplifies interaction, reduces complexity.")
print("# - Promotes modularity and maintainability.")

# 02. Instance Variables - Private and Public
# ------------------------------------
# - Instance variables are data that is unique to each instance of a class.
# - In Python, instance variables can be conceptually treated as public or private, although Python's approach to privacy is based on convention rather than strict enforcement like in some other languages.
# - Public Instance Variables: Accessible from anywhere, both inside and outside the class. By default, instance variables in Python are considered public.
# - Private Instance Variables: Intended to be accessed only from within the class itself. Python uses a convention called name mangling to indicate private variables. To make a variable private, prefix its name with double underscores `__` (e.g., `__variable_name`). Python interpreter renames these attributes to make them harder to access directly from outside, though not impossible (name mangling is for convention, not strict privacy).

print("\n# 02. Instance Variables - Private and Public")
print("# ------------------------------------")
print("# - Instance variables: unique data for each object.")
print("# - Public (default): Accessible from anywhere.")
print("# - Private (by convention with name mangling): Intended for internal class use only.")
print("# - Name mangling for private variables: prefix with double underscores '__' (e.g., __variable).")
print("# - Python's privacy is by convention, not strict enforcement.")

# Example of Public and Private Instance Variables
print("\n# Example - Public and Private Instance Variables:")
print("class Student:")
print("    def __init__(self, name, age):")
print("        self.name = name  # Public instance variable")
print("        self.__student_id = 'ST123' # Private instance variable (name mangled)")
print("    def display_details(self):")
print("        print(f\"Name: {self.name}, Student ID: {self.__student_id}\") # Accessing private variable inside class")

class Student:
    def __init__(self, name, age):
        self.name = name  # Public instance variable
        self.__student_id = 'ST123' # Private instance variable (name mangled)

    def display_details(self):
        print(f"Name: {self.name}, Student ID: {self.__student_id}") # Accessing private variable inside class

student1 = Student("Alice", 20)
print("# Class 'Student' with public 'name' and private '__student_id'.")
print("print(\"Accessing public variable student1.name:\", student1.name)")
print("student1.display_details()")
print("# print(\"Trying to access private variable student1.__student_id directly:\", student1.__student_id) # This would cause AttributeError due to name mangling")
print("# To access name-mangled variable (for demonstration, not recommended practice): print(\"Accessing name-mangled variable student1._Student__student_id:\", student1._Student__student_id)") # Demonstrating name mangling access

print("\n# Output from Public and Private Instance Variables:")
print("Accessing public variable student1.name:", student1.name)
student1.display_details()
# print("Trying to access private variable student1.__student_id directly:", student1.__student_id) # Uncommenting would cause AttributeError
print("Accessing name-mangled variable student1._Student__student_id:", student1._Student__student_id)

# 03. Getters and Setters
# ------------------------------------
# - Getters (accessors) and Setters (mutators) are methods used to control access to instance variables, especially private ones.
# - Getters: Methods used to retrieve the value of a private instance variable. Conventionally named `get_variable_name` or in Python, often implemented using `@property` decorator for more Pythonic access like attribute.
# - Setters: Methods used to modify the value of a private instance variable. They can include validation logic to ensure data integrity. Conventionally named `set_variable_name` or in Python, using `@variable_name.setter` decorator.
# - Using getters and setters provides controlled access to attributes, allowing for validation, computed attributes, and more, while maintaining encapsulation.

print("\n# 03. Getters and Setters")
print("# ------------------------------------")
print("# - Methods to control access to instance variables (especially private).")
print("# - Getters (accessors): Retrieve value of private variable (e.g., get_variable or @property).")
print("# - Setters (mutators): Modify value of private variable, can include validation (e.g., set_variable or @variable.setter).")
print("# - Provide controlled attribute access, enabling validation, computed attributes, encapsulation.")

# Example of Getters and Setters using Property Decorators (Pythonic approach)
print("\n# Example - Getters and Setters using Property Decorators:")
print("class Product:")
print("    def __init__(self, price):")
print("        self.__price = price # Private variable")
print("    @property")
print("    def price(self): # Getter for price")
print("        return self.__price")
print("    @price.setter")
print("    def price(self, value): # Setter for price with validation")
print("        if value < 0:")
print("            raise ValueError(\"Price cannot be negative\")")
print("        self.__price = value")

class Product:
    def __init__(self, price):
        self.__price = price # Private variable

    @property
    def price(self): # Getter for price
        return self.__price

    @price.setter
    def price(self, value): # Setter for price with validation
        if value < 0:
            raise ValueError("Price cannot be negative")
        self.__price = value

product1 = Product(100)
print("# Class 'Product' with private '__price', getter '@property price', setter '@price.setter'.")
print("print(\"Initial product1.price (using getter):\", product1.price)")
print("product1.price = 120 # Using setter to modify price")
print("print(\"Modified product1.price (using getter):\", product1.price)")
print("# product1.price = -10 # This would raise ValueError due to setter validation")

print("\n# Output from Getters and Setters:")
print("Initial product1.price (using getter):", product1.price)
product1.price = 120 # Using setter to modify price
print("Modified product1.price (using getter):", product1.price)
# product1.price = -10 # Uncommenting would raise ValueError

# 04. Static vs Instance Variables
# ------------------------------------
# - Instance Variables (covered in #02): Belong to the instance of the class. Each object has its own copy. Changes to an instance variable of one object do not affect other objects or the class itself.
# - Static Variables (Class Variables): Belong to the class itself. They are shared by all instances of the class. Changes to a class variable affect all instances of the class and are reflected class-wide. Defined within the class, outside of any method, and are typically accessed using the class name (though instances can also access them).
# - Use Instance variables when each object needs its own unique data.
# - Use Static (Class) variables when you want data to be shared among all objects of the class and/or keep track of class-level information (e.g., count of objects created, default values).

print("\n# 04. Static vs Instance Variables")
print("# ------------------------------------")
print("# - Instance Variables: Unique per object, each object has its own copy, changes are object-specific.")
print("# - Static Variables (Class Variables): Shared by all objects, belong to class, changes are class-wide.")
print("# - Instance Variables use case: unique object data.")
print("# - Static (Class) Variables use case: shared data, class-level info (counts, defaults).")

# Example of Static vs Instance Variables
print("\n# Example - Static vs Instance Variables:")
print("class Vehicle:")
print("    wheels = 4 # Static/Class variable (shared by all Vehicle instances)")
print("    vehicle_count = 0 # Static/Class variable to count instances")
print("    def __init__(self, model_name):")
print("        self.model_name = model_name # Instance variable (unique to each vehicle)")
print("        Vehicle.vehicle_count += 1 # Incrementing class variable on each instance creation")
print("    def display_vehicle_info(self):")
print("        print(f\"Model: {self.model_name}, Wheels: {Vehicle.wheels}, Total Vehicles: {Vehicle.vehicle_count}\")") # Accessing class variable via ClassName

class Vehicle:
    wheels = 4 # Static/Class variable (shared by all Vehicle instances)
    vehicle_count = 0 # Static/Class variable to count instances

    def __init__(self, model_name):
        self.model_name = model_name # Instance variable (unique to each vehicle)
        Vehicle.vehicle_count += 1 # Incrementing class variable on each instance creation

    def display_vehicle_info(self):
        print(f"Model: {self.model_name}, Wheels: {Vehicle.wheels}, Total Vehicles: {Vehicle.vehicle_count}") # Accessing class variable via ClassName

vehicle1 = Vehicle("Car")
vehicle2 = Vehicle("Bike")

print("# Class 'Vehicle' with static variable 'wheels' and 'vehicle_count', instance variable 'model_name'.")
print("vehicle1.display_vehicle_info()")
print("vehicle2.display_vehicle_info()")
print("print(\"Vehicle.wheels (class variable):\", Vehicle.wheels)")
print("print(\"vehicle1.wheels (instance access to class variable):\", vehicle1.wheels)")
print("print(\"Vehicle.vehicle_count (class variable):\", Vehicle.vehicle_count)")

print("\n# Output from Static vs Instance Variables:")
vehicle1.display_vehicle_info()
vehicle2.display_vehicle_info()
print("Vehicle.wheels (class variable):", Vehicle.wheels)
print("vehicle1.wheels (instance access to class variable):", vehicle1.wheels)
print("Vehicle.vehicle_count (class variable):", Vehicle.vehicle_count)

# 05. Static Methods
# ------------------------------------
# - Static methods are methods that belong to the class itself, not to any specific instance.
# - They are defined using the `@staticmethod` decorator.
# - Static methods do not receive the instance as an implicit first argument (no `self` parameter). They also do not receive class as implicit first argument (unlike classmethods).
# - Static methods are typically used for utility functions that are related to the class conceptually, but do not need to access instance-specific or class-specific data directly. They operate on parameters passed explicitly to them.
# - They can be called on the class itself `ClassName.static_method()` or on an instance `instance.static_method()`, but are generally intended to be class-level utilities.

print("\n# 05. Static Methods")
print("# ------------------------------------")
print("# - Methods belonging to the class, not instance-specific.")
print("# - Defined using @staticmethod decorator.")
print("# - No implicit 'self' or 'cls' parameter.")
print("# - Used for utility functions related to the class conceptually, but not needing instance or class state.")
print("# - Called on class (ClassName.static_method()) or instance (instance.static_method()).")

# Example of Static Methods
print("\n# Example - Static Methods:")
print("class MathUtils:")
print("    @staticmethod")
print("    def add(x, y): # Static method - no 'self' parameter")
print("        return x + y")
print("    @staticmethod")
print("    def is_positive(number): # Another static method")
print("        return number > 0")

class MathUtils:
    @staticmethod
    def add(x, y): # Static method - no 'self' parameter
        return x + y

    @staticmethod
    def is_positive(number): # Another static method
        return number > 0

print("# Class 'MathUtils' with static methods 'add' and 'is_positive'.")
print("print(\"MathUtils.add(5, 3) (calling static method on class):\", MathUtils.add(5, 3))")
print("print(\"MathUtils.is_positive(-1) (calling static method on class):\", MathUtils.is_positive(-1))")

print("\n# Output from Static Methods:")
print("MathUtils.add(5, 3) (calling static method on class):", MathUtils.add(5, 3))
print("MathUtils.is_positive(-1) (calling static method on class):", MathUtils.is_positive(-1))

# 06. Magic Methods (in context of Encapsulation/Class behavior)
# ------------------------------------
# - Magic methods related to encapsulation and class behavior often involve controlling attribute access and object lifecycle.
# - `__getattr__(self, name)`: Called when attribute lookup fails for the attribute `name`. Can be used to provide default values, compute attributes dynamically, or raise AttributeError.
# - `__setattr__(self, name, value)`: Called when an attribute assignment is attempted. Allows control over setting attribute values, can be used for validation or to prevent attribute creation.
# - `__delattr__(self, name)`: Called when attribute deletion is attempted. Can control or prevent deletion of attributes.
# - These magic methods allow for powerful control over how attributes of a class are accessed, set, and deleted, directly supporting encapsulation principles by managing data access and modification.

print("\n# 06. Magic Methods (in context of Encapsulation/Class behavior)")
print("# ------------------------------------")
print("# - Magic methods for controlling attribute access and object behavior (encapsulation).")
print("# - __getattr__(self, name): Called on attribute access failure, can provide defaults, dynamic attributes.")
print("# - __setattr__(self, name, value): Called on attribute assignment, control setting, validation.")
print("# - __delattr__(self, name): Called on attribute deletion, control/prevent deletion.")
print("# - Enable powerful attribute access control, supporting encapsulation.")

# Example using __getattr__, __setattr__ for attribute access control
print("\n# Example - Magic Methods __getattr__, __setattr__:")
print("class SmartObject:")
print("    def __init__(self, **kwargs):")
print("        self.__data = kwargs # Using a private dict to store attributes")
print("    def __getattr__(self, name): # Called when attribute not found")
print("        print(f\"__getattr__ called for attribute: {name}\")")
print("        return self.__data.get(name, None) # Return from internal data or None if not found")
print("    def __setattr__(self, name, value): # Called on attribute assignment")
print("        if name == '_SmartObject__data': # Allow setting of __data (for initialization)")
print("            super().__setattr__(name, value) # Use default behavior for __data")
print("        else:")
print("            print(f\"__setattr__ called for attribute: {name} with value: {value}\")")
print("            self.__data[name] = value # Store in internal data")

class SmartObject:
    def __init__(self, **kwargs):
        self.__data = kwargs # Using a private dict to store attributes

    def __getattr__(self, name): # Called when attribute not found
        print(f"__getattr__ called for attribute: {name}")
        return self.__data.get(name, None) # Return from internal data or None if not found

    def __setattr__(self, name, value): # Called on attribute assignment
        if name == '_SmartObject__data': # Allow setting of __data (for initialization)
            super().__setattr__(name, value) # Use default behavior for __data
        else:
            print(f"__setattr__ called for attribute: {name} with value: {value}")
            self.__data[name] = value # Store in internal data

smart_obj = SmartObject(initial_value=100)
print("# Class 'SmartObject' using __getattr__ and __setattr__ for attribute control.")
print("smart_obj.new_attribute = 200 # Assignment triggers __setattr__")
print("print(\"smart_obj.new_attribute (access triggers __getattr__ if not directly set):\", smart_obj.new_attribute)")
print("print(\"smart_obj.initial_value (access triggers __getattr__ if not directly set):\", smart_obj.initial_value)")
print("print(\"smart_obj.non_existent_attribute (access triggers __getattr__):\", smart_obj.non_existent_attribute)")

print("\n# Output from Magic Methods __getattr__, __setattr__ Example:")
smart_obj.new_attribute = 200 # Assignment triggers __setattr__
print("smart_obj.new_attribute (access triggers __getattr__ if not directly set):", smart_obj.new_attribute)
print("smart_obj.initial_value (access triggers __getattr__ if not directly set):", smart_obj.initial_value)
print("smart_obj.non_existent_attribute (access triggers __getattr__):", smart_obj.non_existent_attribute)

# 07. Aggregation
# ------------------------------------
# - Aggregation is a type of association between classes where one class (the 'whole' or composite class) contains instances of another class (the 'part' or component class).
# - In aggregation, the 'part' class instances can exist independently of the 'whole' class. It's a "has-a" relationship.
# - For example, a 'Department' may have 'Employees'. If the department is closed down, employees can still exist independently (work in another department or company). This is aggregation, not composition (where parts are strongly owned by the whole and can't exist independently).
# - Aggregation emphasizes a weaker form of relationship compared to composition.

print("\n# 07. Aggregation")
print("# ------------------------------------")
print("# - Association where one class ('whole') contains instances of another ('part').")
print("# - 'Part' class instances can exist independently of the 'whole' class (weaker relationship).")
print("# - 'Has-a' relationship. E.g., Department has-a Employee, but Employee can exist without the Department.")
print("# - Weaker form of relationship than composition.")

# Example of Aggregation
print("\n# Example - Aggregation:")
print("class Address:")
print("    def __init__(self, street, city):")
print("        self.street = street")
print("        self.city = city")
print("    def __str__(self):")
print("        return f\"{self.street}, {self.city}\"")
print("class EmployeeAgg:") # Renamed to avoid conflict with previous Employee class
print("    def __init__(self, name, address):")
print("        self.name = name")
print("        self.address = address # Aggregation: Employee 'has-a' Address")
print("    def display_info(self):")
print("        print(f\"Employee: {self.name}, Address: {self.address}\")") # Address is an object of Address class

class Address:
    def __init__(self, street, city):
        self.street = street
        self.city = city

    def __str__(self):
        return f"{self.street}, {self.city}"

class EmployeeAgg: # Renamed to avoid conflict with previous Employee class
    def __init__(self, name, address):
        self.name = name
        self.address = address # Aggregation: Employee 'has-a' Address

    def display_info(self):
        print(f"Employee: {self.name}, Address: {self.address}") # Address is an object of Address class

address1 = Address("123 Main St", "Cityville") # Address object created independently
employee_agg1 = EmployeeAgg("Eve", address1) # Employee aggregates Address object

print("# Classes 'Address' and 'EmployeeAgg' demonstrating aggregation.")
print("employee_agg1.display_info()")
print("print(\"Address object can exist independently:\", address1)")

print("\n# Output from Aggregation Example:")
employee_agg1.display_info()
print("Address object can exist independently:", address1)

print("\n# End of Encapsulation and Related OOP Concepts Explanation")

# 08. Name Mangling Internals
# ------------------------------------
# - A `__name` attribute (two leading underscores, at most one trailing) gets
#   automatically rewritten by Python to `_ClassName__name` wherever it's
#   referenced inside the class body. This is called name mangling.
# - It exists to avoid accidental name clashes in subclasses, NOT to make an
#   attribute truly private - the mangled name is still visible in __dict__
#   and still accessible from outside if you know the mangled form.

print("\n# 08. Name Mangling Internals")
print("# ------------------------------------")
print("# - __attr inside a class body is rewritten to _ClassName__attr.")
print("# - Purpose: avoid subclass name clashes, not true privacy.")
print("# - Still visible via vars()/__dict__ and accessible via the mangled name.")

class Account:
    def __init__(self, balance):
        self.__balance = balance # becomes _Account__balance

print("\n# Example - Name Mangling:")
print("class Account:")
print("    def __init__(self, balance):")
print("        self.__balance = balance  # becomes _Account__balance")

acc = Account(500)
print("# Output:")
print("vars(acc):", vars(acc))
print("acc._Account__balance (mangled name still works):", acc._Account__balance)
try:
    print(acc.__balance) # AttributeError - '__balance' unmangled doesn't exist
except AttributeError as e:
    print("acc.__balance -> AttributeError:", e)

# 09. Property with Computed Value + Caching (functools.cached_property)
# ------------------------------------
# - A regular @property recomputes its value on every access.
# - @functools.cached_property computes it once, on first access, then stores
#   the result in the instance's __dict__ - later accesses skip recomputation.
# - Only makes sense for values that don't change after the first computation
#   (or where staleness is acceptable) - the instance must NOT use __slots__
#   without also slotting for the cache attribute.

print("\n# 09. Property with Caching (functools.cached_property)")
print("# ------------------------------------")
print("# - @property: recomputes on every access.")
print("# - @functools.cached_property: computes once, caches in instance __dict__.")

from functools import cached_property

class Report:
    def __init__(self, numbers):
        self.numbers = numbers
    @cached_property
    def expensive_total(self):
        print("(computing expensive_total...)")
        return sum(self.numbers)

print("\n# Example - cached_property:")
print("class Report:")
print("    def __init__(self, numbers): self.numbers = numbers")
print("    @cached_property")
print("    def expensive_total(self):")
print("        print(\"(computing...)\")")
print("        return sum(self.numbers)")

report = Report([1, 2, 3, 4, 5])
print("# Output:")
print("First access:", report.expensive_total)   # prints "(computing...)" then the value
print("Second access:", report.expensive_total)  # no recomputation - served from cache

# 10. The "Pythonic" Philosophy of Encapsulation
# ------------------------------------
# - Python trusts developers: "we're all consenting adults here."
# - A single underscore `_attr` is a CONVENTION meaning "internal, please
#   don't touch from outside" - it is not enforced by the language at all.
# - Double underscore `__attr` only adds name mangling (see #08) - it deters
#   accidental access, not deliberate access.
# - Contrast with languages like Java/C++ where `private` is enforced by the
#   compiler - Python leaves the choice (and responsibility) with the caller.

print("\n# 10. The 'Pythonic' Philosophy of Encapsulation")
print("# ------------------------------------")
print("# - 'We're all consenting adults here' - privacy is convention, not enforcement.")
print("# - _attr: 'internal, please don't touch' - a hint, not a lock.")
print("# - __attr: name-mangled, harder to reach by accident, still reachable on purpose.")

class BankAccount:
    def __init__(self, balance):
        self._balance = balance # single underscore: 'internal use' convention

print("\n# Example - Convention, Not Enforcement:")
print("class BankAccount:")
print("    def __init__(self, balance): self._balance = balance")

account = BankAccount(1000)
print("# Output:")
print("account._balance (nothing stops direct access):", account._balance)
account._balance = 999999 # nothing in the language prevents this either
print("account._balance after direct external mutation:", account._balance)
print("# - Python trusts you to respect the underscore, it won't stop you.")

# 11. __slots__ Interaction with Properties
# ------------------------------------
# - __slots__ removes __dict__, so a plain `self.x = x` assignment for a slot
#   name works fine - slots create data descriptors that store the value in a
#   fixed per-instance slot instead of a dict entry.
# - Properties still work normally alongside __slots__, but the property's
#   backing attribute (e.g. `_radius`) must ALSO be listed in __slots__, since
#   there's no __dict__ left to fall back on for storage.

print("\n# 11. __slots__ Interaction with Properties")
print("# ------------------------------------")
print("# - __slots__ + @property both work together.")
print("# - The property's backing attribute must be included in __slots__ too.")

class CircleSlotted:
    __slots__ = ('_radius',) # must include the backing attribute used by the property
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

print("\n# Example - __slots__ with @property:")
print("class CircleSlotted:")
print("    __slots__ = ('_radius',)")
print("    @property")
print("    def radius(self): return self._radius")
print("    @radius.setter")
print("    def radius(self, value): self._radius = value")

circle = CircleSlotted(5)
circle.radius = 10 # goes through the setter, stored in the slotted _radius
print("# Output:")
print("circle.radius:", circle.radius)
try:
    circle.extra = 1 # fails - 'extra' is not in __slots__, no __dict__ to fall back on
except AttributeError as e:
    print("circle.extra = 1 -> AttributeError:", e)

