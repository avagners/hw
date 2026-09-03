# ISP без Shallow-интерфейсов и Closure of Operations

## 2. Три интерфейса, полностью соответствующих ISP, но не Shallow

Если свести интерфейс к «абсолютному минимуму по SRP», получится ограниченная функциональность, необходимость постоянно менять интерфейс, утечки абстракции и фасады/адаптеры вокруг каждой мелочи. Значит, «хороший» интерфейс узок по роли (ISP), но при этом «глубок»: содержит все операции своей роли, и каждая операция прячет реальную сложность, а не просто проксирует детали реализации.

### Пример 2.1. BatchIngester - роль «батчевая запись с гарантиями»

```python
from typing import Protocol, Mapping

class BatchIngester(Protocol):
    def add(self, row: Mapping) -> None: ...
    def flush(self) -> int: ...
    def abort(self) -> None: ...
```

```python
class PostgresBatchIngester:
    """Реализация: копит строки в памяти и сбрасывает одним транзакционным COPY."""

    def __init__(self, dsn: str, table: str, batch_size: int = 1000):
        self._dsn = dsn
        self._table = table
        self._batch_size = batch_size
        self._buffer: list[Mapping] = []

    def add(self, row: Mapping) -> None:
        self._buffer.append(row)
        if len(self._buffer) >= self._batch_size:
            self._flush_buffer()

    def flush(self) -> int:
        n = len(self._buffer)
        self._flush_buffer()
        return n

    def abort(self) -> None:
        self._buffer.clear()

    def _flush_buffer(self) -> None:
        # один COPY ... INTO ... в одной транзакции, с ретраями и таймаутами
        ...
```

Почему интерфейс глубокий, а не Shallow: если оставить только `add(row)`, клиенту пришлось бы самому решать, когда сбрасывать батч, и проигрывать атомарность (одна строка упала - как откатить предыдущие?). Пришлось бы лезть в детали реализации - это и есть утечка абстракции. Три операции `add`/`flush`/`abort` закрывают весь сценарий записи: накопил, сбросил, откатил при ошибке.

Почему это ISP: роль одна - «надёжная запись пачками», и клиент один - цикл загрузки. Методов не больше, чем нужно роли, но и не меньше:

```python
def load_all(rows: Iterable[Mapping], ingester: BatchIngester) -> int:
    try:
        for row in rows:
            ingester.add(row)
        return ingester.flush()
    except Exception:
        ingester.abort()
        raise
```

### Пример 2.2. StreamConsumer - роль «чтение с подтверждением»

```python
class StreamConsumer(Protocol):
    def poll(self, max_records: int = 100) -> list[dict]: ...
    def commit(self, offsets: dict[str, int]) -> None: ...
    def position(self) -> dict[str, int]: ...
```

```python
class KafkaConsumerAdapter:
    """Обёртка над confluent-kafka: чтение + управление offset'ами."""

    def __init__(self, topic: str, group_id: str):
        ...

    def poll(self, max_records: int = 100) -> list[dict]:
        # десериализация, обработка таймаутов и ретраев - здесь, не у клиента
        ...

    def commit(self, offsets: dict[str, int]) -> None:
        # синхронный commit в группу потребителей
        ...

    def position(self) -> dict[str, int]:
        # текущие offset'ы для мониторинга и resume после рестарта
        ...
```

Shallow-версия - только `poll()`: тогда offset'ы «протекают» наружу, и клиент сам обязан помнить, что он уже прочитал, чтобы не потерять сообщения при рестарте (или не продублировать). А это означает, что клиент вынужден строить поверх интерфейса собственную логику подтверждения - то есть фасад/адаптер. Здесь же интерфейс узкий (одна роль - потребление), но полный: `poll` читает, `commit` подтверждает, `position` позволяет возобновить чтение.

### Пример 2.3. CredentialsProvider - роль «секреты с автообновлением»

```python
class CredentialsProvider(Protocol):
    def get(self) -> str: ...
    def rotate(self) -> str: ...
```

```python
class VaultCredentialsProvider:
    """Достаёт токен из Vault, кэширует и продлевает до истечения."""

    def __init__(self, vault_url: str, secret_path: str, ttl_seconds: int = 300):
        ...

    def get(self) -> str:
        # вернуть валидный токен; если скоро истечёт - обновить заранее
        ...

    def rotate(self) -> str:
        # принудительная ротация (вызывается операторами или триггером безопасности)
        ...
```

Shallow-интерфейс дал бы только `get()`: тогда клиент не знает про TTL, кэширует у себя устаревший секрет и получает 401 в рантайме, а ротацию секрета невозможно сделать вообще без правки интерфейса. `get` + `rotate` - это одна роль «управление жизненным циклом секрета», а не две разные. Интерфейс мал (2 сигнатуры), но не поверхностен: за `get` спрятан кэш, проверка TTL и HTTP к Vault.

## 3. Два примера Closure of Operations

Замыкание операций: сигнатура метода такова, что тип результата равен типу входа (или является его подмножеством). Такой интерфейс легко реализует Null Object (вернуть вход) и Composite (прогнать вход по цепочке), и его экземпляры удобно комбинировать.

### Пример 3.1. Цепочка нормализаторов: `str -> str`

```python
from typing import Protocol, Iterable

class Normalizer(Protocol):
    def normalize(self, value: str) -> str: ...
```

Null Object и Composite реализуются тривиально, потому что тип замкнут на `str`:

```python
class IdentityNormalizer:
    """Null Object: возвращает вход как есть."""
    def normalize(self, value: str) -> str:
        return value

class CollapseWhitespaceNormalizer:
    def normalize(self, value: str) -> str:
        return " ".join(value.split())

class LowercaseNormalizer:
    def normalize(self, value: str) -> str:
        return value.strip().lower()

class ChainedNormalizer:
    """Composite: сам является Normalizer'ом, поэтому цепочки вкладываются."""
    def __init__(self, normalizers: Iterable[Normalizer]):
        self._normalizers = list(normalizers)

    def normalize(self, value: str) -> str:
        for n in self._normalizers:
            value = n.normalize(value)
        return value
```

```python
phone_normalizer = ChainedNormalizer([
    CollapseWhitespaceNormalizer(),
    LowercaseNormalizer(),
    IdentityNormalizer(),   # шаг временно «выключен» через Null Object
])

# ChainedNormalizer можно использовать как обычный Normalizer
# внутри другой цепочки - композиция композитов бесплатна:
canonical = ChainedNormalizer([phone_normalizer, SomeExtraNormalizer()])
```

### Пример 3.2. Агрегат Money: операции замкнуты на собственном типе

Второй пример - из предметной области, где замыкание операций совпадает с идеей агрегата из DDD: все изменения состояния выполняются методами самого агрегата, инварианты проверяются внутри, а наружу состояние не «протекает».

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
    amount: int          # в минимальных единицах, чтобы не было проблем с float
    currency: str

    def add(self, other: "Money") -> "Money":
        assert other.currency == self.currency, "нельзя складывать разные валюты"
        return Money(self.amount + other.amount, self.currency)

    def sub(self, other: "Money") -> "Money":
        assert other.currency == self.currency, "нельзя вычитать разные валюты"
        assert self.amount >= other.amount, "баланс не может стать отрицательным"
        return Money(self.amount - other.amount, self.currency)

    def is_zero(self) -> bool:
        return self.amount == 0
```

Тип результата `add`/`sub` - снова `Money`, поэтому любые цепочки операций остаются внутри того же типа:

```python
balance = Money(1000, "RUB")
balance = balance.add(Money(500, "RUB")).sub(Money(200, "RUB"))  # Money(1300, "RUB")
```

Инварианты агрегата («валюта операций совпадает», «баланс неотрицателен») проверяются внутри самого агрегата, а не в клиентском коде, и операция либо целиком удаётся, либо падает до изменения состояния (объект иммутабельный - атомарность заложена в дизайн). Классический Null Object здесь тоже естественен - `Money(0, currency)`.

## Выводы

Для себя два практических приёма.

Первый: ISP и Shallow Interface - это не одно и то же. Узкий интерфейс не означает «одна тривиальная сигнатура». Хороший интерфейс - это полный набор операций одной роли, где каждая операция скрывает существенную сложность. Если интерфейс слишком мелкий, я сразу вижу симптомы из материала: клиенты достраивают поверх него фасады и адаптеры или лезут в детали реализации. Когда я ловлю себя на том, что пишу Adapter вокруг своего же интерфейса, - это сигнал, что интерфейс получился Shallow, а не «чистым ISP».

Второй: Closure of Operations - мощный индикатор компонуемости. Когда тип результата метода равен типу входа, я «на халяву» получаю Null Object (вернуть как есть), Composite (цепочка/вложение), декораторы и предсказуемые цепочки вызовов. При проектировании я теперь стараюсь сводить операции к замкнутым сигнатурам - `T -> T` - либо к ролям из пункта 2, где набор сигнатур мал, но каждая несёт реальную работу. Материал 96 в итоге дал мне конкретный рецепт: сначала пробуй замкнуть тип на себя, потом ослабляй до одной роли, но никогда не разменивай глубину на количество методов.

Closure of Operations прям очень понравился!