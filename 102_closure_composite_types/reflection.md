# Обобщение замыкания и составные типы (продолжение материала 96)

Продолжаю серию про выявление хороших абстракций. Здесь - две следующие категории компонуемых интерфейсов из материала 96: обобщение замыкания (выходной тип - подмножество входных) и составные типы, включая интерфейсы, возвращающие перечислимые объекты.

## 2. Три примера интерфейсов для обобщения замыкания

Напомню идею: когда полноценное замыкание (`T -> T`) недостижимо, можно ослабить требование до «выходной тип есть подмножество входных типов». Тогда компонуемость частично сохраняется: лишние типы можно игнорировать или подменять, не ломая цепочки.

### Пример 2.1. Комбинатор частичных агрегатов `merge(T, T) -> T`

Прямой аналог делегата `T MyFunction<T>(T x)` из C#. На входе пара значений одного типа, на выходе - подмножество (тот же `T`).

```python
from typing import Protocol, TypeVar

T = TypeVar("T")

class Combiner(Protocol[T]):
    """Бинарная операция: складывает два частичных результата в один."""
    def merge(self, left: T, right: T) -> T: ...
```

Реальный пример - сбор метрик, посчитанных по разным партициям (шардам):

```python
class MetricCombiner:
    """Суммирует словари вида {metric_name: count}."""
    def merge(self, left: dict[str, int], right: dict[str, int]) -> dict[str, int]:
        result = dict(left)
        for name, count in right.items():
            result[name] = result.get(name, 0) + count
        return result
```

Компонуемость здесь почти «арифметическая»: раз результат того же типа, что и операнды, частичные агрегаты можно свёртывать в любом порядке и в любом количестве - хоть попарно, хоть деревом:

```python
from functools import reduce

combiner = MetricCombiner()
part_results = [  # посчитано на разных воркерах
    {"clicks": 10, "views": 100},
    {"clicks": 5, "views": 50},
    {"clicks": 3},
]
total = reduce(combiner.merge, part_results)   # {"clicks": 18, "views": 150}
```

Выходной тип - подмножество входных: операция замкнута относительно `T`, а все «лишние» типы (имена метрик, идентификаторы партиций) в сигнатуру вообще не попадают. Такой интерфейс можно безопасно оборачивать декоратором (логирование, замер времени) и вкладывать: `merge` композита просто рекурсивно мёржит вложенные результаты.

### Пример 2.2. «Возьми нужный тип, остальное игнорируй» (аналог `T1 DoIt(Foo<T1, T2, T3>)`)

В материале был пример: из `Foo<T1, T2, T3>` берём `T1` и игнорируем всё остальное. В моём проекте то же самое - обработка сообщений из очереди: сообщение приходит в обёртке с ключом и метаданными, а бизнес-логике нужен только полезный груз.

```python
from typing import Any, Generic, Protocol, TypeVar

V = TypeVar("V")
K = TypeVar("K")
M = TypeVar("M")

class Envelope(Generic[V, K, M]):
    def __init__(self, value: V, key: K, meta: M):
        self.value = value
        self.key = key
        self.meta = meta

class PayloadExtractor(Protocol):
    """Из обёртки достаёт только value, игнорируя key и meta."""
    def extract(self, env: Envelope[V, Any, Any]) -> V: ...
```

Ценность «игнорирования остального»: интерфейс не зависит от типов `K` и `M`, поэтому одна и та же реализация работает с сообщениями, у которых ключ - строка, число или вообще отсутствует, а метаданные меняются от версии к версии. Тип `V` на выходе образует замкнутое подмножество, и дальше с ним можно строить цепочки, не таская обёртку:

```python
class KafkaPayloadExtractor:
    def extract(self, env: Envelope[V, Any, Any]) -> V:
        return env.value

# композит-фолбэк: если первый экстрактор вернул None, пробуем следующий
class FirstNonEmptyExtractor:
    def __init__(self, extractors: list[PayloadExtractor]):
        self._extractors = extractors

    def extract(self, env: Envelope[V, Any, Any]) -> V | None:
        for ex in self._extractors:
            value = ex.extract(env)
            if value is not None:
                return value
        return None
```

### Пример 2.3. Оператор над потоком: лишние типы параметров исключены из результата

Третий случай обобщения: вход и выход - один и тот же тип элемента (`Row`), но в сигнатуре есть дополнительные типы (ключи, лимиты), которые на компонуемость не влияют. Это классика стриминговых операторов в моих пайплайнах:

```python
from typing import Iterable, Protocol

class Row: ...

class StreamOperator(Protocol):
    """Iterable[Row] -> Iterable[Row]; ключи и лимиты не меняют тип потока."""
    def apply(
        self,
        rows: Iterable[Row],
        keys: tuple[str, ...],
        limit: int | None = None,
    ) -> Iterable[Row]: ...
```

Реализации - дедупликация и взятие топ-N:

```python
class DedupeOperator:
    def apply(self, rows, keys, limit=None):
        seen: set[tuple] = set()
        for row in rows:
            signature = tuple(getattr(row, k) for k in keys)
            if signature in seen:
                continue
            seen.add(signature)
            yield row

class TopNOperator:
    def apply(self, rows, keys, limit=None):
        ordered = sorted(rows, key=lambda r: tuple(getattr(r, k) for k in keys))
        yield from ordered if limit is None else ordered[:limit]
```

Компонуемость: результат оператора - снова `Iterable[Row]`, поэтому операторы выстраиваются в цепочку, и у каждого звена могут быть свои `keys` и `limit` - эти типы «протекают» только внутрь звена и не мешают собирать конвейер:

```python
result = TopNOperator().apply(
    DedupeOperator().apply(raw_rows, keys=("user_id", "date"), limit=100),
    keys=("clicks",),
    limit=10,
)
```

## 3. Два примера составных типов

Перехожу к самой «слабой» категории: `T2 map(T1)`. Чтобы она оставалась компонуемой, либо результат оборачивают в составной тип, либо интерфейс сразу возвращает перечислимое.

### Пример 3.1. Фолбэк-цепочка вместо одного некомпонуемого результата

Когда результат - одиночный скаляр (`int | None`), напрямую его не скомпоновать. Помогает приём из материала (композит возвращает первый ненулевой результат). Реальный кейс - приведение строки из сырых данных к числу несколькими способами по очереди:

```python
class ValueParser(Protocol):
    def parse(self, raw: str) -> int | None: ...

class IntParser:
    def parse(self, raw: str) -> int | None:
        try:
            return int(raw)
        except ValueError:
            return None

class IsoTimestampParser:
    """Парсит '2026-09-03T10:00:00Z' -> epoch seconds."""
    def parse(self, raw: str) -> int | None:
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
            return int(dt.timestamp())
        except ValueError:
            return None

class NullParser:
    """Null Object: всегда 'не распознано'."""
    def parse(self, raw: str) -> int | None:
        return None

class FirstMatchParser:
    """Composite: возвращает результат первого сработавшего парсера."""
    def __init__(self, parsers: list[ValueParser]):
        self._parsers = parsers

    def parse(self, raw: str) -> int | None:
        for parser in self._parsers:
            value = parser.parse(raw)
            if value is not None:
                return value
        return None

parse = FirstMatchParser([IntParser(), IsoTimestampParser(), NullParser()])
assert parse("42") == 42
assert parse("2026-09-03T10:00:00Z") is not None
```

Одиночный тип результата компонуется плохо, поэтому правило объединения приходится придумывать вручную («первый ненулевой») - это ровно тот случай, про который материал говорит: если результат не компонуется сам по себе, придётся приложить усилия, и лучше такие цепочки делать короткими.

### Пример 3.2. Интерфейс, возвращающий перечислимое, - компонуется «бесплатно»

Второй пример - более удачный: интерфейс сразу возвращает `Iterable`, и тогда Null Object - это пустая последовательность, а Composite - последовательность, склеенная из нескольких. У меня это правило-движок генерации событий: на входе изменение записи, на выходе - ноль или больше событий-уведомлений.

```python
from typing import Iterable, Protocol

class Event: ...

class ChangeRule(Protocol):
    """По изменению записи порождает Iterable событий (может быть пустым)."""
    def emit(self, change: dict) -> Iterable[Event]: ...

class NoopRule:
    """Null Object: правило 'выключено' - порождает пустую последовательность."""
    def emit(self, change: dict) -> Iterable[Event]:
        return iter(())

class PriceDropRule:
    def emit(self, change: dict) -> Iterable[Event]:
        if change.get("type") == "price_drop":
            yield Event("notify_followers", change["product_id"])

class StockRule:
    def emit(self, change: dict) -> Iterable[Event]:
        if change.get("type") == "restock":
            yield Event("notify_waitlist", change["product_id"])

class CompositeRule:
    """Composite: события всех правил подряд."""
    def __init__(self, rules: list[ChangeRule]):
        self._rules = rules

    def emit(self, change: dict) -> Iterable[Event]:
        for rule in self._rules:
            yield from rule.emit(change)
```

Интерфейс возвращает перечислимое, поэтому:
- выключить правило = подставить `NoopRule` вместо `if rule is not None`;
- добавить правило = дописать его в список, потребитель не меняется;
- сам `CompositeRule` - тоже `ChangeRule`, поэтому движки правил можно вкладывать друг в друга.

```python
engine = CompositeRule([PriceDropRule(), StockRule(), NoopRule()])
events = list(engine.emit({"type": "restock", "product_id": 7}))
```

Именно поэтому материал и говорит: интерфейсы, возвращающие перечислимые объекты, - как правило, хорошие абстракции.

## 4. Заключение: насколько применимо в моей работе

Применимо хорошо, потому что я работаю в основном с потоками и пайплайнами данных, а это буквально «царство» замкнутых сигнатур и перечислимых типов.

Что я уже забираю в практику:

- **Сигнатуру `Iterable -> Iterable` как стандарт для операторов.** Дедупликация, топ-N, фильтры, обогащение - всё это в моих конвейерах теперь оформляется как интерфейс, возвращающий перечислимое. Это даёт бесплатные Null Object (пустой поток) и Composite (конкатенация), и каждый новый шаг не требует правки потребителя.
- **`merge(T, T) -> T` для агрегации по партициям.** Раньше я писал отдельные функции «собрать результаты», теперь проектирую их как бинарные комбинаторы - их можно свёртывать как угодно и переиспользовать между пайплайнами.
- **Принцип «игнорируй лишние типы».** В обработке сообщений и конфигов я стал явно выносить в интерфейс только тот тип, что нужен на выходе, а обёртки (ключи, метаданные) оставлять за скобками. Интерфейсы стали заметно стабильнее: смена формата метаданных больше не ломает подписчиков.

Где применимо с трудом:

- **Полноценное замыкание `T -> T`** в чистом виде получается редко: почти всегда есть хотя бы один дополнительный параметр (ключ, лимит, конфиг). Поэтому мне ближе именно обобщение - «выход - подмножество входных типов», а не строгое замыкание.
- **Составные типы с одиночным некомпонуемым результатом** (как парсеры в примере 3.1) я стараюсь избегать и переписывать на возврат перечислимого или на цепочку «первый подходящий», но полностью исключить не получается - например, валидаторы и парсеры по своей природе возвращают один ответ.

Главный вывод для себя: эти рекомендации - не абстрактная теория, а рабочий инструмент. Я теперь на этапе проектирования интерфейса сразу спрашиваю: «что будет Null Object и Composite для этой абстракции?» - и если ответ неочевиден, меняю сигнатуру так, чтобы он стал очевиден. В моей предметной области это почти всегда означает «возвращай поток, а не одно значение».
