## 01. Inheritance Introduction
## 02. DRY - Dont Repeat Yourself
## 03. What Gets Inherited?
## 04. Method Overriding
## 05. Super Keyword
## 06. Types Of Inheritance with Examples - Single, Multi-Level, Hierarchical, Multiple (Method Resolution Order), Hybdrid

# 01. Inheritance Introduction
# ------------------------------------
# - Inheritance is a fundamental principle in OOP that allows a class (child/derived class) to inherit properties and behaviors from another class (parent/base class).
# - It promotes code reusability and establishes an "is-a" relationship between classes. For example, a 'Dog' is a type of 'Animal'.
# - The derived class can inherit attributes and methods from the base class, and can also add new attributes and methods or modify inherited ones.
# - Inheritance forms a hierarchy of classes, making code organized and easier to extend and maintain.

print("# 01. Inheritance Introduction")
print("# ------------------------------------")
print("# - OOP principle allowing a class (child/derived) to inherit from another (parent/base).")
print("# - Promotes code reusability and 'is-a' relationship (e.g., Dog is-a Animal).")
print("# - Derived class inherits attributes and methods, can add new or modify inherited ones.")
print("# - Forms class hierarchies, improves organization, extensibility, and maintenance.")

# 02. DRY - Don't Repeat Yourself
# ------------------------------------
# - DRY (Don't Repeat Yourself) is a principle of software development aimed at reducing repetition of software patterns, replacing it with abstractions or data normalization to avoid redundancy.
# - Inheritance directly supports the DRY principle by allowing you to define common attributes and methods in a base class and reuse them in multiple derived classes.
# - Instead of rewriting the same code in different classes, you inherit the common parts, and only implement the specific functionalities in each derived class.
# - This reduces code length, improves maintainability (changes to common logic only need to be made in one place - the base class), and reduces the chance of errors due to inconsistencies in duplicated code.

print("\n# 02. DRY - Don't Repeat Yourself")
print("# ------------------------------------")
print("# - Principle to reduce repetition in code, using abstractions instead.")
print("# - Inheritance directly supports DRY by reusing base class code in derived classes.")
print("# - Common attributes/methods defined once in base class, reused in derived classes.")
print("# - Reduces code, improves maintainability (single point of change), minimizes errors.")

# 03. What Gets Inherited?
# ------------------------------------
# - When a class inherits from a base class, it inherits:
#   - Public and protected members (attributes and methods) of the base class.
#   - Private members of the base class are technically inherited but are not directly accessible or modifiable in the derived class (due to name mangling in Python). However, they exist in the object instance of the derived class.
# - The derived class does not inherit:
#   - Constructors (`__init__` methods) of the base class are not automatically inherited in the sense of being directly called when a derived class object is created. However, you can explicitly call the base class constructor using `super().__init__()` in the derived class's constructor.

print("\n# 03. What Gets Inherited?")
print("# ------------------------------------")
print("# - Derived class inherits:")
print("#   - Public and protected members (attributes and methods).")
print("#   - Private members (technically inherited but not directly accessible/modifiable due to name mangling).")
print("# - Derived class does not automatically inherit:")
print("#   - Constructors (__init__ methods). Need to be explicitly called using super().__init__().")

# 04. Method Overriding
# ------------------------------------
# - Method overriding is a feature in OOP where a derived class provides a specific implementation for a method that is already defined in its base class.
# - When a method in a derived class has the same name, same parameters, or signature as a method in its base class, then the derived class's method is said to override the base class's method.
# - When you call an overridden method on an object of the derived class, the method in the derived class is executed, not the method from the base class.
# - Method overriding allows a derived class to extend or customize the behavior inherited from a base class.

print("\n# 04. Method Overriding")
print("# ------------------------------------")
print("# - Derived class provides specific implementation for a method already in base class.")
print("# - Same method name, same signature in derived class overrides base class method.")
print("# - Calling overridden method on derived class object executes derived class's method.")
print("# - Allows customization and extension of base class behavior in derived classes.")

# Example of Method Overriding
print("\n# Example - Method Overriding:")
print("class Animal:")
print("    def speak(self):")
print("        print(\"Generic animal sound\")")
print("class Dog(Animal):")
print("    def speak(self): # Method overriding")
print("        print(\"Woof!\")")

class Animal:
    def speak(self):
        print("Generic animal sound")

class Dog(Animal):
    def speak(self): # Method overriding
        print("Woof!")

animal = Animal()
dog = Dog()

print("# Class 'Animal' with method 'speak', class 'Dog' inheriting and overriding 'speak'.")
print("print(\"animal.speak():\")")
animal.speak() # Calls Animal's speak method
print("print(\"dog.speak():\")")
dog.speak() # Calls Dog's overridden speak method

print("\n# Output from Method Overriding Example:")
print("animal.speak():")
animal.speak()
print("dog.speak():")
dog.speak()

# 05. Super Keyword
# ------------------------------------
# - The `super()` keyword in Python is used to call a method from a parent class within a derived class.
# - It is commonly used in method overriding to extend the functionality of a base class method, rather than completely replacing it.
# - `super()` returns a temporary object of the superclass, allowing you to call superclass methods directly from the subclass.
# - It is especially useful in constructors (`__init__` methods) of derived classes to invoke the constructor of the base class to initialize inherited attributes.

print("\n# 05. Super Keyword")
print("# ------------------------------------")
print("# - Used in derived class to call methods from parent class.")
print("# - Commonly used in method overriding to extend base class functionality.")
print("# - super() returns temporary object of superclass to call its methods.")
print("# - Useful in __init__ of derived class to invoke base class's constructor.")

# Example of Super Keyword
print("\n# Example - Super Keyword:")
print("class Parent:")
print("    def __init__(self, name):")
print("        self.name = name")
print("        print(\"Parent __init__ called\")")
print("    def display_info(self):")
print("        print(f\"Parent name: {self.name}\")")
print("class Child(Parent):")
print("    def __init__(self, name, child_age):")
print("        super().__init__(name) # Calling Parent's __init__")
print("        self.age = child_age")
print("        print(\"Child __init__ called\")")
print("    def display_info(self):")
print("        super().display_info() # Calling Parent's display_info")
print("        print(f\"Child age: {self.age}\")")

class Parent:
    def __init__(self, name):
        self.name = name
        print("Parent __init__ called")

    def display_info(self):
        print(f"Parent name: {self.name}")

class Child(Parent):
    def __init__(self, name, child_age):
        super().__init__(name) # Calling Parent's __init__
        self.age = child_age
        print("Child __init__ called")

    def display_info(self):
        super().display_info() # Calling Parent's display_info
        print(f"Child age: {self.age}")

child = Child("Alice", 10)

print("# Classes 'Parent' and 'Child' demonstrating 'super()' to call parent methods.")
print("print(\"child.display_info():\")")
child.display_info()

print("\n# Output from Super Keyword Example:")
print("child.display_info():")
child.display_info()

# 06. Types Of Inheritance with Examples
# ------------------------------------
print("\n# 06. Types Of Inheritance with Examples")
print("# ------------------------------------")

# a) Single Inheritance
print("\n# a) Single Inheritance")
print("# - A derived class inherits from only a single base class.")
print("# - Simplest form of inheritance.")

print("\n# Example - Single Inheritance:")
print("class Shape:")
print("    def area(self):")
print("        return \"Area of shape\"")
print("class Circle(Shape): # Single inheritance from Shape")
print("    def __init__(self, radius):")
print("        self.radius = radius")
print("    def area(self): # Overriding area method")
print("        return 3.14 * self.radius * self.radius")

class Shape:
    def area(self):
        return "Area of shape"

class Circle(Shape): # Single inheritance from Shape
    def __init__(self, radius):
        self.radius = radius

    def area(self): # Overriding area method
        return 3.14 * self.radius * self.radius

circle = Circle(5)
print("# Single inheritance: Circle inherits from Shape.")
print("print(\"circle.area():\", circle.area())")
print("print(\"Is circle instance of Shape?:\", isinstance(circle, Shape))")

print("\n# Output from Single Inheritance Example:")
print("circle.area():", circle.area())
print("Is circle instance of Shape?:", isinstance(circle, Shape))

# b) Multi-Level Inheritance
print("\n# b) Multi-Level Inheritance")
print("# - A derived class inherits from a base class, and then another class inherits from this derived class.")
print("# - Forms a chain of inheritance.")

print("\n# Example - Multi-Level Inheritance:")
print("class Vehicle:")
print("    def start(self):")
print("        return \"Vehicle started\"")
print("class Car(Vehicle): # Inherits from Vehicle")
print("    def accelerate(self):")
print("        return \"Car accelerating\"")
print("class SportsCar(Car): # Inherits from Car (which inherited from Vehicle)")
print("    def top_speed(self):")
print("        return \"Sports car top speed\"")

class Vehicle:
    def start(self):
        return "Vehicle started"

class Car(Vehicle): # Inherits from Vehicle
    def accelerate(self):
        return "Car accelerating"

class SportsCar(Car): # Inherits from Car (which inherited from Vehicle)
    def top_speed(self):
        return "Sports car top speed"

sportscar = SportsCar()
print("# Multi-level inheritance: SportsCar -> Car -> Vehicle.")
print("print(\"sportscar.start():\", sportscar.start())") # Inherited from Vehicle
print("print(\"sportscar.accelerate():\", sportscar.accelerate())") # Inherited from Car
print("print(\"sportscar.top_speed():\", sportscar.top_speed())") # Defined in SportsCar
print("print(\"Is sportscar instance of Vehicle?:\", isinstance(sportscar, Vehicle))")
print("print(\"Is sportscar instance of Car?:\", isinstance(sportscar, Car))")

print("\n# Output from Multi-Level Inheritance Example:")
print("sportscar.start():", sportscar.start())
print("sportscar.accelerate():", sportscar.accelerate())
print("sportscar.top_speed():", sportscar.top_speed())
print("Is sportscar instance of Vehicle?:", isinstance(sportscar, Vehicle))
print("Is sportscar instance of Car?:", isinstance(sportscar, Car))

# c) Hierarchical Inheritance
print("\n# c) Hierarchical Inheritance")
print("# - Multiple derived classes inherit from a single base class.")
print("# - Forms a tree-like structure of classes.")

print("\n# Example - Hierarchical Inheritance:")
print("class Animal:")
print("    def eat(self):")
print("        return \"Animal eating\"")
print("class Dog(Animal): # Inherits from Animal")
print("    def bark(self):")
print("        return \"Woof!\"")
print("class Cat(Animal): # Inherits from Animal")
print("    def meow(self):")
print("        return \"Meow!\"")

class Animal:
    def eat(self):
        return "Animal eating"

class Dog(Animal): # Inherits from Animal
    def bark(self):
        return "Woof!"

class Cat(Animal): # Inherits from Animal
    def meow(self):
        return "Meow!"

dog_hierarchical = Dog()
cat_hierarchical = Cat()

print("# Hierarchical inheritance: Dog and Cat inherit from Animal.")
print("print(\"dog_hierarchical.eat():\", dog_hierarchical.eat())") # Inherited from Animal
print("print(\"dog_hierarchical.bark():\", dog_hierarchical.bark())") # Defined in Dog
print("print(\"cat_hierarchical.eat():\", cat_hierarchical.eat())") # Inherited from Animal
print("print(\"cat_hierarchical.meow():\", cat_hierarchical.meow())") # Defined in Cat
print("print(\"Is dog_hierarchical instance of Animal?:\", isinstance(dog_hierarchical, Animal))")
print("print(\"Is cat_hierarchical instance of Animal?:\", isinstance(cat_hierarchical, Animal))")

print("\n# Output from Hierarchical Inheritance Example:")
print("dog_hierarchical.eat():", dog_hierarchical.eat())
print("dog_hierarchical.bark():", dog_hierarchical.bark())
print("cat_hierarchical.eat():", cat_hierarchical.eat())
print("cat_hierarchical.meow():", cat_hierarchical.meow())
print("Is dog_hierarchical instance of Animal?:", isinstance(dog_hierarchical, Animal))
print("Is cat_hierarchical instance of Animal?:", isinstance(cat_hierarchical, Animal))

# d) Multiple Inheritance (and Method Resolution Order - MRO)
print("\n# d) Multiple Inheritance (and Method Resolution Order - MRO)")
print("# - A derived class inherits from more than one base class.")
print("# - Python supports multiple inheritance.")
print("# - Method Resolution Order (MRO) determines the order in which base classes are searched when a method is called.")
print("# - Python uses C3 linearization algorithm to calculate MRO.")

print("\n# Example - Multiple Inheritance and MRO:")
print("class Flyer:")
print("    def fly(self):")
print("        return \"Can fly\"")
print("class Swimmer:")
print("    def swim(self):")
print("        return \"Can swim\"")
print("class Duck(Flyer, Swimmer): # Multiple inheritance from Flyer and Swimmer")
print("    def quack(self):")
print("        return \"Quack!\"")

class Flyer:
    def fly(self):
        return "Can fly"

class Swimmer:
    def swim(self):
        return "Can swim"

class Duck(Flyer, Swimmer): # Multiple inheritance from Flyer and Swimmer
    def quack(self):
        return "Quack!"

duck_multi = Duck()

print("# Multiple inheritance: Duck inherits from Flyer and Swimmer.")
print("print(\"duck_multi.fly():\", duck_multi.fly())") # Inherited from Flyer
print("print(\"duck_multi.swim():\", duck_multi.swim())") # Inherited from Swimmer
print("print(\"duck_multi.quack():\", duck_multi.quack())") # Defined in Duck
print("print(\"Duck.__mro__ (Method Resolution Order):\", Duck.__mro__)") # Display MRO

print("\n# Output from Multiple Inheritance Example:")
print("duck_multi.fly():", duck_multi.fly())
print("duck_multi.swim():", duck_multi.swim())
print("duck_multi.quack():", duck_multi.quack())
print("Duck.__mro__ (Method Resolution Order):", Duck.__mro__) # Shows the tuple MRO order

# e) Hybrid Inheritance
print("\n# e) Hybrid Inheritance")
print("# - Combination of more than one type of inheritance.")
print("# - For example, combining multi-level and multiple inheritance.")

print("\n# Example - Hybrid Inheritance (Combination of Hierarchical and Multiple):")
print("class Engine:")
print("    def start_engine(self):")
print("        return \"Engine started\"")
print("class ElectricEngine(Engine): # Multi-level inheritance from Engine")
print("    def power_source(self):")
print("        return \"Electric power\"")
print("class FuelEngine(Engine): # Another branch in hierarchical inheritance from Engine")
print("    def fuel_type(self):")
print("        return \"Fossil fuel\"")
print("class HybridCar(ElectricEngine, FuelEngine): # Multiple inheritance from ElectricEngine and FuelEngine")
print("    def drive(self):")
print("        return \"Driving in hybrid mode\"")

class Engine:
    def start_engine(self):
        return "Engine started"

class ElectricEngine(Engine): # Multi-level inheritance from Engine
    def power_source(self):
        return "Electric power"

class FuelEngine(Engine): # Another branch in hierarchical inheritance from Engine
    def fuel_type(self):
        return "Fossil fuel"

class HybridCar(ElectricEngine, FuelEngine): # Multiple inheritance from ElectricEngine and FuelEngine
    def drive(self):
        return "Driving in hybrid mode"

hybrid_car = HybridCar()

print("# Hybrid inheritance: HybridCar combines ElectricEngine and FuelEngine, both derived from Engine.")
print("print(\"hybrid_car.start_engine():\", hybrid_car.start_engine())") # Inherited from Engine (via ElectricEngine and FuelEngine)
print("print(\"hybrid_car.power_source():\", hybrid_car.power_source())") # Inherited from ElectricEngine
print("print(\"hybrid_car.fuel_type():\", hybrid_car.fuel_type())") # Inherited from FuelEngine
print("print(\"hybrid_car.drive():\", hybrid_car.drive())") # Defined in HybridCar
print("print(\"HybridCar.__mro__ (Method Resolution Order):\", HybridCar.__mro__)") # Display MRO

print("\n# Output from Hybrid Inheritance Example:")
print("hybrid_car.start_engine():", hybrid_car.start_engine())
print("hybrid_car.power_source():", hybrid_car.power_source())
print("hybrid_car.fuel_type():", hybrid_car.fuel_type())
print("hybrid_car.drive():", hybrid_car.drive())
print("HybridCar.__mro__ (Method Resolution Order):", HybridCar.__mro__)

print("\n# End of Inheritance Explanation and Examples")

# 07. Method Resolution Order (MRO) and C3 Linearization
# ------------------------------------
# - MRO is the order Python searches base classes when looking up a method
#   or attribute. `ClassName.__mro__` (or `ClassName.mro()`) shows that order.
# - Python computes MRO using the C3 linearization algorithm: a class always
#   comes before its parents, and parents keep the left-to-right order they
#   were listed in at the class definition - a consistent, predictable rule
#   that also detects impossible orderings and raises TypeError.

print("\n# 07. Method Resolution Order (MRO) and C3 Linearization")
print("# ------------------------------------")
print("# - ClassName.__mro__ shows the exact search order for methods/attributes.")
print("# - C3 linearization: a class before its parents, parents in listed order.")

class Base:
    def greet(self):
        return "Base greet"

class Left(Base):
    def greet(self):
        return "Left greet"

class Right(Base):
    def greet(self):
        return "Right greet"

class Bottom(Left, Right):
    pass

print("\n# Example - MRO:")
print("class Base: ...")
print("class Left(Base): ...")
print("class Right(Base): ...")
print("class Bottom(Left, Right): pass")

bottom = Bottom()
print("# Output:")
print("bottom.greet():", bottom.greet()) # Left comes first in Bottom's bases
print("Bottom.__mro__:", Bottom.__mro__) # Bottom -> Left -> Right -> Base -> object

# 08. The Diamond Problem and Cooperative super()
# ------------------------------------
# - The "diamond": two classes (B, C) both inherit from A, and a fourth class
#   D inherits from both B and C - so A could be reached (and initialized)
#   through two different paths.
# - Calling `super().__init__()` in each class (instead of naming the parent
#   class directly) makes every class cooperate - each __init__ call is routed
#   along the MRO exactly once, so A's __init__ runs only a single time.

print("\n# 08. The Diamond Problem and Cooperative super()")
print("# ------------------------------------")
print("# - Diamond: D(B, C), and both B and C inherit from A.")
print("# - super().__init__() at every level follows the MRO - A's __init__ runs once, not twice.")

class A:
    def __init__(self):
        print("A.__init__")
        self.from_a = True

class B(A):
    def __init__(self):
        super().__init__() # cooperative - follows the MRO, not a hardcoded 'A'
        print("B.__init__")
        self.from_b = True

class C(A):
    def __init__(self):
        super().__init__() # cooperative
        print("C.__init__")
        self.from_c = True

class D(B, C):
    def __init__(self):
        super().__init__() # kicks off the whole chain along D's MRO
        print("D.__init__")

print("\n# Example - Diamond with Cooperative super():")
print("class A: def __init__(self): print(\"A.__init__\")")
print("class B(A): def __init__(self): super().__init__(); print(\"B.__init__\")")
print("class C(A): def __init__(self): super().__init__(); print(\"C.__init__\")")
print("class D(B, C): def __init__(self): super().__init__(); print(\"D.__init__\")")

print("# Output:")
d = D() # A.__init__ runs exactly once, thanks to the MRO
print("D.__mro__:", D.__mro__) # D -> B -> C -> A -> object
print("d.from_a, d.from_b, d.from_c:", d.from_a, d.from_b, d.from_c)

# 09. Mixins
# ------------------------------------
# - A mixin is a small class designed to be combined with others via multiple
#   inheritance, adding one specific piece of reusable behavior. It's not
#   meant to be instantiated on its own.
# - Convention: mixin class names often end in "Mixin", and they're listed
#   before the "main" base class in the inheritance list.

print("\n# 09. Mixins")
print("# ------------------------------------")
print("# - A mixin adds one focused piece of behavior, meant to be combined, not used alone.")

class LoggingMixin:
    def log(self, message):
        print(f"[{self.__class__.__name__}] {message}")

class Service:
    def run(self):
        return "running the service"

class LoggedService(LoggingMixin, Service): # mixed in alongside the main base class
    def run(self):
        self.log("starting run()")
        result = super().run()
        self.log("finished run()")
        return result

print("\n# Example - LoggingMixin:")
print("class LoggingMixin:")
print("    def log(self, message): print(f\"[{self.__class__.__name__}] {message}\")")
print("class Service:")
print("    def run(self): return \"running the service\"")
print("class LoggedService(LoggingMixin, Service):")
print("    def run(self):")
print("        self.log(\"starting run()\")")
print("        result = super().run()")
print("        self.log(\"finished run()\")")
print("        return result")

print("# Output:")
service = LoggedService()
print("service.run():", service.run())

# 10. isinstance() vs type() == for Checking Inheritance
# ------------------------------------
# - `isinstance(obj, Cls)` returns True for obj's class AND any of its
#   subclasses - it respects the inheritance hierarchy.
# - `type(obj) == Cls` only matches the EXACT class, ignoring inheritance -
#   a subclass instance fails this check even though it "is a" Cls.
# - Prefer isinstance() almost always; exact-type checks are a code smell
#   unless you deliberately want to exclude subclasses.

print("\n# 10. isinstance() vs type() == for Checking Inheritance")
print("# ------------------------------------")
print("# - isinstance(obj, Cls): True for Cls and any subclass of Cls.")
print("# - type(obj) == Cls: True only for the exact class, ignores subclasses.")

print("\n# Example - isinstance vs type():")
print("print(isinstance(bottom, Base))  # True - Bottom is a subclass of Base")
print("print(type(bottom) == Base)      # False - bottom's exact type is Bottom")

print("# Output:")
print("isinstance(bottom, Base):", isinstance(bottom, Base))
print("type(bottom) == Base:", type(bottom) == Base)
print("type(bottom) == Bottom:", type(bottom) == Bottom)

# 11. NotImplementedError Pattern vs Real ABC
# ------------------------------------
# - Raising NotImplementedError in a base method is a lightweight convention
#   signaling "subclasses must override this" - but nothing stops a subclass
#   from forgetting to, and the error only surfaces when the method is called.
# - A real abstract base class (ABC + @abstractmethod) enforces this at
#   INSTANTIATION time instead - fails fast, before the missing method is
#   ever called. See 05-Abstraction.py for the full ABC treatment.

print("\n# 11. NotImplementedError Pattern vs Real ABC")
print("# ------------------------------------")
print("# - NotImplementedError: a convention, only fails when the method is actually called.")
print("# - ABC + @abstractmethod: enforced at instantiation - fails immediately. See 05-Abstraction.py.")

class PaymentMethodConvention:
    def pay(self, amount):
        raise NotImplementedError("Subclasses must implement pay()")

class ForgottenPayment(PaymentMethodConvention):
    pass # forgot to override pay() - no error until someone calls it

print("\n# Example - NotImplementedError Pattern:")
print("class PaymentMethodConvention:")
print("    def pay(self, amount): raise NotImplementedError(\"Subclasses must implement pay()\")")

forgotten = ForgottenPayment() # instantiation succeeds - the gap isn't caught yet
print("# Output:")
print("ForgottenPayment() instantiated fine (no enforcement at creation time).")
try:
    forgotten.pay(100)
except NotImplementedError as e:
    print("forgotten.pay(100) -> NotImplementedError:", e, "(caught late, only on call)")

