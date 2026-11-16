# 04 - OOPs

| File | Covers |
|---|---|
| [01-Class-Object](01-Class-Object.ipynb) | Class/object basics, magic methods, `self`, `__slots__`, `__new__` vs `__init__`, a brief intro to metaclasses |
| [02-Encapsulation](02-Encapsulation.ipynb) | Private/public attributes, getters/setters, static members, name mangling, `functools.cached_property` |
| [03-Inheritance](03-Inheritance.ipynb) | Inheritance types, method overriding, `super()`, MRO/C3 linearization, the diamond problem, mixins |
| [04-Polymorphism](04-Polymorphism.ipynb) | Method overriding polymorphism, duck typing, `__eq__`/`__hash__`, `functools.total_ordering`, `__call__`, `functools.singledispatch` |
| [05-Abstraction](05-Abstraction.ipynb) | Abstract base classes, `@abstractmethod`, virtual subclass registration, `Protocol` vs ABC |
| [06-Dataclasses-And-Operator-Overloading](06-Dataclasses-And-Operator-Overloading.ipynb) | `@dataclass`, `field()`, `__post_init__`, `slots=True`, operator overloading (binary, unary, reflected, `NotImplemented`), `__bool__`, `__format__` |
| [07-Custom-Containers-And-ABCs](07-Custom-Containers-And-ABCs.ipynb) | `collections.abc` hierarchy, custom `Sequence`/`MutableSequence`/`MutableMapping`/`Set`, free mixin methods, subclassing `dict` gotcha, `UserDict` |
| [08-SOLID-Principles](08-SOLID-Principles.ipynb) | Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion — each with a before/after example |
| [09-Descriptors-And-Properties](09-Descriptors-And-Properties.ipynb) | descriptor protocol (`__get__`/`__set__`/`__set_name__`), data vs non-data, lookup order, how `property`/methods work, validated and lazy fields |
| [10-Attribute-Access-Hooks](10-Attribute-Access-Hooks.ipynb) | `__getattr__` vs `__getattribute__`, `__setattr__`, `__delattr__`, `__dir__`, recursion gotcha, proxies, frozen objects |
| [11-Metaclasses-And-Class-Creation](11-Metaclasses-And-Class-Creation.ipynb) | `type()`, class-creation steps, metaclass `__new__`/`__call__`/`__prepare__`, `__init_subclass__`, `__class_getitem__`, class decorators |
| [12-Object-Lifecycle-Copy-And-Serialization](12-Object-Lifecycle-Copy-And-Serialization.ipynb) | `__new__`/`__init__`/`__del__`, GC and `weakref`, `copy`/`deepcopy`, `pickle` hooks, hash/eq contract |
| [13-Composition-Vs-Inheritance](13-Composition-Vs-Inheritance.ipynb) | has-a vs is-a, delegation, mixins, Protocols, fragile base class, refactoring inheritance into composition |
| [14-Creational-Design-Patterns](14-Creational-Design-Patterns.ipynb) | Singleton (4 ways), Factory, Abstract Factory, Builder, Prototype, Object Pool, Borg |
| [15-Structural-Design-Patterns](15-Structural-Design-Patterns.ipynb) | Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy |
| [16-Behavioral-Design-Patterns](16-Behavioral-Design-Patterns.ipynb) | Strategy, Observer, Command, State, Template Method, Iterator, Chain of Responsibility, Visitor, Mediator, Memento, Null Object |
| [17-Pythonic-Patterns-And-Anti-Patterns](17-Pythonic-Patterns-And-Anti-Patterns.ipynb) | registry/plugins, DI, EAFP, Repository, Result types, anti-patterns and code smells |
