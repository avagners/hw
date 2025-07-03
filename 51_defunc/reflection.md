# Дефункционализация

## Пример 1. Command pattern

До: 

```python
def run_after(func, delay):
    import time
    time.sleep(delay)
    return func()

# вызов
result = run_after(lambda: expensive_computation(42), 5)
```

После:
```python
from enum import Enum, auto

class CommandType(Enum):
    EXPENSIVE = auto()
    GREET = auto()

class Command:
    def __init__(self, typ, arg=None):
        self.typ = typ
        self.arg = arg

    def execute(self):
        if self.typ is CommandType.EXPENSIVE:
            return expensive_computation(self.arg)
        elif self.typ is CommandType.GREET:
            return f"Hello, {self.arg}!"
        else:
            raise ValueError

def run_after(cmd_obj, delay):
    import time
    time.sleep(delay)
    return cmd_obj.execute()

# использование
cmd = Command(CommandType.EXPENSIVE, arg=42)
print(run_after(cmd, 5))
cmd2 = Command(CommandType.GREET, arg="Alice")
print(run_after(cmd2, 1))
```

Теперь все «команды» перечислены, их можно сериализовать, очереди команд можно передавать между процессами.

## Пример 2. Сallback‑обработчики

До:
```python
def read_file_async(path, callback):
    # внутри — какая-то неблокирующая I/O‑обёртка
    data = ...  # когда данные готовы
    callback(data)

# вызов
def process(data):
    print("Length:", len(data))
read_file_async("foo.txt", process)
```

После:
```python
from enum import Enum, auto

class CallbackType(Enum):
    PRINT_LENGTH = auto()
    COUNT_LINES = auto()

class Callback:
    def __init__(self, typ):
        self.typ = typ

    def run(self, data):
        if self.typ is CallbackType.PRINT_LENGTH:
            print("Length:", len(data))
        elif self.typ is CallbackType.COUNT_LINES:
            print("Lines:", data.count("\n") + 1)
        else:
            raise ValueError

def read_file_async(path, cb_obj):
    # неблокирующая часть...
    data = ...
    cb_obj.run(data)

# использование
cb1 = Callback(CallbackType.PRINT_LENGTH)
read_file_async("foo.txt", cb1)
cb2 = Callback(CallbackType.COUNT_LINES)
read_file_async("foo.txt", cb2)
```

Теперь можно хранить Callback-объекты, передавать их по сети или сохранять в базе.

## Пример 3. Преобразование строк (ETL step)

До:
```python
from typing import Callable

def apply_transformation(value: str, func: Callable[[str], str]) -> str:
    return func(value)

# использование
apply_transformation("  hello ", lambda s: s.strip().lower())
```

После: 
```python
from enum import Enum, auto
from typing import Optional

class TransformType(Enum):
    STRIP_LOWER = auto()
    REMOVE_DIGITS = auto()
    PREFIX = auto()

class Transform:
    def __init__(self, typ: TransformType, param: Optional[str] = None):
        self.typ = typ
        self.param = param

    def apply(self, value: str) -> str:
        match self.typ:
            case TransformType.STRIP_LOWER:
                return value.strip().lower()
            case TransformType.REMOVE_DIGITS:
                return ''.join(c for c in value if not c.isdigit())
            case TransformType.PREFIX:
                return f"{self.param}{value}"
            case _:
                raise ValueError("Unknown transform")

# использование
t1 = Transform(TransformType.STRIP_LOWER)
t2 = Transform(TransformType.PREFIX, "ID_")
print(t1.apply("  HeLLo123 "))  # → "hello123"
print(t2.apply("0005"))         # → "ID_0005"
```

Такие трансформации часто задаются в YAML-конфигах или UI-интерфейсах — и здесь удобно сериализовать типы операций.

## Выводы

До этого я вообще не знал, что такое дефункционализация. Когда впервые услышал — показалось чем-то сложным и непрактичным. Типа «зачем заменять функции на классы и перечисления?

Перечитывал материал раз 10. И только после переписывания примеров начало доходить что это такое и зачем нужно.

Когда начал разбираться на реальных примерах — стало доходить, зачем это нужно. Особенно когда попробовал описать пайплайн трансформаций в YAML и применить его к данным. Понял, что lambda туда не вставишь. А вот `Enum + apply()` работает. 

Самое главное открытие для меня — это то, что дефункционализация нужна не для красоты кода, а для сериализации, расширяемости и переносимости. Если хочешь передавать задачи в очередь, логировать, накапливать истории.

В итоге я теперь смотрю на функции по-другому: если функция короткая и живёт локально — окей, а если она участвует в пайплайне, будет логироваться, храниться, передаваться — лучше сразу сделать через `Enum + apply()`.

Вывод: раньше казалось «overengineering», теперь — нормальный инструмент, особенно в проде, особето в ETL и распределенных вычислениях.