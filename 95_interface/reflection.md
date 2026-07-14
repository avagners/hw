# Когда интерфейсы -- плохие абстракции

## 1. Нарушение LSP (прямоугольник и квадрат)

```python
from abc import ABC, abstractmethod

class IRectangle(ABC):
    @property
    @abstractmethod
    def width(self) -> int: ...

    @width.setter
    @abstractmethod
    def width(self, value: int): ...

    @property
    @abstractmethod
    def height(self) -> int: ...

    @height.setter
    @abstractmethod
    def height(self, value: int): ...

class Rectangle(IRectangle):
    def __init__(self, w: int, h: int):
        self._w = w
        self._h = h

    @property
    def width(self): return self._w
    @width.setter
    def width(self, v): self._w = v

    @property
    def height(self): return self._h
    @height.setter
    def height(self, v): self._h = v

class Square(IRectangle):
    def __init__(self, side: int):
        self._side = side

    @property
    def width(self): return self._side
    @width.setter
    def width(self, v): self._side = v   # побочный эффект: height тоже меняется

    @property
    def height(self): return self._side
    @height.setter
    def height(self, v): self._side = v  # то же самое
```

Почему интерфейс плох:
Клиент, работающий с IRectangle, ожидает, что изменение ширины не затронет высоту. Square нарушает этот контракт: установка width неявно меняет height. Это именно то нарушение LSP, которое превращает «абстракцию» в ловушку. Пользователю приходится «задаунгрейдить» объект (проверять isinstance) или ловить странные побочные эффекты.

## 2. Заголовочный интерфейс (Header Interface)

```python
from abc import ABC, abstractmethod

class PdfReportGenerator:
    def load_data(self, path: str): ...
    def process(self): ...
    def validate(self) -> bool: ...
    def render(self) -> bytes: ...
    def save(self, output_path: str): ...

# «Извлекли» интерфейс – получился механический слепок с класса
class IPdfReportGenerator(ABC):
    @abstractmethod
    def load_data(self, path: str): ...
    @abstractmethod
    def process(self): ...
    @abstractmethod
    def validate(self) -> bool: ...
    @abstractmethod
    def render(self) -> bytes: ...
    @abstractmethod
    def save(self, output_path: str): ...

class PdfReportGeneratorV2(IPdfReportGenerator):
    # реализация 1:1 повторяет сигнатуры
    ...
```

Почему интерфейс плох:
Интерфейс дословно повторяет публичный API единственного класса. Отношение 1:1 между интерфейсом и реализацией не даёт ни слабой связанности, ни настоящей абстракции. Это просто дублирование сигнатур, создающее иллюзию гибкости, но не несущее никакой ценности — классический header interface.

## 3. Поверхностный интерфейс

```python
from abc import ABC, abstractmethod
from django.db import models

class IOrderRepository(ABC):
    @abstractmethod
    def get_orders_by_user(self, user_id: int) -> models.QuerySet:
        """Возвращает Django QuerySet – деталь реализации ORM."""
        ...

class DjangoOrderRepository(IOrderRepository):
    def get_orders_by_user(self, user_id: int) -> models.QuerySet:
        return Order.objects.filter(user_id=user_id)
```

Почему интерфейс плох:
Интерфейс «протёк» из-за того, что не был рекурсивно очищен от деталей реализации. Сигнатура метода завязана на QuerySet конкретной ORM. Заменить DjangoOrderRepository на реализацию, работающую с MongoDB или внешним API, практически невозможно — новый код придётся подгонять под QuerySet, ломая весь смысл абстракции. Это поверхностный интерфейс, создающий обманчивое впечатление несвязанности.


## 4. Протекающая абстракция

```python
from abc import ABC, abstractmethod

class IStorage(ABC):
    @abstractmethod
    def save_to_file(self, path: str, content: bytes): ...
    @abstractmethod
    def read_from_file(self, path: str) -> bytes: ...
    @abstractmethod
    def delete_file(self, path: str): ...
```

Почему интерфейс плох:
Названия методов (file, path) раскрывают файловую природу хранилища. Если мы захотим реализовать этот интерфейс для хранения в S3, Redis или в памяти, слова file и path станут неверными метафорами. Абстракция негерметична: деталь реализации (файловая система) «просачивается» в контракт. Переиспользовать такой интерфейс для других хранилищ оказывается неудобно, а сам код вводит в заблуждение.

## 5. Интерфейс как форма без контракта (USB-форма без гарантий)

```python
from abc import ABC, abstractmethod

class INotificationSender(ABC):
    @abstractmethod
    def send(self, message: str) -> bool:
        """Отправляет сообщение; возвращает True при успехе."""
        ...

class EmailSender(INotificationSender):
    def send(self, message: str) -> bool:
        # кидает SMTPException при недоступности сервера
        ...

class PushSender(INotificationSender):
    def send(self, message: str) -> bool:
        # требует передачи device token отдельно, может вернуть False при недоставке
        ...
```

Почему интерфейс плох:
Интерфейс задаёт только механическую стыковку (метод send с одинаковой сигнатурой), но не даёт контрактных гарантий. Разные реализации ведут себя по-разному: одна бросает исключения, другая тихо возвращает False, третья требует предварительной регистрации токена. Клиент вынужден знать, с каким именно «отправителем» работает, то есть интерфейс не является полноценной абстракцией, позволяющей заменять реализацию без модификации кода. Это как Type-A и Type-B USB — форма совпадает, а содержание разное.

## Выводы

После выполнения этого задания я понял, что раньше воспринимал интерфейсы как универсальное средство для построения хорошей архитектуры. Казалось, что если между классами поставить интерфейс, то код автоматически станет слабосвязанным и расширяемым. Теперь я понимаю, что это не так. 

Главный вывод для меня — интерфейс сам по себе не является абстракцией. Он лишь определяет форму взаимодействия: какие методы доступны и какие параметры они принимают. Но это совершенно не означает, что все реализации будут одинаково корректно работать с точки зрения предметной области.

В дальнейшем при проектировании я постараюсь меньше думать категориями «нужно сделать интерфейс» и больше задаваться вопросами: какую абстракцию я хочу выразить, какие гарантии она должна предоставлять и сможет ли любая реализация естественным образом соблюдать этот контракт. Думаю, такой подход поможет создавать более понятный, гибкий и устойчивый к изменениям код.