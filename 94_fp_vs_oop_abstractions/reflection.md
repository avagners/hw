# Различие между генерико-подобными и интерфейсо-подобными абстракциями

## 1. Выражают абстрактные свойства (генерико-подобная абстракция)

Идея: не важно, что это за объект. Важно, что он обладает некоторым математическим свойством.

Например — **Functor**.

```python
from typing import Protocol, TypeVar, Callable

T = TypeVar("T")
U = TypeVar("U")


class Functor(Protocol[T]):
    def map(self, f: Callable[[T], U]) -> "Functor[U]":
        ...


class Box:
    def __init__(self, value):
        self.value = value

    def map(self, f):
        return Box(f(self.value))


box = Box(10)
print(box.map(lambda x: x + 1).value)
```

Здесь важно свойство:

> "К контейнеру можно применить функцию."

Не важно, что это именно `Box`.

## 2. Выражают понятия предметной области (интерфейсо-подобная абстракция)

Идея: абстракция отражает понятие бизнеса.

```python
from abc import ABC, abstractmethod


class PaymentProvider(ABC):

    @abstractmethod
    def pay(self, amount: float):
        pass


class Stripe(PaymentProvider):

    def pay(self, amount):
        print(f"Stripe charged {amount}")


class TBank(PaymentProvider):

    def pay(self, amount):
        print(f"TBank charged {amount}")
```

Это уже понятие предметной области:

> Платежная система.


## 3. Спецификации бессрочны (генерико-подобная абстракция)

Пример — **Monoid**.

```python
class SumMonoid:

    @staticmethod
    def empty():
        return 0

    @staticmethod
    def combine(a, b):
        return a + b


print(SumMonoid.combine(2, 3))
```

Свойства моноида:

```text
combine(a, empty) == a
combine(empty, a) == a
```

Эти свойства не зависят от технологий и времени.

# 4. Реализации имеют срок действия (интерфейсо-подобная абстракция)

Сегодня используется один API.
Завтра — другой.

```python
class SmsGateway:

    def send(self, phone, text):
        pass


class TwilioGateway(SmsGateway):

    def send(self, phone, text):
        print("Twilio")


class NexmoGateway(SmsGateway):

    def send(self, phone, text):
        print("Nexmo")
```

Через год Twilio могут заменить.
Интерфейс останется прежним.

# 5. Используются для идентификации идиом (генерико-подобная абстракция)

Пример — **Fold**.

```python
from functools import reduce

numbers = [1, 2, 3, 4]

total = reduce(lambda acc, x: acc + x, numbers, 0)

print(total)
```

# 6. Используются для конструирования паттернов (интерфейсо-подобная абстракция)

Пример — паттерн **Strategy**.

```python
from abc import ABC, abstractmethod


class DiscountStrategy(ABC):

    @abstractmethod
    def apply(self, price):
        pass


class VipDiscount(DiscountStrategy):

    def apply(self, price):
        return price * 0.8


class StudentDiscount(DiscountStrategy):

    def apply(self, price):
        return price * 0.9
```

Это строительный блок архитектуры.

# 7. Статическая типизация (генерико-подобная абстракция)

Пример с Generic.

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):

    def __init__(self, value: T):
        self.value = value
```

В Haskell, F# или OCaml такие типы проверяются компилятором.

---

# 8. Динамическая реализация (интерфейсо-подобная абстракция)

Duck Typing.

```python
class Dog:

    def speak(self):
        print("Woof")


class Cat:

    def speak(self):
        print("Meow")


def make_sound(animal):
    animal.speak()


make_sound(Dog())
make_sound(Cat())
```

Вообще не важно, какого класса объект.
Важно только, что он умеет `speak()`.

---

# 9. Полиморфизм времени компиляции (генерико-подобная абстракция)

Generic-функция.

```python
from typing import Iterable, Callable


def fmap(xs: Iterable[int], f: Callable[[int], int]):
    return [f(x) for x in xs]


print(fmap([1, 2], lambda x: x * 2))
```

В статически типизированном языке компилятор выводит тип функции.

# 10. Динамический полиморфизм (интерфейсо-подобная абстракция)

```python
from abc import ABC, abstractmethod


class Storage(ABC):

    @abstractmethod
    def save(self, value):
        pass


class FileStorage(Storage):

    def save(self, value):
        print("File")


class DbStorage(Storage):

    def save(self, value):
        print("DB")
```

Выбор реализации происходит во время выполнения программы.

# 11. Механизм генерализации (генерико-подобная абстракция)

Одна функция работает для множества типов.

```python
from typing import Iterable


def length(xs: Iterable):
    return sum(1 for _ in xs)


print(length([1, 2, 3]))
print(length("abc"))
```

Мы обобщили алгоритм.


# 12. Механизм инкапсуляции (интерфейсо-подобная абстракция)

```python
class PaymentService:

    def __init__(self, provider):
        self.provider = provider

    def checkout(self, amount):
        self.provider.pay(amount)
```

Клиент не знает, какой именно провайдер используется внутри.

## 13. Абстрактные свойства

```python
class Comparable:

    def less(self, other):
        ...
```

Выражается абстрактное свойство:

> "объекты можно сравнивать".

## 14. Понятия предметной области

```python
class Courier:

    def deliver(self, order):
        ...
```

Это уже понятие бизнеса — **курьер**.

## 15. Бессрочная спецификация

```python
class Equality:

    def equals(self, a, b):
        return a == b
```

Понятие равенства не меняется со временем.

## 16. Реализация со сроком жизни

```python
class Cache:

    def get(self, key):
        ...
```

Сегодня реализация через Redis.
Завтра — через Memcached.
Интерфейс остается прежним.

## 17. Идентификация идиомы

```python
mapped = map(str.upper, ["a", "b"])
```

## 18. Конструирование паттерна

Паттерн **Factory**.

```python
class ReportFactory:

    def create(self, kind):
        ...
```

## 19. Статическая типизация

```python
from typing import Optional

name: Optional[str]
```

Тип известен заранее и проверяется средствами анализа типов.

## 20. Динамическая реализация

```python
class JsonSerializer:

    def serialize(self, obj):
        ...
```

Во время выполнения можно подставить другую реализацию сериализатора.

## 21. Полиморфизм времени компиляции

```python
from typing import TypeVar

T = TypeVar("T")


def identity(x: T) -> T:
    return x
```

Одна функция работает для любых типов.

## 22. Динамический полиморфизм

```python
class Animal:

    def move(self):
        ...


class Bird(Animal):

    def move(self):
        print("Fly")


class Fish(Animal):

    def move(self):
        print("Swim")
```

Какой метод будет вызван, определяется во время выполнения программы.

## 23. Механизм генерализации

```python
def first(iterable):
    return next(iter(iterable))
```

Один алгоритм работает для любых итерируемых объектов.

## 24. Механизм инкапсуляции

```python
class UserRepository:

    def find(self, user_id):
        ...
```

Снаружи никто не знает:

- используется SQL;
- используется MongoDB;
- данные берутся через REST API;
- применяется кеширование.

Все детали скрыты за интерфейсом.

---

# Итоговое сравнение

| Генерико-подобные абстракции | Интерфейсо-подобные абстракции |
|------------------------------|--------------------------------|
| Что общего у объектов? | Кто выполняет роль? |
| Выражают абстрактные свойства | Выражают обязанности предметной области |
| Генерализуют алгоритмы | Позволяют заменять реализации |
| Работают через параметры типов | Работают через интерфейсы и полиморфизм |
| Главная задача — повторное использование алгоритмов | Главная задача — расширяемость системы |
| Примеры: `Functor`, `Fold`, `Map`, `Monoid`, `Comparable`, `Iterable` | Примеры: `PaymentProvider`, `Repository`, `Notifier`, `Storage`, `DiscountStrategy`, `MessageBus` |

## Главное различие

**Генерико-подобные абстракции** отвечают на вопрос:

> **Какими общими свойствами обладают разные типы данных?**

Они помогают писать один алгоритм, работающий сразу для множества типов.

---

**Интерфейсо-подобные абстракции** отвечают на вопрос:

> **Какие роли существуют в системе и какие обязанности они выполняют?**

Они помогают строить расширяемые приложения, в которых реализации можно свободно заменять без изменения клиентского кода.