# 04 - OOPs

| File | Covers |
|---|---|
| [01-Class-Object.py](01-Class-Object.py) · [notes](01-Class-Object.md) | Class/object basics, magic methods, `self`, `__slots__`, `__new__` vs `__init__`, a brief intro to metaclasses |
| [02-Encapsulation.py](02-Encapsulation.py) · [notes](02-Encapsulation.md) | Private/public attributes, getters/setters, static members, name mangling, `functools.cached_property` |
| [03-Inheritance.py](03-Inheritance.py) · [notes](03-Inheritance.md) | Inheritance types, method overriding, `super()`, MRO/C3 linearization, the diamond problem, mixins |
| [04-Polymorphism.py](04-Polymorphism.py) · [notes](04-Polymorphism.md) | Method overriding polymorphism, duck typing, `__eq__`/`__hash__`, `functools.total_ordering`, `__call__`, `functools.singledispatch` |
| [05-Abstraction.py](05-Abstraction.py) · [notes](05-Abstraction.md) | Abstract base classes, `@abstractmethod`, virtual subclass registration, `Protocol` vs ABC |
| [06-Dataclasses-And-Operator-Overloading.py](06-Dataclasses-And-Operator-Overloading.py) · [notes](06-Dataclasses-And-Operator-Overloading.md) | `@dataclass`, `field()`, `__post_init__`, `slots=True`, operator overloading (binary, unary, reflected, `NotImplemented`), `__bool__`, `__format__` |
| [07-Custom-Containers-And-ABCs.py](07-Custom-Containers-And-ABCs.py) · [notes](07-Custom-Containers-And-ABCs.md) | `collections.abc` hierarchy, custom `Sequence`/`MutableSequence`/`MutableMapping`/`Set`, free mixin methods, subclassing `dict` gotcha, `UserDict` |
| [08-SOLID-Principles.py](08-SOLID-Principles.py) · [notes](08-SOLID-Principles.md) | Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion — each with a before/after example |
| [09-Descriptors-And-Properties.py](09-Descriptors-And-Properties.py) · [notes](09-Descriptors-And-Properties.md) | descriptor protocol (`__get__`/`__set__`/`__set_name__`), data vs non-data, lookup order, how `property`/methods work, validated and lazy fields |
| [10-Attribute-Access-Hooks.py](10-Attribute-Access-Hooks.py) · [notes](10-Attribute-Access-Hooks.md) | `__getattr__` vs `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`, recursion gotcha, proxies, frozen objects |
| [11-Metaclasses-And-Class-Creation.py](11-Metaclasses-And-Class-Creation.py) · [notes](11-Metaclasses-And-Class-Creation.md) | `type()`, class-creation steps, metaclass `__new__`/`__call__`/`__prepare__`, `__init_subclass__`, `__class_getitem__`, class decorators |
| [12-Object-Lifecycle-Copy-And-Serialization.py](12-Object-Lifecycle-Copy-And-Serialization.py) · [notes](12-Object-Lifecycle-Copy-And-Serialization.md) | `__new__`/`__init__`/`__del__`, GC and `weakref`, `copy`/`deepcopy`, `pickle` hooks, hash/eq contract |
| [13-Composition-Vs-Inheritance.py](13-Composition-Vs-Inheritance.py) · [notes](13-Composition-Vs-Inheritance.md) | has-a vs is-a, delegation, mixins, Protocols, fragile base class, refactoring inheritance into composition |
| [14-Creational-Design-Patterns.py](14-Creational-Design-Patterns.py) · [notes](14-Creational-Design-Patterns.md) | Singleton (4 ways), Factory, Abstract Factory, Builder, Prototype, Object Pool, Borg |
| [15-Structural-Design-Patterns.py](15-Structural-Design-Patterns.py) · [notes](15-Structural-Design-Patterns.md) | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| [16-Behavioral-Design-Patterns.py](16-Behavioral-Design-Patterns.py) · [notes](16-Behavioral-Design-Patterns.md) | Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility, Visitor, Mediator, Memento, Null Object |
| [17-Pythonic-Patterns-And-Anti-Patterns.py](17-Pythonic-Patterns-And-Anti-Patterns.py) · [notes](17-Pythonic-Patterns-And-Anti-Patterns.md) | registry/plugins, DI, EAFP, Repository, Result types, anti-patterns and code smells |
