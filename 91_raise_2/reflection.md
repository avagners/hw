# Примеры слабого использования исключений в Python

### 1. Вычисление среднего значения списка

**До (слабый подход):**
```python
def average(numbers):
    if not numbers:
        raise ValueError("Список не может быть пустым")
    return sum(numbers) / len(numbers)
```

**После (сильный подход):**
```python
from typing import Sequence, TypeVar

T = TypeVar('T', int, float)

class NonEmptyList(Sequence[T]):
    def __init__(self, items: Sequence[T]):
        if not items:
            raise ValueError("Список не может быть пустым")
        self._items = list(items)

    def __getitem__(self, index):
        return self._items[index]

    def __len__(self):
        return len(self._items)

    def average(self):
        return sum(self._items) / len(self._items)

# Использование
valid_list = NonEmptyList([1, 2, 3])
result = valid_list.average()  # Гарантированно непустой список
```

---

### 2. Вызов метода на потенциально `None` объекте

**До (слабый подход):**
```python
def process_user(user):
    if user is None:
        raise ValueError("Объект пользователя не может быть None")
    return user.get_name().upper()
```

**После (сильный подход):**
```python
from typing import Optional

def process_user(user: Optional[object]) -> str:
    if user is None:
        return "DEFAULT_USER"  # Обработка None на уровне вызывающего кода
    return user.get_name().upper()

# Использование
result = process_user(None)  # Явная обработка None
```

---

### 3. Форматирование пустой строки

**До (слабый подход):**
```python
def format_text(text):
    if not text:
        raise ValueError("Текст не может быть пустым")
    return f"Formatted: {text.upper()}"
```

**После (сильный подход):**
```python
class NonEmptyString(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("Строка не может быть пустой")
        return super().__new__(cls, value)

def format_text(text: NonEmptyString):
    return f"Formatted: {text.upper()}"

# Использование
valid_text = NonEmptyString("hello")
result = format_text(valid_text)  # Гарантированно непустая строка
```

---

### 4. Извлечение квадратного корня из отрицательного числа

**До (слабый подход):**
```python
import math

def sqrt_positive(x):
    if x < 0:
        raise ValueError("Число должно быть неотрицательным")
    return math.sqrt(x)
```

**После (сильный подход):**
```python
class PositiveNumber(float):
    def __new__(cls, value: float):
        if value < 0:
            raise ValueError("Число должно быть неотрицательным")
        return super().__new__(cls, value)

def sqrt_positive(x: PositiveNumber):
    return math.sqrt(x)

# Использование
valid_num = PositiveNumber(9)
result = sqrt_positive(valid_num)  # Гарантированно положительное число
```

---

### 5. Доступ к ключу в словаре

**До (слабый подход):**
```python
def get_value(data, key):
    if not data:
        raise ValueError("Словарь не может быть пустым")
    if key not in data:
        raise KeyError(f"Ключ '{key}' отсутствует")
    return data[key]
```

**После (сильный подход):**
```python
from typing import Mapping

class NonEmptyDict(Mapping[str, object]):
    def __init__(self, data: Mapping[str, object]):
        if not data:
            raise ValueError("Словарь не может быть пустым")
        self._data = dict(data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

def get_value(data: NonEmptyDict, key: str):
    return data[key]  # Гарантированно непустой словарь

# Использование
valid_dict = NonEmptyDict({"name": "Alice"})
result = get_value(valid_dict, "name")  # Ключ гарантированно существует
```

## Выводы

Главное, что я понял из этого упражнения, — это то, что исключения не должны использоваться для управления логикой программы. Вместо того чтобы выбрасывать исключения в обычных ситуациях, таких как валидация входных данных, лучше использовать систему типов и специальные классы, которые гарантируют корректность данных на этапе создания.

Теперь я понимаю, что валидация — это не исключительная ситуация, а нормальный поток данных. Если функция ожидает непустой список, а получает пустой, это не исключение, а ошибка ввода. Надо вернуть код ошибки явно или использовать специальные классы, которые гарантируют непустоту.

Также я понял, что использование системы типов позволяет избежать размазанного кода проверки по всему проекту. Вместо того чтобы проверять на пустоту в каждой функции, можно один раз проверить при создании объекта и затем быть уверенным, что данные корректны.