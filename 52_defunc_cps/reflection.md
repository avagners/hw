# Дефункционализация + CPS

## Пример 1. ETL-пайплайн с возможностью восстановления после сбоя (CPS)

Сценарий:
Строим ETL-цепочку из шагов:
- загрузка данных,
- очистка,
- нормализация,
- агрегация,
- выгрузка в хранилище.

Обычно они выполняются в виде вызова одной функции за другой. Но если один шаг падает, всё обрушивается, и восстановить цепочку сложно.

Решение: Дефункционализированное CPS-представление.

Вместо вызовов:
```python
data = load()
data = clean(data)
data = normalize(data)
upload(data)
```

Создаем continuation-цепочку, где каждый шаг знает, что делать дальше:
```python
from abc import ABC, abstractmethod
from typing import Any

class Cont(ABC):
    @abstractmethod
    def apply(self, result: Any) -> Any: ...

class Halt(Cont):
    def apply(self, result: Any) -> Any:
        print("Pipeline finished.")
        return result

class NormalizeThen(Cont):
    def __init__(self, next_cont: Cont):
        self.next = next_cont

    def apply(self, result: Any) -> Any:
        normalized = normalize(result)
        return self.next.apply(normalized)

class CleanThen(Cont):
    def __init__(self, next_cont: Cont):
        self.next = next_cont

    def apply(self, result: Any) -> Any:
        cleaned = clean(result)
        return self.next.apply(cleaned)

class LoadStart:
    def __init__(self, cont: Cont):
        self.cont = cont

    def run(self):
        data = load()
        return self.cont.apply(data)


# Построение пайплайна
if __name__ == "__main__":
    cont = Halt()
    cont = NormalizeThen(cont)
    cont = CleanThen(cont)
    pipeline = LoadStart(cont)
    pipeline.run()
```

Что даёт такой подход:
- Шаги можно логировать и восстанавливать;
- Возможность поставить checkpoint;
- Сериализовать контекст — т.е. если в середине цепи сбой, ты можешь начать заново с нужного шага.

## Пример 2. Проверки качества данных (Data Quality Rules Engine)

Сценарий:
Нужно проверять CSV или DataFrame по последовательности правил:
- Колонка email не пустая.
- Колонка age в диапазоне.
- Если country == "US" → state не пуст.

В простом HOF-стиле логика вложенная и нечитаемая. А если проверка сложная (с вложенными условиями), нужно отделить шаги и иметь возможность пошагового анализа.

Решение: Дефункционализированная CPS-валидация
```python
class RuleCont(ABC):
    @abstractmethod
    def apply(self, df): ...

class End(RuleCont):
    def apply(self, df): return True

class CheckNotNull(RuleCont):
    def __init__(self, column: str, next: RuleCont):
        self.column = column
        self.next = next

    def apply(self, df):
        if df[self.column].isnull().any():
            print(f"❌ Nulls in {self.column}")
            return False
        return self.next.apply(df)

class CheckInRange(RuleCont):
    def __init__(self, column: str, low: int, high: int, next: RuleCont):
        self.column = column
        self.low = low
        self.high = high
        self.next = next

    def apply(self, df):
        if not df[self.column].between(self.low, self.high).all():
            print(f"❌ {self.column} out of range")
            return False
        return self.next.apply(df)


if __name__ == "__main__":
    rules = End()
    rules = CheckInRange("age", 18, 65, rules)
    rules = CheckNotNull("email", rules)
    result = rules.apply(df)
```

Плюсы:
- Легко отследить, на каком правиле упали;
- Можно сериализовать шаги;
- Возможность визуализировать цепочку правил.

## Пример 3. Отложенные вычисления на кластере

Сценарий:
У тебя очередь задач (например, в Dask или Celery), которые нужно исполнять по цепочке, и они могут быть асинхронными или удалёнными.
Вместо прямой передачи `lambda` (что не работает), ты строишь цепочку продолжений, где каждая задача получает результат и решает — передать дальше или завершить.

Пример задачи:
```python
class TaskCont(ABC):
    @abstractmethod
    def apply(self, x: float) -> float: ...

class Finish(TaskCont):
    def apply(self, x: float) -> float:
        print(f"Final result: {x}")
        return x

class AddThen(TaskCont):
    def __init__(self, n: float, next: TaskCont):
        self.n = n
        self.next = next

    def apply(self, x: float) -> float:
        return self.next.apply(x + self.n)

class MultiplyThen(TaskCont):
    def __init__(self, n: float, next: TaskCont):
        self.n = n
        self.next = next

    def apply(self, x: float) -> float:
        return self.next.apply(x * self.n)


if __name__ == "__main__":
    # Цепочка: (((x + 5) * 2) + 1)
    cont = Finish()
    cont = AddThen(1, cont)
    cont = MultiplyThen(2, cont)
    cont = AddThen(5, cont)
    cont.apply(10)  # → Final result: 31
```

## Выводы

Сначала всё это казалось каким-то усложнением. Зачем заменять простые lambda и if на Enum и какие-то apply()? А уж CPS вообще звучало как что-то из функционального программирования, к которому я раньше не прикасался.

Но когда я попробовал описать пайплайн из шагов или правила валидации данных — понял, зачем это нужно.
Когда шаги логируются, сериализуются, передаются в очередь, восстанавливаются после сбоя — простая функция уже не подходит. А enum + apply — идеально ложится.

С CPS сначала было вообще непривычно: передавать «что делать дальше» как параметр? Но оказалось, это удобный способ контролировать исполнение пошагово — особенно в пайплайнах, где нужно приостанавливать, ветвить, логировать.

Теперь я понимаю, что:
- для простого кода lambda окей,
- но если логика должна быть гибкой, сохраняемой, исполняемой частями или в другом месте — лучше использовать дефункционализацию и CPS.

Это не про "замену" функций, а про структурированный контроль над вычислениями. Теперь я вижу, где это может сильно упростить жизнь — особенно в ETL, очередях задач и пайплайнах данных.

Еще я заметил, что некоторые "паттерны" (как `Command` или `State`) — это частные случаи дефункционализации. Этого я не понимал.