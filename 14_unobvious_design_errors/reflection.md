# Неочевидные проектные ошибки (1)

## Пример 1

### Было:

```python
import re

def send_email(email, subject, body):
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        raise ValueError("Invalid email address")
    if not isinstance(subject, str):
        raise ValueError("Subject must be a string")
    if not isinstance(body, str):
        raise ValueError("Body must be a string")

    # Send email
    print(f"Email sent to {email} with subject: {subject}")
```

### Стало:
```python
import re

class EmailAddress:
    def __init__(self, email: str):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Invalid email address")
        self.value = email

    def __repr__(self):
        return self.value


class Email:
    def __init__(self, to: EmailAddress, subject: str, body: str):
        self.to = to
        self.subject = subject
        self.body = body

    def send(self):
        print(f"Email sent to {self.to} with subject: {self.subject}")


email_address = EmailAddress("example@example.com")
email = Email(email_address, "Hello", "This is the body of the email")
email.send()
```

В данном примере удалены проверки формата электронной почты, типа строки для темы и тела в функции send_email.
Созданы отдельные классы `EmailAddress` и `Email`, которые инкапсулируют проверку правильности данных.

## Пример 2

### Было:
```python
def get_value(data, key):
    if not isinstance(data, dict):
        raise ValueError("Data must be a dictionary")
    if key not in data:
        raise KeyError("Key not found in data")

    return data[key]
```

### Стало:
```python
from typing import Dict

def get_value(data: Dict[str, int], key: str) -> int:
    return data[key]
```

Удалена проверка типа данных и наличия ключа.
Использована аннотация типов и статический анализатор для обеспечения корректности данных.

## Пример 3

### Было:
```python
def read_file(file_path):
    if not isinstance(file_path, str):
        raise ValueError("File path must be a string")
    if not file_path.endswith('.txt'):
        raise ValueError("File must be a .txt file")

    with open(file_path, 'r') as file:
        return file.read()
```

### Стало:
```python
from pathlib import Path

def read_file(file_path: Path) -> str:
    if file_path.suffix != '.txt':
        raise ValueError("File must be a .txt file")

    with file_path.open('r') as file:
        return file.read()
```

Удалена проверка типа данных.
Использован тип Path из модуля pathlib для представления и проверки файловых путей.

## Пример 4

### Было:
```python
def process_data(data):
    if not isinstance(data, list):
        raise ValueError("Input data must be a list")
    if not all(isinstance(item, int) for item in data):
        raise ValueError("All items in the list must be integers")
    if not data:
        raise ValueError("Input list cannot be empty")

    result = sum(data)
    return result
```

### Стало:
```python
from typing import List

def process_data(data: List[int]) -> int:
    if not data:
        raise ValueError("Input list cannot be empty")

    result = sum(data)
    return result
```

Удалена проверка типа данных и типа элементов в списке.
Использована аннотация типов и статический анализатор для обеспечения корректности типа данных.

## Пример 5

### Было:
```python
def schedule_event(date, time, event_name):
    if not isinstance(date, str):
        raise ValueError("Date must be a string")
    if not re.match(r"\d{4}-\d{2}-\d{2}", date):
        raise ValueError("Date must be in the format YYYY-MM-DD")
    if not isinstance(time, str):
        raise ValueError("Time must be a string")
    if not re.match(r"\d{2}:\d{2}", time):
        raise ValueError("Time must be in the format HH:MM")
    if not isinstance(event_name, str):
        raise ValueError("Event name must be a string")

    # Schedule event
    print(f"Event '{event_name}' scheduled on {date} at {time}")
```

```python
import re
from datetime import datetime

class Date:
    def __init__(self, date_str: str):
        try:
            self.value = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date must be in the format YYYY-MM-DD")

    def __repr__(self):
        return self.value.strftime("%Y-%m-%d")

class Time:
    def __init__(self, time_str: str):
        try:
            self.value = datetime.strptime(time_str, "%H:%M").time()
        except ValueError:
            raise ValueError("Time must be in the format HH:MM")

    def __repr__(self):
        return self.value.strftime("%H:%M")

class Event:
    def __init__(self, date: Date, time: Time, event_name: str):
        self.date = date
        self.time = time
        self.event_name = event_name

    def schedule(self):
        print(f"Event '{self.event_name}' scheduled on {self.date} at {self.time}")
```

Удалена проверка формата даты и времени, типа строки для названия события в функции `schedule_event`.
Cозданы отдельные классы `Date` и `Time`, которые инкапсулируют проверку правильности данных. Теперь ошибки, связанные с некорректным форматом даты и времени или неправильным типом данных, невозможны, так как проверка выполняется один раз в конструкторах этих классов.

## Выводы

Какие уроки я вынес на будущее:

1) вместо того чтобы делать проверки на каждом шагу, лучше инкапсулировать их внутри соответствующих классов;

2) aннотации типов и статический анализатор могут значительно упростить процесс обнаружения ошибок на этапе написания кода;

3) cоздание классов-значений (например, EmailAddress, Date, Time) позволяет явно задать допустимые значения и гарантирует, что объект всегда находится в валидном состоянии;

4) поднятие уровня абстракции за счет создания новых типов данных делает код более гибким и модульным, что облегчает тестирование и повторное использование кода;

5) стараясь сделать ошибки невозможными путем проектирования системы типов и структуры данных, можно снизить вероятность появления ошибок.
