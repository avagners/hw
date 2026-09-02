# Выявляем хорошие абстракции для интерфейсов

Главный тест «хорошести» интерфейса из материала 96: из него можно собрать осмысленный Composite (и Null Object). Разберу три интерфейса из моих проектов: один тест не проходит, два - проходят.

## Пример 1. Интерфейс, который НЕ проходит тест на композит (толстый обработчик событий)

В проекте с потоковой обработкой событий у меня был «универсальный» интерфейс обработчика:

```python
from typing import Protocol

class EventHandler(Protocol):
    def start(self) -> None: ...
    def handle(self, event: dict) -> bool: ...   # вернуть True = обработано
    def flush(self) -> None: ...
    def get_stats(self) -> dict: ...
    def stop(self) -> None: ...
```

Попытка собрать из него Composite упирается в стену: семантика каждого метода своя, и единого правила объединения нет.

```python
class CompositeHandler:
    """Попытка композита - на каждом методе приходится выдумывать правило."""

    def __init__(self, handlers: list[EventHandler]):
        self._handlers = handlers

    def start(self) -> None:
        for h in self._handlers:
            h.start()                     # ок, все стартуют

    def handle(self, event: dict) -> bool:
        # А что вернуть? Все должны обработать? Хотя бы один?
        # Если первый вернул True - остальные событие НЕ увидят?
        return any(h.handle(event) for h in self._handlers)  # потеряли часть обработчиков!

    def flush(self) -> None:
        for h in self._handlers:
            h.flush()                     # снова ок

    def get_stats(self) -> dict:
        # Складывать? Усреднять? А если у обработчиков разные ключи?
        stats = {}
        for h in self._handlers:
            stats.update(h.get_stats())   # тихие коллизии ключей
        return stats

    def stop(self) -> None:
        for h in self._handlers:
            h.stop()                      # а если stop() одного упал?
```

Проблема не в Composite как таковом, а в интерфейсе: пять сигнатур с разными типами возврата (`None`, `bool`, `dict`) и разной семантикой не оставляют однозначного способа объединить реализации. Null Object тоже бессмысленен: что должен возвращать `get_stats()` у «пустого» обработчика, если других его нигде не используют?

Рефакторинг по материалу: разделить на роли и свести к команде с одной сигнатурой. Тогда Composite и Null Object получаются сами собой.

```python
class Handler(Protocol):
    """Команда: единственный метод, всё - через побочный эффект."""
    def handle(self, event: dict) -> None: ...

class NoopHandler:
    """Null Object: просто игнорирует событие."""
    def handle(self, event: dict) -> None:
        pass

class CompositeHandler:
    """Композит: просто раздаёт событие всем. Правило одно - broadcast."""
    def __init__(self, handlers: list[Handler]):
        self._handlers = handlers

    def handle(self, event: dict) -> None:
        for h in self._handlers:
            h.handle(event)

# Статистику выносим в отдельный ролевой интерфейс-наблюдатель,
# чтобы не смешивать query и command в одной абстракции.
```

Вывод: чем больше сигнатур и чем разнороднее типы возврата, тем хуже интерфейс проходит тест на композит. ISP - это не про «модно», а про компонуемость.

## Пример 2. Интерфейс `T -> T` (замыкание операций) - проходит тест

В ETL-проекте шаги очистки данных я описал одним функциональным интерфейсом:

```python
from typing import Protocol
import pandas as pd

class Cleaner(Protocol):
    def apply(self, df: pd.DataFrame) -> pd.DataFrame: ...
```

Тип входа равен типу выхода - это замыкание операций. Поэтому и Null Object, и Composite реализуются тривиально:

```python
class NoopCleaner:
    """Null Object: вернуть вход как есть."""
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df

class DropNullsCleaner:
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.dropna(subset=["user_id"])

class TrimStringsCleaner:
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        return df.apply(lambda col: col.str.strip() if col.dtype == object else col)

class PipeCleaner:
    """Composite: пайплайн сам является Cleaner'ом и может быть вложенным."""
    def __init__(self, cleaners: list[Cleaner]):
        self._cleaners = cleaners

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        for cleaner in self._cleaners:
            df = cleaner.apply(df)
        return df

class TimingCleaner:
    """Decorator поверх Cleaner - тоже остаётся Cleaner'ом."""
    def __init__(self, inner: Cleaner):
        self._inner = inner

    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        start = time.perf_counter()
        result = self._inner.apply(df)
        logger.info("cleaner took %.3fs", time.perf_counter() - start)
        return result
```

Польза на практике: одна и та же абстракция используется и для отдельного шага, и для всего пайплайна, и для «выключенного» шага (Null Object вместо `if cleaner is not None`):

```python
pipe = PipeCleaner([
    NoopCleaner(),              # шаг временно отключён, но контракт соблюдён
    TimingCleaner(DropNullsCleaner()),
    TrimStringsCleaner(),
])
df = pipe.apply(raw_df)         # PipeCleaner - тоже Cleaner, можно вкладывать
```

## Пример 3. Интерфейс, возвращающий итерируемое, - проходит тест

В проекте миграции данных источники отдавали записи. Интерфейс возвращал `Iterable`, что сразу даёт Null Object (пустая последовательность) и Composite (конкатенация):

```python
from typing import Iterable, Protocol

class RowSource(Protocol):
    def read(self) -> Iterable[dict]: ...

class EmptySource:
    """Null Object: пустая последовательность."""
    def read(self) -> Iterable[dict]:
        return iter(())

class S3ParquetSource:
    def __init__(self, path: str):
        self._path = path

    def read(self) -> Iterable[dict]:
        yield from read_parquet_from_s3(self._path)

class PostgresSource:
    def __init__(self, dsn: str, query: str):
        self._dsn = dsn
        self._query = query

    def read(self) -> Iterable[dict]:
        yield from query_postgres(self._dsn, self._query)

class MergedSource:
    """Composite: записи всех источников подряд - тоже RowSource."""
    def __init__(self, sources: list[RowSource]):
        self._sources = sources

    def read(self) -> Iterable[dict]:
        for source in self._sources:
            yield from source.read()
```

Ключевое преимущество из материала: интерфейсы, возвращающие перечислимые объекты, - почти всегда хорошие абстракции, потому что Null Object - это «ноль элементов», а Composite - «несколько элементов». Мёртвую ветку легко выключить, а новый источник добавить без изменения потребителя:

```python
def build_source(env: str) -> RowSource:
    sources: list[RowSource] = [
        PostgresSource(DSN, "SELECT * FROM users WHERE updated_at > %s"),
    ]
    if env == "prod":
        sources.append(S3ParquetSource("s3://backup/users/"))   # докинуть источник
    return MergedSource(sources)
```

## Выводы

Раньше я проверял интерфейс «на глаз»: «вроде аккуратно, методы осмысленные». Теперь у меня есть конкретный критерий: я мысленно пытаюсь написать Null Object и Composite. Если для этого приходится каждый раз выдумывать новое правило объединения или интерфейс превращается в набор спец-случаев - абстракция плохая, надо резать на роли.

Заметил закономерность из материала: лучше всего тест проходят интерфейсы с одной сигнатурой, где тип входа равен типу выхода (`T -> T`), либо возвращающие итерируемое. Команда (`-> None`) тоже компонуется, но теряешь возможность что-то спросить. А вот «толстые» интерфейсы с query и command вперемешку, с `bool`/`dict`/`None` на выходе - стабильно проваливают тест.

Теперь при проектировании я сразу задаю вопрос: «сможет ли пользователь моего интерфейса собрать из него пайплайн, fallback-цепочку или выключить компонент, не меняя контракт?» Если да - интерфейс, скорее всего, хороший.
