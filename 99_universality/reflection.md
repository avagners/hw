# Универсальность: когда её мало, а когда слишком много

Материал «ООП как средство повторного использования кода» (94) про баланс: универсальность - не самоцель. Слишком специфичный код не переиспользуется (его копипастят), а слишком универсальный - раздувается до состояния, когда его невозможно эксплуатировать. Разберу по три примера из своих проектов (данные/ETL), где я попадал в обе крайности.

## Часть 1. Универсальности явно маловато

### Пример 1. Копипаст загрузчиков под каждую таблицу

Когда у меня впервые появились витрины в Postgres, я наивно написал отдельную функцию под каждую таблицу:

```python
# ПЛОХО: под каждую новую таблицу - новая функция-копия
def load_users(df):
    conn = get_pg_conn()
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                "INSERT INTO users (id, name, email) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                (row["id"], row["name"], row["email"]),
            )
    conn.commit()

def load_orders(df):
    conn = get_pg_conn()
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(
                "INSERT INTO orders (id, user_id, total) VALUES (%s, %s, %s) "
                "ON CONFLICT (id) DO NOTHING",
                (row["id"], row["user_id"], row["total"]),
            )
    conn.commit()

# Новая таблица -> новый copy-paste с другой парой строк.
# Ошибку в логике коннекта приходилось чинить в каждой копии.
```

Универсальности не хватило ровно на один параметр - имя таблицы и список колонок:

```python
# ХОРОШО: одна маленькая, но параметризованная функция
def load_to_postgres(df: pd.DataFrame, table: str, columns: list[str], conflict_cols: list[str]):
    placeholders = ", ".join(["%s"] * len(columns))
    col_list = ", ".join(columns)
    conflict = ", ".join(conflict_cols)
    sql = (f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
           f"ON CONFLICT ({conflict}) DO NOTHING")
    conn = get_pg_conn()
    with conn.cursor() as cur:
        for _, row in df.iterrows():
            cur.execute(sql, tuple(row[col] for col in columns))
    conn.commit()

load_to_postgres(users, "users", ["id", "name", "email"], ["id"])
load_to_postgres(orders, "orders", ["id", "user_id", "total"], ["id"])
```

### Пример 2. Трансформация, захардкоженная под одну витрину

Аналогичная история с агрегациями: под каждый отчёт я писал почти идентичную функцию, отличающуюся только фильтром по типу события и именем колонки-результата.

```python
# ПЛОХО: «аналитика» захардкожена под один конкретный отчёт
def build_daily_clicks(df):
    return (
        df.filter(F.col("event") == "click")
          .groupBy("user_id", F.to_date("ts").alias("day"))
          .agg(F.count("*").alias("clicks"))
    )

def build_daily_orders(df):
    return (
        df.filter(F.col("event") == "order")
          .groupBy("user_id", F.to_date("ts").alias("day"))
          .agg(F.count("*").alias("orders"))
    )

# Третий отчёт -> третья копия. Ошибку (например, сдвиг по часовому поясу
# в F.to_date) правили в трёх местах.
```

Достаточно было вынести в параметры то, что реально отличается:

```python
# ХОРОШО: одна функция, отличающееся - это параметры
def count_events_by_day(df, event: str, result_alias: str):
    return (
        df.filter(F.col("event") == event)
          .groupBy("user_id", F.to_date("ts").alias("day"))
          .agg(F.count("*").alias(result_alias))
    )
```

### Пример 3. Хардкод источника данных

Классика: функция читала данные из «прибитого» пути, и для второго проекта её приходилось не переиспользовать, а копировать с заменой одной строки.

```python
# ПЛОХО: функция прибита к одному бакету
def read_events(date: str) -> pd.DataFrame:
    return pd.read_parquet(f"s3://team-a-bucket/events/dt={date}/")

# Второй проект, другой бакет -> скопировали и поменяли строку
def read_events_proj_b(date: str) -> pd.DataFrame:
    return pd.read_parquet(f"s3://team-b-bucket/raw/events/dt={date}/")
```

Исправление - вынести изменяющуюся часть в аргумент:

```python
# ХОРОШО: базовый путь - параметр, функция переиспользуется везде
def read_parquet_dir(base_path: str, date: str) -> pd.DataFrame:
    return pd.read_parquet(f"{base_path.rstrip('/')}/dt={date}/")

read_parquet_dir("s3://team-a-bucket/events", "2026-08-10")
read_parquet_dir("s3://team-b-bucket/raw/events", "2026-08-10")
```

## Часть 2. Универсальности явно многовато

### Пример 1. Функция-«швейцарский нож» с десятком параметров

В одном из проектов я решил, что напишу одну-единственную «универсальную» функцию ингеста, которая закроет все сценарии разом:

```python
# ПЛОХО: одна «универсальная» функция на все случаи жизни
def ingest(
    source: str,
    target: str,
    source_format: str = "parquet",
    target_format: str = "parquet",
    read_options: dict | None = None,
    write_options: dict | None = None,
    schema: str | None = None,
    partition_cols: list[str] | None = None,
    write_mode: str = "overwrite",
    repartition: int | None = None,
    validate: bool = False,
    null_threshold: float = 0.05,
    deduplicate: bool = False,
    dedup_keys: list[str] | None = None,
    retries: int = 0,
    retry_delay_s: float = 5.0,
    metrics: bool = True,
    metrics_namespace: str = "etl",
    notify: bool = False,
    notify_channel: str = "#etl",
    **kwargs,
):
    # ... 200 строк логики, где комбинации флагов влияют друг на друга
```

Каждый вызов превращался в простыню из kwargs, которую невозможно было запомнить. Отладка стала кошмаром: чтобы понять, что произошло, надо было восстановить, какая комбинация флагов привела к результату. А починка одного сценария ломала другой. Поверхность контакта выросла настолько, что функция стала фактически «универсальной», но неиспользуемой - каждый новый разработчик переписывал её кусок под себя.

Лучше - маленькие сфокусированные компоненты с лаконичным API, собранные композицией:

```python
# ХОРОШО: три маленьких компонента вместо одного монолита
class ParquetReader:
    def __init__(self, base_path: str):
        self.base_path = base_path
    def read(self, date: str) -> pd.DataFrame:
        ...

class Validator:
    def __init__(self, null_threshold: float = 0.05):
        self.null_threshold = null_threshold
    def validate(self, df: pd.DataFrame) -> None:
        ...

class PostgresSink:
    def __init__(self, table: str):
        self.table = table
    def write(self, df: pd.DataFrame) -> None:
        ...

def run_ingest(date: str):
    df = ParquetReader("s3://bucket/events").read(date)
    Validator().validate(df)
    PostgresSink("events").write(df)
```

### Пример 2. Интерфейс ради интерфейса (YAGNI)

Под влиянием «программируйте под интерфейс» я ввёл абстрактный класс для хранилища, хотя реализация на тот момент была ровно одна:

```python
# ПЛОХО: интерфейс введён «на всякий случай», реализация ровно одна
class IDataSink(ABC):
    @abstractmethod
    def write(self, df: pd.DataFrame) -> None: ...
    @abstractmethod
    def read(self, path: str) -> pd.DataFrame: ...
    @abstractmethod
    def exists(self, path: str) -> bool: ...

class S3DataSink(IDataSink):
    def write(self, df): ...
    def read(self, path): ...
    def exists(self, path): ...
```

За два года вторая реализация (GCS, Azure) так и не появилась. Зато каждый клиент был вынужден тянуть интерфейс с тремя методами, мокать его в тестах и ходить по кругам ада, когда менялась сигнатура `read`. Интерфейс не скрывал сложность - он добавлял её.

```python
# ХОРОШО: пока реализация одна, клиенты работают с конкретным классом
class S3DataSink:
    def write(self, df: pd.DataFrame) -> None: ...
    def read(self, path: str) -> pd.DataFrame: ...
    def exists(self, path: str) -> bool: ...

# Когда появится реальная вторая реализация - вот тогда и выделим интерфейс
```

### Пример 3. «Универсальный» движок на YAML-конфиге

Самое больное: я написал движок, который «умел всё» и управлялся конфигом, чтобы не трогать код при добавлении новых пайплайнов:

```python
# ПЛОХО: «универсальный» движок, управляемый YAML-конфигом
class PipelineEngine:
    def __init__(self, config_path: str):
        self.config = yaml.safe_load(Path(config_path).read_text())
        self._current = None

    def run(self):
        for step in self.config["steps"]:
            module = importlib.import_module(step["module"])
            fn = getattr(module, step["fn"])
            self._current = fn(self._current, **step.get("kwargs", {}))
        return self._current

# «Гибко», но на практике:
# - поток данных не виден в коде, только в YAML;
# - опечатка в конфиге -> рантайм-ошибка в проде;
# - нельзя отладить шаг, не прогнав весь пайплайн;
# - движок по факту использовал один человек на три пайплайна.
```

Проблема ровно из материала: универсальность выросла до уровня, когда каждый новый случай требует «широкого» конфига, отладка усложняется, и в итоге система настолько сложна, что её никто не использует. Явный код с композицией маленьких шагов проще, переиспользуемее и отлаживаемее:

```python
# ХОРОШО: явная композиция простых функций
def run():
    raw = read_raw()
    cleaned = clean(raw)
    aggregated = aggregate(cleaned)
    load(aggregated)
```

## Выводы

Раньше я считал, что повторное использование достигается либо максимальной обобщённостью (всё через конфиг и параметры), либо копированием кода в новый проект. Обе крайности я прошёл на собственных граблях. Когда универсальности мало - код размножается копипастом, и каждая ошибка чинится в N местах. Когда универсальности много - API раздувается, комбинации параметров непредсказуемы, отладка превращается в детектив, и компонент в итоге никто не переиспользует, потому что не может разобраться, как им пользоваться.

Теперь я действую так: начинаю с узкой, сфокусированной версии компонента, который делает одну вещь, и только когда вижу 2-3 реальных дублирования одного и того же - выношу общее в параметры или в маленький компонент. Не ввожу абстракции и интерфейсы «на вырост» (YAGNI): интерфейс появляется только когда есть реальная вторая реализация. Стараюсь строить пайплайны из маленьких, слабо связанных компонентов с высоким сцеплением и лаконичным API, а не из монолитного «движка». И, главное, перестал бояться рефакторинга: лучше вовремя разбить разросшийся компонент, чем тянуть его как единый универсальный монолит.
