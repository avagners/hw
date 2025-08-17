# Применяем функциональную композицию правильно

## Пример 1. Очистка данных (валидация + нормализация)

До (ООП-наследование)
Минусы: глубокое наследование ради последовательности шагов. Чтобы добавить новый шаг — новый класс.
```python
class BaseCleaner:
    def clean(self, row: dict) -> dict:
        return row

class TrimCleaner(BaseCleaner):
    def clean(self, row: dict) -> dict:
        row["name"] = row["name"].strip()
        return row

class LowercaseCleaner(TrimCleaner):
    def clean(self, row: dict) -> dict:
        row = super().clean(row)
        row["email"] = row["email"].lower()
        return row
```

После (функциональная композиция)
Теперь шаги чистки = обычные функции, комбинируемые как LEGO.
```python
def trim_name(row: dict) -> dict:
    row["name"] = row["name"].strip()
    return row

def lowercase_email(row: dict) -> dict:
    row["email"] = row["email"].lower()
    return row

def compose(*funcs):
    def wrapper(data):
        for f in funcs:
            data = f(data)
        return data
    return wrapper

clean_row = compose(trim_name, lowercase_email)

row = {"name": " Alice  ", "email": "ALICE@EXAMPLE.COM"}
print(clean_row(row))  # {'name': 'Alice', 'email': 'alice@example.com'}
```

## Пример 2. Трансформации колонок в Pandas

До (ООП-класс со множеством методов)
Минусы: «флюентный» API → фактически нагромождение методов, сильное сцепление.
```python
class Transformer:
    def __init__(self, df):
        self.df = df

    def add_full_name(self):
        self.df["full_name"] = self.df["first"] + " " + self.df["last"]
        return self

    def normalize_age(self):
        self.df["age"] = self.df["age"].fillna(0).astype(int)
        return self

    def run(self):
        return self.df
```

После (функции)
Пайплайн = простая композиция функций. Можно переставлять шаги, убирать, добавлять — без наследования и лишних классов.
```python
import pandas as pd

def add_full_name(df):
    df["full_name"] = df["first"] + " " + df["last"]
    return df

def normalize_age(df):
    df["age"] = df["age"].fillna(0).astype(int)
    return df

def pipeline(df, *steps):
    for step in steps:
        df = step(df)
    return df

df = pd.DataFrame([{"first": "Bob", "last": "Lee", "age": None}])
result = pipeline(df, add_full_name, normalize_age)
print(result)
```

## Пример 3. Загрузка данных в разные хранилища

До (стратегия через классы)
Минусы: «полиморфизм ради полиморфизма». Нужно два класса, чтобы сделать print().
```python
class Loader:
    def load(self, data):
        raise NotImplementedError

class S3Loader(Loader):
    def load(self, data):
        print("Upload to S3")

class PostgresLoader(Loader):
    def load(self, data):
        print("Insert into Postgres")

class Pipeline:
    def __init__(self, loader: Loader):
        self.loader = loader

    def run(self, data):
        self.loader.load(data)
```

После (функции)
Просто передаём функцию загрузки.

```python
def load_to_s3(data):
    print("Upload to S3")

def load_to_postgres(data):
    print("Insert into Postgres")

def pipeline(data, loader):
    loader(data)

pipeline({"x": 1}, load_to_s3)
pipeline({"x": 1}, load_to_postgres)
```
Плагины можно хранить в словаре:
```python
loaders = {"s3": load_to_s3, "pg": load_to_postgres}
pipeline({"y": 2}, loaders["pg"])
```

## Пример 4. Валидация и преобразование данных (Data Contracts)

До (громоздкий класс)
```python
class Validator:
    def __init__(self, rules):
        self.rules = rules

    def validate(self, row):
        for field, func in self.rules.items():
            if not func(row[field]):
                raise ValueError(f"Invalid {field}")
        return row
```

После (функциональная композиция)
```python
def validate_age(row):
    if row["age"] < 0:
        raise ValueError("Invalid age")
    return row

def validate_email(row):
    if "@" not in row["email"]:
        raise ValueError("Invalid email")
    return row

validate = compose(validate_age, validate_email)

row = {"age": 30, "email": "test@example.com"}
print(validate(row))  # OK
```

Проверки = функции, которые можно переставлять, отключать, расширять.

## Выводы

Для инженера данных «вытопить жир» через функции удобно в задачах:
- Очистка и валидация записей (dict → dict);
- Трансформации DataFrame (пошаговые функции вместо методов-классов);
- Лоадеры (простые функции вместо стратегий-наследников);
- Data Contracts (валидации как композиции функций).

Главная фишка - всё плоско, легко тестируется и заменяется.
ООП здесь часто только добавляет «архитектурности ради архитектурности».

Также, нужно зарубить на носу -> 
"Единственный случай, когда действительно полезно использовать наследование: когда вам нужно создавать экземпляры как родительского, так и дочернего классов, и передавать их одним и тем же функциям. Т.е. когда в проекте явно напрашивается полиморфизм подтипов. Точка." 
В остальных случаях используем композицию. 

Про DI.
Он не всегда нужен. DI имеет смысл там, где реально есть разные реализации (например, разные базы данных или платёжные шлюзы). Но когда я могу просто передать функцию в пайплайн - DI избыточен.

Главная ценность функциональной композиции - плоские зависимости.
Композиция функций позволяет избежать «деревьев классов», и код получается более предсказуемым.
Функциональная композиция - это не просто «ещё один стиль». Это способ "вытопить жир" из кода и оставить только главное.
