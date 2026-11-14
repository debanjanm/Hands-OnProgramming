from abc import ABC, abstractmethod

# 01. SOLID Principles - Introduction
# ------------------------------------
# - Five OOP design principles for code that's easier to maintain and extend.
# - S - Single Responsibility   O - Open/Closed        L - Liskov Substitution
# - I - Interface Segregation   D - Dependency Inversion

print("# 01. SOLID Principles - Introduction")
print("# ------------------------------------")

# 02. S - Single Responsibility Principle
# ------------------------------------
# - A class should have only one reason to change.
print("\n# 02. Single Responsibility Principle")

# Bad: one class does math AND formatting/printing (two reasons to change)
class InvoiceBad:
    def __init__(self, amount):
        self.amount = amount
    def total_with_tax(self):
        return self.amount * 1.1
    def print_invoice(self):
        print(f"Invoice total: {self.total_with_tax()}")

# Good: split into two single-purpose classes
class Invoice:
    def __init__(self, amount):
        self.amount = amount
    def total_with_tax(self):
        return self.amount * 1.1

class InvoicePrinter:
    def print_invoice(self, invoice):
        print(f"Invoice total: {invoice.total_with_tax()}")

InvoicePrinter().print_invoice(Invoice(100))

# 03. O - Open/Closed Principle
# ------------------------------------
# - Open for extension, closed for modification: add new behavior without
#   editing existing, already-tested code.
print("\n# 03. Open/Closed Principle")

# Bad: adding a new shape means editing this function's if/elif chain
def area_bad(shape):
    if shape["type"] == "circle":
        return 3.14159 * shape["radius"] ** 2
    elif shape["type"] == "square":
        return shape["side"] ** 2
    # every new shape -> another elif here

# Good: new shapes are added as new classes, calculate_area() never changes
class Shape(ABC):
    @abstractmethod
    def area(self):
        pass

class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius
    def area(self):
        return 3.14159 * self.radius ** 2

class Square(Shape):
    def __init__(self, side):
        self.side = side
    def area(self):
        return self.side ** 2

def total_area(shapes):
    return sum(shape.area() for shape in shapes)

print("total area:", total_area([Circle(2), Square(3)]))

# 04. L - Liskov Substitution Principle
# ------------------------------------
# - A subclass must be usable anywhere its parent class is expected,
#   without breaking correctness.
print("\n# 04. Liskov Substitution Principle")

# Bad: Square "is-a" Rectangle in real life, but breaks Rectangle's contract
class RectangleBad:
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def set_width(self, width):
        self.width = width
    def set_height(self, height):
        self.height = height

class SquareBad(RectangleBad):
    def set_width(self, width):     # breaks expectation: only width changes
        self.width = self.height = width
    def set_height(self, height):   # same problem for height
        self.width = self.height = height

def resize_test(rect):
    rect.set_width(5)
    rect.set_height(10)
    assert rect.width == 5  # fails for SquareBad - violates substitutability

try:
    resize_test(SquareBad(2, 2))
except AssertionError:
    print("SquareBad violates Liskov substitution (breaks Rectangle's contract)")

resize_test(RectangleBad(2, 2))
print("RectangleBad honors the contract - no error")

# 05. I - Interface Segregation Principle
# ------------------------------------
# - Don't force a class to implement methods it doesn't need. Prefer several
#   small, focused interfaces over one large one.
print("\n# 05. Interface Segregation Principle")

# Bad: one fat interface forces Robot to implement eat() (which makes no sense)
class WorkerBad(ABC):
    @abstractmethod
    def work(self): pass
    @abstractmethod
    def eat(self): pass

# Good: split into focused interfaces, implement only what applies
class Workable(ABC):
    @abstractmethod
    def work(self): pass

class Eatable(ABC):
    @abstractmethod
    def eat(self): pass

class Human(Workable, Eatable):
    def work(self): return "Human working"
    def eat(self): return "Human eating"

class Robot(Workable):  # no eat() forced on it
    def work(self): return "Robot working"

print(Human().work(), "|", Human().eat())
print(Robot().work())

# 06. D - Dependency Inversion Principle
# ------------------------------------
# - Depend on abstractions, not concrete implementations. High-level code
#   shouldn't be tightly coupled to one specific low-level class.
print("\n# 06. Dependency Inversion Principle")

# Bad: Notifier is hard-wired to EmailSender - can't swap without editing it
class EmailSenderBad:
    def send(self, message):
        print(f"Emailing: {message}")

class NotifierBad:
    def __init__(self):
        self.sender = EmailSenderBad()  # tight coupling to a concrete class
    def notify(self, message):
        self.sender.send(message)

# Good: Notifier depends on an abstraction; any sender that fits it works
class MessageSender(ABC):
    @abstractmethod
    def send(self, message):
        pass

class EmailSender(MessageSender):
    def send(self, message):
        print(f"Emailing: {message}")

class SMSSender(MessageSender):
    def send(self, message):
        print(f"Texting: {message}")

class Notifier:
    def __init__(self, sender: MessageSender):
        self.sender = sender  # injected - depends on the abstraction only
    def notify(self, message):
        self.sender.send(message)

Notifier(EmailSender()).notify("Hello via email")
Notifier(SMSSender()).notify("Hello via SMS")

# 07. Why SOLID Matters
# ------------------------------------
print("\n# 07. Why SOLID Matters")
print("# - Easier to extend without breaking existing, tested code.")
print("# - Easier to test (dependencies can be swapped for fakes/mocks).")
print("# - Not dogma - apply where complexity justifies it, not everywhere.")

# 08. Combined Example - SRP + OCP + DIP Together (Plugin-Style Notifications)
# ------------------------------------
# - A small, realistic design where three principles reinforce each other:
#   SRP (each class does one job), OCP (new channels added without editing
#   existing code), DIP (the dispatcher depends on the MessageSender
#   abstraction from #06, not on any specific channel).
class PushSender(MessageSender): # a brand-new channel - existing code untouched (OCP)
    def send(self, message):
        print(f"Push notification: {message}")

class NotificationService: # single responsibility: fan out to registered senders (SRP)
    def __init__(self):
        self.senders = [] # depends only on the MessageSender abstraction (DIP)
    def register(self, sender: MessageSender):
        self.senders.append(sender)
    def notify_all(self, message):
        for sender in self.senders:
            sender.send(message)

print("\n# 08. Combined Example - Plugin-Style Notification System")
service = NotificationService()
service.register(EmailSender())
service.register(SMSSender())
service.register(PushSender()) # added without touching NotificationService at all
service.notify_all("Server restarted")

# 09. When NOT to Apply SOLID
# ------------------------------------
# - SOLID pays off when a codebase is large, long-lived, or has multiple
#   contributors and changing requirements - the abstractions earn their
#   keep by making future changes safer and cheaper.
# - For a 50-line script, a one-off data analysis, or a throwaway prototype,
#   applying all five principles is over-engineering: extra classes and
#   interfaces add indirection with no future change to protect against.
#   Write the simple, direct version first; introduce SOLID structure only
#   when the pain of NOT having it (duplicated logic, fragile edits) shows up.
print("\n# 09. When NOT to Apply SOLID")
print("# - Small scripts/prototypes: SOLID's abstractions cost more than they save.")
print("# - Apply it when change is likely and the codebase will be maintained by others -")
print("#   not as a checklist for every function you write.")
