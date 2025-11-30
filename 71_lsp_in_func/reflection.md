# LSP с т.зр. ФП

## Пример 1: Функции работы с последовательностями
```python
from typing import Sequence, TypeVar

T = TypeVar('T')

def process_sequence(seq: Sequence[T]) -> list[T]:
    """Обрабатывает любую последовательность - список, кортеж, строку"""
    return [item for item in seq if item is not None]

# LSP в действии - все эти вызовы работают корректно:
process_sequence([1, 2, 3]) # list
process_sequence((1, 2, 3)) # tuple  
process_sequence("hello")   # str
process_sequence(range(5))  # range
```

Все типы соблюдают контракт `Sequence` - они итерируемы, поддерживают `len()`, `__getitem__()`. Я могу подставить любую реализацию последовательности, и функция продолжит работать.

## Пример 2: Контекстные менеджеры
```python
from contextlib import contextmanager
from typing import Iterator

def process_with_resource(resource) -> str:
    """Работает с любым контекстным менеджером"""
    with resource as ctx:
        return f"Processed: {ctx}"

# Разные ресурсы, одинаковый интерфейс:
with open('file.txt') as f:
    process_with_resource(f)  # file object

@contextmanager
def mock_resource() -> Iterator[str]:
    yield "mock_data"

process_with_resource(mock_resource())  # custom context manager
```

Все контекстные менеджеры соблюдают контракт `__enter__`/`__exit__`. Неважно, что под капотом - реальный файл, мок, соединение с БД - интерфейс одинаковый.

## Пример 3: Callable объекты
```python
from typing import Callable, List

def transform_data(
    data: List[int], 
    transformer: Callable[[int], int]
) -> List[int]:
    """Применяет любую callable-функцию к данным"""
    return [transformer(x) for x in data]

# Разные реализации, одинаковый контракт:
transform_data([1, 2, 3], lambda x: x * 2)     # lambda
transform_data([1, 2, 3], abs)                 # built-in function
transform_data([1, 2, 3], lambda x: x ** 2)    # другая lambda

class Multiplier:
    def __init__(self, factor: int):
        self.factor = factor
    
    def __call__(self, x: int) -> int:
        return x * self.factor

transform_data([1, 2, 3], Multiplier(5))       # callable object
```

Все эти сущности соблюдают контракт `Callable[[int], int]` - принимают `int`, возвращают `int`. Реализация не важна.

## Пример 4: Протоколы (структурная типизация)
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Serializable(Protocol):
    def to_json(self) -> dict: ...
    
    def from_json(self, data: dict) -> 'Serializable': ...

def serialize_anything(obj: Serializable) -> str:
    """Сериализует любой объект, поддерживающий Serializable протокол"""
    import json
    return json.dumps(obj.to_json())

# Разные классы, одинаковый протокол:
class User:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age
    
    def to_json(self) -> dict:
        return {"name": self.name, "age": self.age}
    
    def from_json(self, data: dict) -> 'User':
        return User(data["name"], data["age"])

class Product:
    def __init__(self, title: str, price: float):
        self.title = title
        self.price = price
    
    def to_json(self) -> dict:
        return {"title": self.title, "price": self.price}
    
    def from_json(self, data: dict) -> 'Product':
        return Product(data["title"], data["price"])

# LSP: обе реализации взаимозаменяемы
serialize_anything(User("John", 30))
serialize_anything(Product("Laptop", 999.99))
```

Классы `User` и `Product` не связаны наследованием, но соблюдают один протокол. Они взаимозаменяемы в контексте сериализации.

## Пример 5: Итераторы и генераторы
```python
def process_items(items) -> list:  # Не указан конкретный тип!
    """Обрабатывает любую итерируемую коллекцию"""
    result = []
    for item in items:  # Полагается только на итерационный протокол
        result.append(process_item(item))
    return result

# Все эти варианты работают:
process_items([1, 2, 3])                    # list
process_items((x for x in range(5)))        # generator
process_items({1, 2, 3})                    # set
process_items({"a": 1, "b": 2}.values())    # dict_values

class CustomIterable:
    def __iter__(self):
        return iter([10, 20, 30])

process_items(CustomIterable())              # custom iterable
```

Функция полагается только на контракт итератора (`__iter__`/`__next__`). Любая реализация, соблюдающая этот контракт, будет работать.

## Выводы

В Python с его duck typing LSP проявляется естественно. Когда я пишу функцию, которая работает с любым Sequence, я неявно заключаю контракт: "Всё, что можно итерировать и имеет длину, будет работать".

LSP - это про предсказуемость. Если функция обещает принимать `Callable[[int], int]`, то любая реализация должна:
- Брать ровно один int
- Возвращать int
- Не делать неожиданных вещей (типа запросов в сеть)

Я открыл для себя typing.Protocol - это же идеальный инструмент для LSP.
```python
class Serializable(Protocol):
    def to_json(self) -> dict: ...
    
# Теперь User и Product могут быть совершенно разными классами,
# но если оба реализуют to_json() -> они взаимозаменяемы!
```

Раньше я мокал конкретные классы. Теперь понимаю - нужно тестировать интерфейсы:
```python
# Раньше: Жёсткая привязка к реализации
def test_process_user():
    user = User("John")  # Конкретный класс
    # ...

# Теперь: Тестирую контракт
def test_serializable_contract():
    any_serializable = Mock(spec=Serializable)  # Проверяю протокол
    any_serializable.to_json.return_value = {"test": True}
    # ...
```
Что я буду делать по-другому:
- Использовать абстрактные типы (Sequence, Mapping, Iterable) вместо list, dict
- Явно определять протоколы для сложных контрактов
- Думать "а что если подставят другую реализацию?" перед написанием функции
- Тестировать с разными совместимыми типами чтобы убедиться в LSP
- Документировать ожидаемое поведение, а не только типы

LSP - это не про наследование, а про доверие. Когда я пишу функцию `process_sequence(seq: Sequence)`, я доверяю, что любой переданный объект будет вести себя как последовательность. И тот, кто передаёт объект, доверяет, что моя функция не будет делать с ним ничего неожиданного.
Теперь я вижу LSP везде: в контекстных менеджерах, в итераторах, в callable объектах.