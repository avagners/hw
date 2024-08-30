# Интерфейс компактнее реализации?

## Призрачное состояние (ghost state)

### Пример 1

```python
def process_items(items):
    total_processed = 0  # Призрачное состояние
    for item in items:
        if should_process(item):
            process(item)
            total_processed += 1
    return total_processed
```

Здесь `total_processed` является призрачным состоянием. Эта переменная никак не отражена в интерфейсе функции и используется исключительно для внутренних вычислений.

### Пример 2

```python
def calculate(data):
    cache = {}  # Призрачное состояние
    result = []
    for item in data:
        if item in cache:
            result.append(cache[item])
        else:
            computed = complex_calculation(item)
            cache[item] = computed
            result.append(computed)
    return result
```

В этом случае `cache` является призрачным состоянием, которое существует внутри функции. Однако это не видно пользователю функции.

### Пример 3

```python
def process_file(file_path):
    is_valid = False  # Призрачное состояние
    with open(file_path, 'r') as file:
        for line in file:
            if check_format(line):
                is_valid = True
            else:
                is_valid = False
                break
    if is_valid:
        save_processed_file(file_path)
    else:
        raise ValueError("File format is invalid")
```

В этом примере переменная `is_valid` используется для отслеживания состояния файла во время его обработки. Это состояние временное и используется исключительно внутри функции для принятия решения о дальнейшем действии. Однако оно не отражено в интерфейсе функции.


## Погрешности/неточности, которые чрезмерно "сужают" логику кода, ограничивая её.

### Пример 1

```python 
def is_adult(age: int) -> bool:
    return age >= 18
```

Эта функция считает взрослым человека, достигшего 18 лет, что может быть ограничением, если в разных контекстах возраст совершеннолетия может отличаться (например, в некоторых странах возраст совершеннолетия состовляет 21 год).

Расширенная версия ниже.

```python
def is_adult(age: int, adult_age: int) -> bool:
    return age >= adult_age
```

Добавил аргумент `adult_age` -- возраст, с которого человек считается взрослым.
Это позволяет адаптировать логику функции под разные условия, делая ее более гибкой.


### Пример 2

```python
def is_user_in_list(username: str, user_list: List[str]) -> bool:
    return username in user_list
```

Функция проверяет наличие пользователя в списке строго по совпадению строк. Это ограничение может быть проблемой, если требуется учесть регистр символов.

Расширенная версия ниже.

```python
def is_user_in_list(username: str, user_list: List[str], case_sensitive: bool = False, trim_spaces: bool = False) -> bool:
    if trim_spaces:
        username = username.strip()
        user_list = [user.strip() for user in user_list]

    if not case_sensitive:
        username = username.lower()
        user_list = [user.lower() for user in user_list]

    return username in user_list
```

Расширил функцию 2-я параметрами.
Параметр `case_sensitive` позволяет учитывать или игнорировать регистр символов при проверке наличия пользователя в списке. Это делает функцию более гибкой в ситуациях, когда имя пользователя может быть введено с разным регистром.
Параметр `trim_spaces` позволяет удалить пробелы в начале и конце строки, что полезно, если в списке могут случайно появиться лишние пробелы, которые не должны влиять на результат проверки.


### Пример 3

```python
def is_speed_valid(speed: int) -> bool:
    return 60 <= speed <= 120
```

Эта функция жестко ограничивает диапазон допустимой скорости значениями от 60 до 120. Однако допустимые значения скорости могут зависеть от контекста.

Расширенная версия ниже.

```python
def is_speed_valid(speed: float, min_speed: float, max_speed: float) -> bool:
    return min_speed <= speed <= max_speed
```

Добавил параметры `min_speed` и `max_speed`. Это делает функцию пригодной для использования в различных сценариях.


## Интерфейс явно не должен быть проще реализации

### Пример 1

```python
def encrypt(data: bytes, key: bytes, iv: bytes) -> bytes:
    pass
```

Просто интерфейс с тремя байтовыми массивами (данные, ключ, вектор инициализации) недостаточен.

Улучшение с помощью типов данных:
```python
class EncryptionKey:
    def __init__(self, key: bytes):
        # Проверка длины ключа, генерация безопасного ключа
        pass

class InitializationVector:
    def __init__(self, iv: bytes):
        # Проверка длины и безопасности вектора инициализации
        pass

def encrypt(data: bytes, key: EncryptionKey, iv: InitializationVector) -> bytes:
    pass
```

Теперь интерфейс четко указывает, что параметры `key` и `iv` должны соответствовать строгим требованиям безопасности.

### Пример 2

```python
def begin_transaction():
    pass

def commit_transaction():
    pass

def rollback_transaction():
    pass
```

Простые функции не учитывают возможные состояния транзакций и неявные зависимости между ними.

Улучшение с помощью типов данных:
```python
class Transaction:
    def __init__(self):
        self.active = False

    def begin(self):
        self.active = True

    def commit(self):
        if not self.active:
            raise Exception("No active transaction to commit")
        # Завершение транзакции
        self.active = False

    def rollback(self):
        if not self.active:
            raise Exception("No active transaction to rollback")
        # Откат транзакции
        self.active = False
```

Теперь интерфейс гарантирует, что транзакции управляются корректно, а ошибки использования минимизированы.

### Пример 3

```python
def check_access(user_id, resource_id, action):
    # Проверка прав доступа пользователя к ресурсу
    pass
```

Простой интерфейс, принимающий ID пользователя, ID ресурса и действие, не учитывает всех возможных сложностей, связанных с управлением доступом. Например, у пользователя могут быть разные роли в зависимости от контекста.

Улучшение с помощью типов данных:
```python
from typing import List, Optional

class Role:
    def __init__(self, name: str, permissions: List[str]):
        self.name = name
        self.permissions = permissions

class User:
    def __init__(self, user_id: str, roles: List[Role]):
        self.user_id = user_id
        self.roles = roles

    def has_permission(self, action: str, resource: 'Resource') -> bool:
        for role in self.roles:
            if action in role.permissions:
                return True
        return False

class Resource:
    def __init__(self, resource_id: str, required_permissions: List[str]):
        self.resource_id = resource_id
        self.required_permissions = required_permissions

class AccessControl:
    def check_access(self, user: User, resource: Resource, action: str) -> bool:
        return user.has_permission(action, resource)
```

В данном случае усложнение интерфейса помогает более точно управлять доступом в системе, особенно в сложных сценариях. Использование подходящих типов данных делает интерфейс более понятным.

---
## Выводы

Для меня упражнения оказались довольно сложными, но интересными. Не сразу смог понять что от меня требуется. 
Довольно показательны были все 3 случая. Ранее я никогда сильно не акцентировал внимание на интерфейс. 

Понял, что использование более сложных структур данных и явное отражение всех аспектов логики в интерфейсе помогает создавать более надежные и понятные системы, которые легче поддерживать и расширять в будущем.