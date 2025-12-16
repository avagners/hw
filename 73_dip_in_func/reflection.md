# DIP с т.зр. ФП

## Пример 1: Сортировка с ключевой функцией

Было:
```python
users = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
users_sorted = sorted(users, key=lambda u: u["age"])  # Зависимость от конкретной структуры dict
```

Стало: 
```python
from typing import Callable, Any

def sort_by(collection: list[dict], key_extractor: Callable[[dict], Any]) -> list[dict]:
    return sorted(collection, key=key_extractor)

# Теперь можем менять стратегию сортировки:
sort_by(users, lambda u: u["name"])
sort_by(users, lambda u: u["age"])
```

Функция `sort_by` зависит от абстракции `Callable`, а не от конкретного поля словаря.

## Пример 2: Хранилище данных (абстрактное vs. конкретное)

Было:

```python
class UserService:
    def __init__(self):
        self.db = PostgreSQLDatabase()  # Жёсткая зависимость
    
    def get_user(self, user_id):
        return self.db.query("SELECT * FROM users WHERE id = %s", user_id)
```

Стало:
```python
from abc import ABC, abstractmethod
from typing import Protocol

class Database(Protocol):
    def query(self, sql: str, params: tuple) -> list: ...

class UserService:
    def __init__(self, db: Database):  # Зависим от абстракции
        self.db = db
    
    def get_user(self, user_id):
        return self.db.query("SELECT * FROM users WHERE id = %s", (user_id,))

# Можно подменить на SQLite, Mock и т.д.
```

Используем `Protocol` для определения абстракции хранилища.

## Пример 3: Обработчик событий (event handler)

Было:
```python
def process_event(event):
    if event["type"] == "email":
        send_email(event["data"])
    elif event["type"] == "sms":
        send_sms(event["data"])
```

Стало:
```python
from typing import Callable, Dict

Event = Dict[str, str]
Handler = Callable[[Event], None]

def process_event(event: Event, handlers: Dict[str, Handler]):
    handler = handlers.get(event["type"])
    if handler:
        handler(event)

handlers = {
    "email": lambda e: send_email(e["data"]),
    "sms": lambda e: send_sms(e["data"])
}
```
Обработчики инжектируются как словарь функций - легко добавлять новые.

## Пример 4: Валидация данных с помощью стратегий

Было:
```python
def validate_user(user):
    if len(user["name"]) < 3:
        return False
    if "@" not in user["email"]:
        return False
    return True
```

Стало:
```python
from typing import Callable, Dict

Validator = Callable[[Dict], bool]

def validate_user(user: Dict, validators: list[Validator]) -> bool:
    return all(v(user) for v in validators)

validators = [
    lambda u: len(u["name"]) >= 3,
    lambda u: "@" in u["email"],
    lambda u: u["age"] > 0
]
```

Валидаторы - это список функций, которые можно комбинировать и заменять.

## Пример 5: Логирование (абстрактный логгер)

Было:
```python
import logging

def process_data(data):
    logging.info(f"Processing {data}")
    # ... код
```

Стало:
```python
from typing import Callable

Logger = Callable[[str], None]

def process_data(data, logger: Logger):
    logger(f"Processing {data}")
    # ... код

# Можно использовать любой callable:
process_data(data, print)
process_data(data, lambda msg: open("log.txt", "a").write(msg + "\n"))
```

Функция зависит от абстрактного логгера (`Callable`), а не от конкретного модуля `logging`.

## Выводы
После выполнения этого задания я по-новому взглянул на принцип инверсии зависимостей (DIP). Раньше он казался мне чем-то абстрактным.

Оказывается, я уже интуитивно применял его в своём коде, просто не осознавал этого как формальный принцип.

DIP - это про гибкость и тестируемость. Когда зависимости инжектируются извне, код становится проще тестировать (можно подставлять моки) и расширять (можно добавлять новые реализации без изменения существующего кода).

Передача функций как аргументов - это и есть инверсия зависимостей в функциональном стиле. Мне особенно понравилось, как с помощью функций высшего порядка можно создавать гибкие и переиспользуемые компоненты.

Когда модули зависят от абстракций, а не от конкретики, код становится менее связанным, его проще читать и рефакторить.

Что нужно делать дальше в работе:
1) Сразу проектировать зависимости как абстракции (протоколы, абстрактные классы, Callable).
2) Чаще использовать инъекцию зависимостей через аргументы функций или конструкторы.
3) Документировать ожидаемые абстракции в типах и docstring.

