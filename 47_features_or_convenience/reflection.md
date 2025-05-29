# Компромисс между возможностями и удобством

## 1. Добавление аннотаций типов

```python
# Было (без типов)
def process_data(data):
    return data.upper()

# Стало (с аннотациями)
def process_data(data: str) -> str:
    return data.upper()
```

Что получили:
- IDE начала подсказывать ошибки ещё до запуска кода
- Появилась возможность подключить mypy для статической проверки
- Без потерь: Код не стал сложнее, но стал надёжнее
- Удобнее читать код

## 2. Использование pathlib вместо os.path

```python
# Было:
import os
path = os.path.join(os.getcwd(), "data", "file.txt")

# Стало:
from pathlib import Path
path = Path.cwd() / "data" / "file.txt"
```

Что получили:
- Единый объект для работы с путями
- Автоматическая обработка разных ОС (/ vs )
- Встроенные методы для проверки существования, чтения и т.д.
- Без изменений: Общая логика работы с файлами не изменилась

## 3. Внедрение контекстных менеджеров для ресурсов

```python
# Было:
file = open("data.txt")
try:
    data = file.read()
finally:
    file.close()

# Стало:
with open("data.txt") as file:
    data = file.read()
```

Что получили:
- Гарантированное закрытие ресурсов
- Более чистый и читаемый код
- Поддержка нескольких ресурсов в одном with
- Без изменений: Логика работы с файлом осталась прежней

## 4. Использование dataclasses для DTO

```python
# Было:
def process_user(user_dict):
    name = user_dict["name"]
    age = user_dict["age"]

# Стало:
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int

def process_user(user: User):
    name = user.name
    age = user.age
```

Что получили:
- Проверка типов
- Неизменяемость через frozen=True
- Чёткая структура (нельзя добавить случайное поле)
- Без изменений: Объем кода практически не изменился

## 5. Использование Enum

```python
# Было:
STATUS_ACTIVE = "active"
STATUS_INACTIVE = "inactive"

def handle_status(status):
    if status == STATUS_ACTIVE:
        ...

# Стало:
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

def handle_status(status: Status):
    if status is Status.ACTIVE:
        ...
```

Что получили:
- Автодополнение в IDE всех допустимых значений
- Защита от опечаток в строковых константах
- Возможность добавления методов к статусам
- Без изменений: Фактическая логика обработки не усложнилась

## Выводы

Нет идеальных решений. Чем мощнее инструмент, тем сложнее им пользоваться.  
Часто улучшения требуют минимум усилий. Например, добавление аннотации типов дает множество плюсов.  
Компромиссы — это нормально. Принцип "всё лучшее сразу" почти никогда не работает. 
Гораздо важнее — понимать компромисс, на который идешь: что именно я выигрываю, а чем жертвую.
