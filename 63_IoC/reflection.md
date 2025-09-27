# Функциональные интерфейсы

## 1. Конфигурация системы

Было (императивный билдер с состоянием):
```python
class DatabaseConfigBuilder:
    def __init__(self):
        self._host = "localhost"
        self._port = 5432
        self._timeout = 30
    
    def with_host(self, host: str) -> 'DatabaseConfigBuilder':
        self._host = host
        return self  # Мутация состояния + возврат self для чейнинга
    
    def with_port(self, port: int) -> 'DatabaseConfigBuilder':
        self._port = port
        return self
    
    def build(self) -> dict:
        return {
            "host": self._host,
            "port": self._port,
            "timeout": self._timeout
        }

# Использование (проблема: состояние меняется в процессе)
builder = DatabaseConfigBuilder()
config = builder.with_host("db.prod.com").with_port(6432).build()
# Проблема: builder теперь в изменённом состоянии, нельзя переиспользовать
```

Стало (чистые функции с инверсией контроля):

```python
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)  # Иммутабельный конфиг
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    timeout: int = 30

# Чистые функции-трансформеры (как в ФП)
def with_host(config: DatabaseConfig, host: str) -> DatabaseConfig:
    return DatabaseConfig(host=host, port=config.port, timeout=config.timeout)

def with_port(config: DatabaseConfig, port: int) -> DatabaseConfig:
    return DatabaseConfig(host=config.host, port=port, timeout=config.timeout)

# Более функциональный подход: композиция трансформеров
def apply_transforms(initial: DatabaseConfig, 
                    transforms: list[Callable[[DatabaseConfig], DatabaseConfig]]) -> DatabaseConfig:
    from functools import reduce
    return reduce(lambda cfg, transform: transform(cfg), transforms, initial)

# Использование (полный контроль у вызывающей стороны)
config = apply_transforms(
    DatabaseConfig(),
    [lambda cfg: with_host(cfg, "db.prod.com"), 
     lambda cfg: with_port(cfg, 6432)]
)
```
Инверсия контроля: Теперь вызывающий код полностью контролирует процесс преобразования.  
Иммутабельность: DatabaseConfig неизменяем, можно безопасно передавать между потоками.  
Тестируемость: Каждую функцию-трансформер можно тестировать изолированно.  
Композируемость: Трансформеры можно комбинировать в любом порядке.  

## 2. Валидация данных

Было (валидатор с накоплением ошибок):
```python
class UserValidator:
    def __init__(self):
        self._errors = []  # Мутабельное состояние!
    
    def validate_name(self, name: str) -> bool:
        if len(name) < 2:
            self._errors.append("Name too short")
            return False
        return True
    
    def validate_email(self, email: str) -> bool:
        if "@" not in email:
            self._errors.append("Invalid email")
            return False
        return True
    
    def get_errors(self) -> list[str]:
        return self._errors

# Проблема: состояние валидатора меняется при вызовах
validator = UserValidator()
validator.validate_name("A")  # Добавляет ошибку
validator.validate_email("invalid")  # Добавляет ещё ошибку
errors = validator.get_errors()  # ["Name too short", "Invalid email"]
```

Стало (чистые функции валидации):
```python
from typing import Tuple, List

# Валидатор возвращает кортеж (успех, ошибки) вместо мутации состояния
def validate_name(name: str) -> Tuple[bool, List[str]]:
    if len(name) < 2:
        return False, ["Name too short"]
    return True, []

def validate_email(email: str) -> Tuple[bool, List[str]]:
    if "@" not in email:
        return False, ["Invalid email"]
    return True, []

# Композиция валидаторов (чистая функция)
def validate_user(name: str, email: str) -> Tuple[bool, List[str]]:
    name_ok, name_errors = validate_name(name)
    email_ok, email_errors = validate_email(email)
    
    all_ok = name_ok and email_ok
    all_errors = name_errors + email_errors
    
    return all_ok, all_errors

# Более функциональный подход с монадической композицией
def validate_all(validators: list[Callable[[], Tuple[bool, List[str]]]]) -> Tuple[bool, List[str]]:
    from functools import reduce
    return reduce(
        lambda acc, validator: (acc[0] and validator()[0], acc[1] + validator()[1]),
        validators,
        (True, [])
    )
```
Предсказуемость: Результат зависит только от входных данных.  
Параллелизм: Можно запускать валидаторы параллельно.  
Композиция: Легко комбинировать разные валидаторы.  

## 3. Обработка pipeline данных

Было (процессор с состоянием):

```python
class DataProcessor:
    def __init__(self):
        self._data = None
        self._results = []
    
    def load_data(self, data: list) -> 'DataProcessor':
        self._data = data
        return self
    
    def filter_positive(self) -> 'DataProcessor':
        self._data = [x for x in self._data if x > 0]  # Мутация!
        return self
    
    def square_values(self) -> 'DataProcessor':
        self._data = [x*x for x in self._data]  # Мутация!
        return self
    
    def get_result(self) -> list:
        return self._data

# Цепочка мутаций (сложно отслеживать состояние)
processor = DataProcessor()
result = processor.load_data([-1, 2, -3, 4]).filter_positive().square_values().get_result()
# [4, 16]
```

Стало (чистые трансформации):
```python
from typing import TypeVar, Callable

T = TypeVar('T')

# Чистые функции-трансформеры
def filter_positive(data: list[int]) -> list[int]:
    return [x for x in data if x > 0]

def square_values(data: list[int]) -> list[int]:
    return [x*x for x in data]

# Композиция pipeline (инверсия контроля)
def create_pipeline(transformations: list[Callable[[list[int]], list[int]]]) -> Callable[[list[int]], list[int]]:
    def pipeline(data: list[int]) -> list[int]:
        result = data
        for transform in transformations:
            result = transform(result)
        return result
    return pipeline

# Использование (полный контроль над pipeline)
pipeline = create_pipeline([filter_positive, square_values])
result = pipeline([-1, 2, -3, 4])  # [4, 16]

# Или более функционально с functools.reduce
from functools import reduce
def functional_pipeline(data: list[int], transforms: list) -> list[int]:
    return reduce(lambda acc, f: f(acc), transforms, data)
```

## 4. Кэширование

Было (кэш с внутренним состоянием):
```python
class Cache:
    def __init__(self):
        self._storage = {}
    
    def get(self, key: str) -> any:
        return self._storage.get(key)
    
    def set(self, key: str, value: any) -> None:
        self._storage[key] = value  # Мутация!

# Проблема: тестирование, параллелизм, неявные зависимости
cache = Cache()
cache.set("user:1", {"name": "John"})
user = cache.get("user:1")
```

Стало (функциональный интерфейс):
```python
from typing import Tuple, Dict

# Чистые функции работают с кэшем как с данными
def cache_get(cache: Dict[str, any], key: str) -> Tuple[any, Dict[str, any]]:
    # Возвращаем значение и неизменённый кэш
    return cache.get(key), cache

def cache_set(cache: Dict[str, any], key: str, value: any) -> Dict[str, any]:
    # Возвращаем НОВЫЙ кэш (старый не изменяем)
    new_cache = cache.copy()
    new_cache[key] = value
    return new_cache

# Использование (явное управление состоянием)
cache = {}
value, cache = cache_get(cache, "user:1")  # None, {}
cache = cache_set(cache, "user:1", {"name": "John"})
value, cache = cache_get(cache, "user:1")  # {"name": "John"}, {...}
```

Детерминированность: Результат зависит только от входных данных.  
Тестируемость: Легко тестировать каждую функцию изолированно.  
Параллелизм: Можно безопасно использовать в многопоточном коде.  
Отладка: Легко отслеживать изменения состояния.  

## Выводы 

Когда я писал классы с изменяемым состоянием (`add_source`, `self.data = ...` и т.д.), то это казалось нормальным. Но при переписывании я увидел, что реально теряешь контроль: в любой момент кто-то может поменять объект, и уже не ясно, какое у него состояние.

С функциями легче писать юнит-тесты: просто даёшь вход и смотришь на выход. В варианте с мутабельными объектами нужно следить за побочными эффектами, что сложнее.

Даже если под капотом где-то используется мутабельность, наружу можно показать чистый и удобный интерфейс. Такое разделение реально снижает хаос в коде.