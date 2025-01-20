# Повышаем полиморфность кода

## Пример 1

До:
```python
def sort_numbers(numbers: list[int]) -> list[int]:
    return sorted(numbers)
```

После:
```python
from typing import TypeVar, Iterable, Callable

T = TypeVar('T')

def sort_items(items: Iterable[T], key: Callable[[T], any] = None, reverse: bool = False) -> list[T]:
    return sorted(items, key=key, reverse=reverse)
```

Теперь функция принимает любой итерируемый объект и может сортировать элементы любого типа с использованием произвольного ключа.

## Пример 2

До:
```python
def max_of_two(a: int, b: int) -> int:
    return a if a > b else b
```

После:
```python
def max_of_two(a: T, b: T) -> T:
    return a if a > b else b
```

Теперь функция поддерживает сравнение любых типов, поддерживающих операцию сравнения, а не только `int`.

## Пример 3

До:
```python
def join_strings(strings: list[str]) -> str:
    return ", ".join(strings)
```

После:
```python
def join_items(items: Iterable[T], separator: str = ", ") -> str:
    return separator.join(map(str, items))
```

Теперь функция может объединять элементы любого типа, а не только строки.

## Пример 4

До:
```python
def filter_even(numbers: list[int]) -> list[int]:
    return [n for n in numbers if n % 2 == 0]
```

После:
```python
def filter_items(items: Iterable[T], predicate: Callable[[T], bool]) -> list[T]:
    return [item for item in items if predicate(item)]
```

Функция теперь может фильтровать любые данные, используя произвольное условие `predicate`.

## Пример 5

До:
```python
def square_numbers(numbers: list[int]) -> list[int]:
    return [n**2 for n in numbers]
```

После:
```python
def transform_items(items: Iterable[T], transform: Callable[[T], R]) -> list[R]:
    return [transform(item) for item in items]
```

Теперь функция может применять любое преобразование `transform` к любым элементам `items` и возвращать элементы любого типа `R`.

## Итоги

Интересное упражнение, благодаря которму я понял, что:

- Полиморфизм — это мощный инструмент для написания более гибкого и переиспользуемого кода.

- Использование параметров типа (`TypeVar`) и более абстрактных коллекций (`Iterable` вместо `list`) позволило мне применять одни и те же функции в большем числе сценариев. Это снижает дублирование кода и упрощает поддержку.

- Передача поведения через `Callable` (`predicate`, `transform`) помогает разделить ответственность. Функция отвечает только за управление потоком данных, а пользователь сам определяет, как данные обрабатываются.

- Строгая аннотация типов с `Callable` и `TypeVar` помогает IDE предупреждать о возможных ошибках. Это важно, так как повышенная обобщённость может привести к неожиданным случаям, если не контролировать типы.