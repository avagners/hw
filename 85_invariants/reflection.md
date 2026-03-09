# Инварианты и качественный код

## Пример 1

Каждый загруженный датафрейм содержит все обязательные колонки, причём они непустые.

```python
import pandas as pd

class RawDataFrame:
    REQUIRED_COLUMNS = {"id", "timestamp", "event_type"}

    def __init__(self, df: pd.DataFrame):
        assert isinstance(df, pd.DataFrame), "Данные должны быть pandas DataFrame"
        # все обязательные колонки присутствуют
        assert self.REQUIRED_COLUMNS.issubset(df.columns), \
            f"Отсутствуют колонки: {self.REQUIRED_COLUMNS - set(df.columns)}"
        # нет полностью пустых обязательных колонок
        for col in self.REQUIRED_COLUMNS:
            assert not df[col].isnull().all(), f"Колонка {col} полностью пустая"
        self._df = df

    @property
    def data(self):
        return self._df

    def filter_by_event(self, event: str):
        # Метод сохраняет инвариант, т.к. колонки не удаляются
        filtered = self._df[self._df["event_type"] == event].copy()
        return RawDataFrame(filtered)

    def __repr__(self):
        return f"RawDataFrame(shape={self._df.shape}, columns={list(self._df.columns)})"


# Использование
df = pd.DataFrame({
    "id": [1, 2, 3],
    "timestamp": ["2026-01-01", "2026-01-02", "2026-01-03"],
    "event_type": ["click", "view", "click"],
    "extra": [10, 20, 30]
})

raw = RawDataFrame(df)
print(raw)
# RawDataFrame(shape=(3, 4), columns=['id', 'timestamp', 'event_type', 'extra'])

clicks = raw.filter_by_event("click")
print(clicks.data[["id", "event_type"]])
```

## Пример 2

Все загружаемые файлы имеют одинаковую схему (одинаковые колонки с одинаковыми типами).

```python
import pyarrow.parquet as pq
import pyarrow as pa

class ConsistentSchemaDataset:
    def __init__(self, file_paths: list[str]):
        assert len(file_paths) > 0, "Нет файлов для загрузки"
        
        # Читаем схему первого файла как эталон
        self.base_schema = pq.read_schema(file_paths[0])
        self.base_columns = set(self.base_schema.names)
        
        # Проверяем все остальные файлы
        for path in file_paths[1:]:
            schema = pq.read_schema(path)
            assert set(schema.names) == self.base_columns, \
                f"Файл {path} имеет другие колонки: {set(schema.names) ^ self.base_columns}"
            
            # Проверяем типы
            for field in schema:
                base_field = self.base_schema.field(field.name)
                assert field.type == base_field.type, \
                    f"Колонка {field.name} в {path} имеет тип {field.type}, ожидался {base_field.type}"
        
        self.file_paths = file_paths
        self._tables = None

    def load_all(self):
        if self._tables is None:
            tables = [pq.read_table(p) for p in self.file_paths]
            self._tables = pa.concat_tables(tables)
        return self._tables


# Использование
files = ["data1.parquet", "data2.parquet", "data3.parquet"]
try:
    ds = ConsistentSchemaDataset(files)
    full_table = ds.load_all()
except AssertionError as e:
    print(f"Схема разъехалась: {e}")
```

## Пример 3

Email всегда валидный (содержит @, имеет домен, нет пробелов, в нижнем регистре).
Невозможно создать объект  User с некорректным email.

```python
import re
from dataclasses import dataclass

class Email:
    def __init__(self, value: str):
        assert isinstance(value, str), "Email должен быть строкой"
        value = value.strip().lower()
        
        # Проверка формата
        assert re.match(r"^[^@]+@[^@]+\.[^@]+$", value), \
            f"Некорректный формат email: {value}"
        
        # Проверка что нет пробелов внутри
        assert " " not in value, "Email не должен содержать пробелов"
        
        # локальная часть не пустая
        local, domain = value.split("@")
        assert len(local) > 0, "Локальная часть email не может быть пустой"
        assert len(domain) > 0, "Домен email не может быть пустым"
        assert "." in domain, "Домен должен содержать точку"
        
        self._value = value

    @property
    def value(self):
        return self._value

    @property
    def domain(self):
        return self._value.split("@")[1]

    def __eq__(self, other):
        if not isinstance(other, Email):
            return False
        return self._value == other._value

    def __hash__(self):
        return hash(self._value)

    def __repr__(self):
        return f"Email({self._value})"


# Использование Email в User
class User:
    def __init__(self, user_id: int, email: Email, name: str):
        self.user_id = user_id
        self.email = email  # Инвариант уже в типе
        self.name = name

    def change_email(self, new_email: Email):
        # Не надо ничего проверять. Email уже гарантирует корректность
        self.email = new_email
        assert isinstance(self.email, Email), "Инвариант нарушен: email не того типа"


# Использование
email = Email("  Test@Example.COM  ")
print(email)  # Email(test@example.com)
print(email.domain)  # example.com

user = User(1, email, "Тест")
print(user.email.value)  # test@example.com

# Попытка создать невалидный email
# Email("not-an-email")  # AssertionError
# Email("user@")  # AssertionError
# Email("@domain.com")  # AssertionError
```

## Выводы

Раньше я думал, что проверю email в том месте, где он нужен. А потом это место менялось, появлялись новые точки входа (API, админка, импорт из Excel), и в какой-то момент я забывал поставить проверку. Теперь Email - это отдельный класс. Если объект создался, то он однозначно корректен и никакие проверки в логике не нужны.

Я думал что ставить assert это нехорошая практика, так как вокруг так никто не делал. Или если и использовали, то только во время разработки, а перед деплоем на прод все подчищали. Теперь понимаю, что это было неверно. 

Если assert сработал в проде - это значит, что это ошибка в логике, и лучше упасть сразу, чем считать дальше с кривыми данными.
Ассерты - это как тесты, но только встроенные прямо в код.

Сделать недопустимые состояния непредставимыми - это настоящее мастерство. Ранее я был вынужден везде писать проверки на допустимое состояние. То сейчас объекты с недопустимым состоянием просто не будут созданы. Если объект создан, то я уверен что объект валидный и проверки не нужны.

Какую привычку следует привить в работе?
Прежде чем писать метод, спросить себя: «А какой здесь инвариант?»
Инвариант добавлять в конструктор.
При изменении состояния объекта лучше возвращать новый объект.
Не стесняться писать ассерты. Особенно после сложных вычислений, перед возвратом результата, в методах, которые меняют состояние, в конструкторах. Если инвариант сложный, то выносить в отдельный класс-обёртку.

С такой работой данные получаются как детальки LEGO. Если деталька существует, то она уже правильной формы и с нужным креплением, и её можно соединять с другими без страха, что всё развалится.
