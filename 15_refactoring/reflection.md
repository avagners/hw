# Неочевидные проектные ошибки (2)

## Пример 1

### Было:
Код парсит CSV-файл, фильтрует данные и затем сохраняет их в базу данных. Всё это сделано в одной функции.

```python
import csv
import sqlite3

def process_csv(file_path):
    conn = sqlite3.connect('example.db')
    cursor = conn.cursor()

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if int(row[2]) > 10:  # фильтрация данных
                cursor.execute("INSERT INTO data_table (col1, col2, col3) VALUES (?, ?, ?)", (row[0], row[1], row[2]))

    conn.commit()
    conn.close()
```

Проблемы:  

Смешение логики: Вся работа с CSV-файлом и базой данных сосредоточена в одной функции.  
Трудно тестировать: Тестировать такую функцию сложно, так как необходимо управлять как файлами, так и базой данных.  
Неявные границы: Логические границы между чтением данных, их фильтрацией и записью не определены явно.

### Стало:
```python
import csv
import sqlite3
from typing import List, Tuple

def read_csv(file_path: str) -> List[Tuple[str, str, str]]:
    with open(file_path, 'r') as file:
        return [tuple(row) for row in csv.reader(file)]

def filter_data(data: List[Tuple[str, str, str]]) -> List[Tuple[str, str, str]]:
    return [row for row in data if int(row[2]) > 10]

def save_to_db(data: List[Tuple[str, str, str]], db_path: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.executemany("INSERT INTO data_table (col1, col2, col3) VALUES (?, ?, ?)", data)

    conn.commit()
    conn.close()

def process_csv(file_path: str, db_path: str):
    data = read_csv(file_path)
    filtered_data = filter_data(data)
    save_to_db(filtered_data, db_path)
```

### Что изменилось
Явные интерфейсы: Функции `read_csv`, `filter_data` и `save_to_db` имеют чётко определённые интерфейсы (принимают и возвращают данные). Эти интерфейсы задают границы между разными этапами обработки данных.  
Влияние на другие части: Теперь тестировать каждый этап обработки данных стало проще: можно тестировать функции отдельно. Также логика программы стала более понятной, а изменения в одной части (например, смена базы данных) не требуют изменения других частей.

## Пример 2

### Было:
Код управляет пользователями в системе, включая их создание, обновление и удаление. Всё это реализовано в одном большом классе.

```python
class UserManager:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id, name, age):
        if user_id not in self.users:
            self.users[user_id] = {"name": name, "age": age}
        else:
            raise ValueError("User already exists")

    def update_user(self, user_id, name=None, age=None):
        if user_id in self.users:
            if name:
                self.users[user_id]["name"] = name
            if age:
                self.users[user_id]["age"] = age
        else:
            raise ValueError("User does not exist")

    def delete_user(self, user_id):
        if user_id in self.users:
            del self.users[user_id]
        else:
            raise ValueError("User does not exist")
```
Проблемы:  
Смешение логики/Неявные границы: Вся логика управления пользователями сосредоточена в одном классе.   
Трудно расширять: Добавление новых операций с пользователями или изменении существующих функций требует модификации этого класса, что может нарушить его работу.

### Стало:
```python
class User:
    def __init__(self, user_id: str, name: str, age: int):
        self.user_id = user_id
        self.name = name
        self.age = age

class UserRepository:
    def __init__(self):
        self.users = {}

    def add_user(self, user: User):
        if user.user_id in self.users:
            raise ValueError("User already exists")
        self.users[user.user_id] = user

    def get_user(self, user_id: str) -> User:
        if user_id not in self.users:
            raise ValueError("User does not exist")
        return self.users[user_id]

    def remove_user(self, user_id: str):
        if user_id not in self.users:
            raise ValueError("User does not exist")
        del self.users[user_id]

class UserManager:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def create_user(self, user_id: str, name: str, age: int):
        user = User(user_id, name, age)
        self.repository.add_user(user)

    def update_user(self, user_id: str, name: str = None, age: int = None):
        user = self.repository.get_user(user_id)
        if name:
            user.name = name
        if age:
            user.age = age

    def delete_user(self, user_id: str):
        self.repository.remove_user(user_id)
```

### Что изменилось
Явные интерфейсы: Класс `UserRepository` управляет данными пользователей, а `UserManager` отвечает за бизнес-логику (создание, обновление и удаление пользователей). Эти классы взаимодействуют через чётко определённые методы.  
Влияние на другие части: Теперь можно легко заменить хранилище пользователей, не меняя бизнес-логику (`UserManager`). Расширение функциональности, например, добавление поиска пользователей, можно реализовать в рамках UserRepository, не затрагивая `UserManager`.

## Пример 3
### Было:
В проекте реализована функция обработки HTTP-запроса, которая выполняет как проверку данных, так и бизнес-логику.

```python
def handle_request(request):
    if not request.get("user_id"):
        return {"error": "User ID is required"}
    
    user = get_user_by_id(request["user_id"])
    
    if not user:
        return {"error": "User not found"}

    if request.get("action") == "update":
        if "name" in request:
            user["name"] = request["name"]
        if "age" in request:
            user["age"] = request["age"]

    return {"success": True, "user": user}
```
Проблемы:  
Смешение логики: Логика обработки запросов и бизнес-логика обновления данных объединены.  
Трудно расширять: Добавление новых типов запросов или изменение логики требует изменений в этой функции, что может привести к ошибкам.  
Неявные границы: Логические границы между проверкой данных и бизнес-логикой не определены.

### Стало:
```python
def validate_request(request) -> bool:
    if not request.get("user_id"):
        return False
    if request.get("action") not in {"update", "delete"}:
        return False
    return True

def process_update(user, request):
    if "name" in request:
        user["name"] = request["name"]
    if "age" in request:
        user["age"] = request["age"]

def handle_request(request):
    if not validate_request(request):
        return {"error": "Invalid request"}
    
    user = get_user_by_id(request["user_id"])
    
    if not user:
        return {"error": "User not found"}

    if request.get("action") == "update":
        process_update(user, request)

    return {"success": True, "user": user}
```
### Что изменилось:
Явные интерфейсы: Функции `validate_request` и `process_update` отделяют логику проверки данных от бизнес-логики. Это чётко разграничивает задачи и позволяет легко добавлять новые типы запросов или изменять логику обработки данных.  
Влияние на другие части: Упрощённая структура позволяет тестировать каждую функцию отдельно и делает добавление новых типов запросов менее трудоёмким и менее подверженным ошибкам.

## Use Case: Управление профилями пользователей

Этот сценарий охватывает основные операции с пользователями: создание нового профиля, обновление данных и удаление профиля. Этот процесс критичен для работы всей системы, поскольку корректное управление профилями пользователей обеспечивает надежность и актуальность данных.

```python
import unittest

class UserManagerUseCaseTest(unittest.TestCase):
    def setUp(self):
        self.repository = UserRepository()
        self.manager = UserManager(self.repository)

    def test_create_user(self):
        """Администратор создает нового пользователя."""
        self.manager.create_user('user1', 'John Doe', 30)
        user = self.repository.get_user('user1')
        
        self.assertEqual(user.name, 'John Doe')
        self.assertEqual(user.age, 30)
        print("Test 'create_user' passed: Пользователь успешно создан")

    def test_update_user(self):
        """Администратор обновляет данные пользователя."""
        self.manager.create_user('user1', 'John Doe', 30)
        self.manager.update_user('user1', name='John Smith', age 35)
        user = self.repository.get_user('user1')

        self.assertEqual(user.name, 'John Smith')
        self.assertEqual(user.age, 35)
        print("Test 'update_user' passed: Данные пользователя успешно обновлены")

    def test_delete_user(self):
        """Администратор удаляет пользователя."""
        self.manager.create_user('user1', 'John Doe', 30)
        self.manager.delete_user('user1')

        with self.assertRaises(ValueError):
            self.repository.get_user('user1')
        print("Test 'delete_user' passed: Пользователь успешно удалён")

    def test_error_on_duplicate_user(self):
        """Попытка создать пользователя с дублирующимся идентификатором."""
        self.manager.create_user('user1', 'John Doe', 30)
        
        with self.assertRaises(ValueError):
            self.manager.create_user('user1', 'Jane Doe', 25)
        print("Test 'error_on_duplicate_user' passed: Невозможно создать пользователя с дублирующимся ID")

    def test_error_on_nonexistent_user_update(self):
        """Попытка обновления несуществующего пользователя."""
        with self.assertRaises(ValueError):
            self.manager.update_user('nonexistent', name='John Smith')
        print("Test 'error_on_nonexistent_user_update' passed: Ошибка при обновлении несуществующего пользователя")

    def test_error_on_nonexistent_user_delete(self):
        """Попытка удаления несуществующего пользователя."""
        with self.assertRaises(ValueError):
            self.manager.delete_user('nonexistent')
        print("Test 'error_on_nonexistent_user_delete' passed: Ошибка при удалении несуществующего пользователя")

if __name__ == '__main__':
    unittest.main()
```

Эти тесты не только проверяют корректность отдельных функций, но и демонстрируют, как эти функции вписываются в общий контекст работы системы и какие ключевые аспекты они поддерживают.


## Выводы:
Выполнение этой работы оказалось для меня очень полезным. Правильное разделение логики на отдельные части значительно упрощает поддержку, расширение функционала и тестирование. После занятия я совсем по-другому смотрю на код во время ревью. Стал больше задавать себе вопрос "что делается?", а не "как делается?". Стал обращать пристальное внимание на интерфейсы, на смешение/разделение логики, так как это несет большие последствия в плане будущего развития кода.  

Важно! "При рефакторинге надо изменять структуру, изменять дизайн, изменять саму конструкцию."  

Создание use case тестов дало мне понимание, как важен контекст при тестировании. Теперь я лучше понимаю, как тесты могут демонстрировать назначение кода в контексте всей системы, а не только проверять его на предмет ошибок.