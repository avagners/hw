# Некорректное использование исключений в коде

## Основные принципы

1. **Исходное назначение исключений**: обработка ошибок внешних ресурсов (файлы, сеть, БД) или отладка
2. **Не использовать для управления логикой программы**: вместо `try-except` использовать `if`
3. **Не генерировать исключения для**:
   - Некорректных аргументов функции (лучше коды ошибок)
   - Ситуаций без ошибок (чтобы сэкономить строки кода)
   - Избегания рефакторинга

---

## Примет 1. Валидация в доменной модели — `BucketName.py`

**Проблема:** Использование исключений для валидации аргументов конструктора

```python
def _validate_english_letters(self, name: str):
    if not name.isalpha() and not name.isascii():
        raise exceptions.BuketNameError.because_name_contains_non_english_letters()

def _validate_length_name(self, name: str):
    if len(name) > self._LENGTH:
        raise exceptions.BuketNameError.because_length_longer_than(...)
```

**Почему неправильно:** Это не исключительная ситуация, а обычная валидация входных данных.

**Исправление:**

```python
from typing import Optional, Tuple

class BucketName(ValueObject):
    _LENGTH = 50

    def __init__(self, name: str):
        self._name = name

    @classmethod
    def create(cls, name: str) -> Tuple[Optional["BucketName"], Optional[str]]:
        if len(name) > cls._LENGTH:
            return None, f"Длина имени превышает {cls._LENGTH} символов"
        if not name.isalpha() or not name.isascii():
            return None, "Имя содержит недопустимые символы"
        return cls(name), None

    def get_name(self) -> str:
        return self._name
```

---

## Пример 2. Валидация в доменной модели — `Role.py`

**Проблема:** Исключение для валидации аргумента

```python
def __post_init__(self):
    if not isinstance(self.role_name, str) or not self.role_name.strip():
        raise ValueError("Role name not NULL.")
```

**Почему неправильно:** Проверка входных данных, а не обработка исключительной ситуации.

**Исправление:**

```python
@dataclasses.dataclass(frozen=True)
class Role:
    role_name: str

    @classmethod
    def create(cls, role_name: str) -> typing.Tuple[typing.Optional["Role"], typing.Optional[str]]:
        if not isinstance(role_name, str) or not role_name.strip():
            return None, "Имя роли должно быть непустой строкой"
        return cls(role_name=role_name), None
```

---

## Пример 3. Валидация в DTO — `CloseAccessTeamBucketResource.py`

**Проблема:** Pydantic валидатор выбрасывает исключение вместо встроенных механизмов

```python
@field_validator("roles")
def validate_roles(cls, value):
    if value is None:
        raise ValidationError("The 'roles' field cannot be None.")
    elif not value:
        raise ValidationError("The 'roles' field cannot be empty.")
    return value
```

**Почему неправильно:** Pydantic уже имеет встроенные механизмы валидации через `Field`.

**Исправление:**

```python
from pydantic import BaseModel, Field

class CloseAccessTeamBucketResource(BaseModel):
    order_id: str = Field(
        title="Order ID",
        description="Unique identifier for the order."
    )
    roles: typing.List[str] = Field(
        title="Roles",
        description="List of roles associated with the bucket.",
        min_length=1  # Встроенная валидация
    )
```

---

## Пример 5. Обёртка исключений без добавления ценности — `ARangerAccessControlClientAdapter.py`

**Проблема:** Бессмысленная обёртка исключений

```python
async def check_access(self, location: str) -> bool:
    try:
        return await self._ranger_client.exists_access(location)
    except Exception as e:
        raise AccessControlClientException(f"Apache Ranger check_access error: {e}")
```

**Почему неправильно:**
- Перехватывает ВСЕ исключения без разбора
- Не добавляет новой информации, только переименовывает
- Согласно статье: try-catch для внешних ресурсов с конкретной целью

**Исправление:**

```python
async def check_access(self, location: str) -> bool:
    """Возвращает False при ошибке доступа, позволяя вызывающему коду решить."""
    try:
        return await self._ranger_client.exists_access(location)
    except Exception:
        logger.exception(f"Ошибка проверки доступа для {location}")
        return False  # Безопасное значение: доступ запрещён при ошибке
```

---

## Пример 5. Глобальный перехват Exception в репозитории — `BucketRepository.py`

**Проблема:** Обернуть всё в `try-except Exception` и выбросить своё — антипаттерн

```python
async def _add(self, bucket: Bucket) -> None:
    try:
        stream_name = self._stream_name_for(bucket.id)
        await self._event_store.create_new_stream(stream_name, bucket.changes)
    except Exception as e:
        raise exceptions.BucketDatabaseOperationError(e) from e
```

**Почему неправильно:**
- Перехватывает ВСЕ исключения, включая системные
- Нет обработки — только переименование
- Согласно статье: try-catch только для внешних ресурсов с конкретной целью

**Исправление:**

```python
async def _add(self, bucket: Bucket) -> None:
    """Добавляет новый бакет в хранилище.
    
    Исключения всплывают для обработки на уровне use case.
    """
    stream_name = self._stream_name_for(bucket.id)
    await self._event_store.create_new_stream(stream_name, bucket.changes)
```

Или с конкретной обработкой:

```python
from sqlalchemy.exc import IntegrityError, OperationalError

async def _add(self, bucket: Bucket) -> None:
    stream_name = self._stream_name_for(bucket.id)
    try:
        await self._event_store.create_new_stream(stream_name, bucket.changes)
    except IntegrityError as e:
        logger.error(f"Нарушение целостности при добавлении бакета {bucket.id}: {e}")
        raise
    except OperationalError as e:
        logger.error(f"Ошибка операции БД при добавлении бакета {bucket.id}: {e}")
        raise exceptions.BucketDatabaseOperationError(f"Временная ошибка БД: {e}") from e
```

## Выводы

Главное что я понял, что исключения - это инструмент для обработки ошибок внешних ресурсов, а не для управления логикой программы.
Важно писать детерминированный код, где все пути выполнения видны статически. Где ошибки обрабатываются явно, а не через «магию» исключений.

Теперь я понимаю, что, например, валидация - это не исключительная ситуация. Это нормальный поток данных. Если функция ожидает строку, а получила что-то другое, то это не исключение, это ошибка ввода. Надо вернуть код ошибки явно.

