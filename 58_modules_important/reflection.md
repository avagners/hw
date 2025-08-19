# Модули важнее всего

## Пример 1: Коллекция данных как Стек, Очередь и Итерируемый объект

Одна и та же структура данных (например, список) может рассматриваться как стек, очередь или просто как коллекция для перебора.

```python
from abc import ABC, abstractmethod
from collections import deque
from typing import Iterable, Iterator

# Интерфейс №1: Стек
class Stack(ABC):
    @abstractmethod
    def push(self, item):
        pass

    @abstractmethod
    def pop(self):
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

# Интерфейс №2: Очередь (FIFO)
class Queue(ABC):
    @abstractmethod
    def enqueue(self, item):
        pass

    @abstractmethod
    def dequeue(self):
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        pass

# Интерфейс №3: Просто итерируемая коллекция
class SimpleCollection(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator:
        pass

    @abstractmethod
    def add(self, item):
        pass

# Одна-единственная реализация.
class UniversalCollection:
    def __init__(self):
        self._data = deque()

    # Реализация методов Stack
    def push(self, item):
        self._data.append(item)

    def pop(self):
        return self._data.pop()

    # Реализация методов Queue
    def enqueue(self, item):
        self._data.appendleft(item)

    def dequeue(self):
        return self._data.pop()

    # Реализация методов SimpleCollection
    def __iter__(self):
        return iter(self._data)

    def add(self, item):
        self.push(item)  # Просто используем push как способ добавления

    # Общий метод для всех интерфейсов
    def is_empty(self) -> bool:
        return len(self._data) == 0

# Функции, которые зависят от интерфейсов, а не от реализации
def stack_processor(s: Stack):
    s.push("stack_item")
    print(f"Popped from stack: {s.pop()}")

def queue_processor(q: Queue):
    q.enqueue("queue_item")
    print(f"Dequeued from queue: {q.dequeue()}")

def collection_processor(c: SimpleCollection):
    c.add("collection_item")
    print("Collection contents:", list(c))

# Использование
if __name__ == "__main__":
    collection = UniversalCollection()

    # Один объект используется через три разных интерфейса
    stack_processor(collection)  # Объект воспринимается как Stack
    queue_processor(collection)  # Тот же объект воспринимается как Queue
    collection_processor(collection) # Тот же объект воспринимается как SimpleCollection
```

Класс `UniversalCollection` не наследуется явно от всех интерфейсов, но он реализует все их методы. Таким образом, один объект этого класса может быть передан в три разные функции, каждая из которых ожидает свой интерфейс.

## Пример 2: Файловый объект как источник данных и как логирующий механизм

Один и тот же объект, пишущий в файл, может быть интерпретирован как основной механизм вывода данных и как система логирования.
```python
from abc import ABC, abstractmethod

# Интерфейс №1: Запись основных данных
class DataSink(ABC):
    @abstractmethod
    def write_data(self, data: str):
        pass

# Интерфейс №2: Система логирования
class Logger(ABC):
    @abstractmethod
    def log_info(self, message: str):
        pass

    @abstractmethod
    def log_error(self, message: str):
        pass

# Единая реализация - файловый объект
class FileWriter:
    def __init__(self, filename: str):
        self.filename = filename

    # Метод, который делает его пригодным для DataSink
    def write_data(self, data: str):
        with open(self.filename, 'a') as f:
            f.write(f"DATA: {data}\n")

    # Методы, которые делают его пригодным для Logger
    def log_info(self, message: str):
        with open(self.filename, 'a') as f:
            f.write(f"INFO: {message}\n")

    def log_error(self, message: str):
        with open(self.filename, 'a') as f:
            f.write(f"ERROR: {message}\n")

# Функции, работающие с интерфейсами
def save_application_data(sink: DataSink):
    sink.write_data("Very important user data")

def run_application(logger: Logger):
    logger.log_info("Application started")
    # ... какая-то логика
    logger.log_error("A non-critical error occurred")

# Использование
if __name__ == "__main__":
    file_writer = FileWriter("app_output.log")

    # Один объект используется и для данных, и для логов
    save_application_data(file_writer)  # Используется как DataSink
    run_application(file_writer)        # Тот же объект используется как Logger

    # Содержимое файла app_output.log после запуска:
    # DATA: Very important user data
    # INFO: Application started
    # ERROR: A non-critical error occurred
```

Объект `FileWriter` предоставляет функциональность для двух совершенно разных ролей в системе. Модуль `save_application_data` видит в нем только `DataSink`, а модуль `run_application` — только `Logger`. Реализация одна, а интерфейсов — два.

## Пример 3: Кэш как быстрый словарь и как хранилище с временем жизни

Один и тот же кэширующий объект можно использовать просто как быстрый ключ-значение словарь, а можно — как хранилище с TTL (time to live), где важен не только факт наличия данных, но и их "свежесть".

```python
from abc import ABC, abstractmethod
import time

# Интерфейс №1: Простое ключ-значение хранилище
class KeyValueStorage(ABC):
    @abstractmethod
    def get(self, key):
        pass

    @abstractmethod
    def set(self, key, value):
        pass

# Интерфейс №2: Хранилище с временем жизни записей (TTL)
class TTLStorage(ABC):
    @abstractmethod
    def get_with_ttl(self, key):
        """Возвращает значение и оставшееся время жизни."""
        pass

    @abstractmethod
    def set_with_ttl(self, key, value, ttl_seconds: int):
        pass

# Единая реализация кэша с TTL
class TTLCache:
    def __init__(self):
        self._storage = {}
        # Будем хранить не только значение, но и время его "смерти"
        self._expiry_times = {}

    # Реализация методов KeyValueStorage
    def get(self, key):
        # Для простого хранилища мы просто возвращаем значение, если оно живо
        value, _ = self._get_if_alive(key)
        return value

    def set(self, key, value):
        # Для простого хранилища устанавливаем значение без TTL (или с бесконечным)
        self.set_with_ttl(key, value, 999999)

    # Реализация методов TTLStorage
    def get_with_ttl(self, key):
        value, expiry_time = self._get_if_alive(key)
        if value is None:
            return None, 0
        remaining_ttl = max(0, expiry_time - time.time())
        return value, remaining_ttl

    def set_with_ttl(self, key, value, ttl_seconds: int):
        expiry_time = time.time() + ttl_seconds
        self._storage[key] = value
        self._expiry_times[key] = expiry_time

    # Внутренний вспомогательный метод
    def _get_if_alive(self, key):
        if key not in self._storage:
            return None, 0

        expiry_time = self._expiry_times[key]
        if time.time() > expiry_time:
            # Значение устарело, удаляем его
            del self._storage[key]
            del self._expiry_times[key]
            return None, 0
        return self._storage[key], expiry_time

# Функции, работающие с разными интерфейсами
def use_as_simple_cache(cache: KeyValueStorage):
    cache.set("user_123", "Alice")
    print(f"Got from simple cache: {cache.get('user_123')}")

def use_as_ttl_cache(cache: TTLStorage):
    cache.set_with_ttl("session_456", "active", ttl_seconds=2)  # Сессия умрет через 2 секунды
    value, ttl = cache.get_with_ttl("session_456")
    print(f"Got from TTL cache: {value}, TTL: {ttl:.2f}s")

    time.sleep(3)  # Ждем, пока сессия протухнет
    value, ttl = cache.get_with_ttl("session_456")
    print(f"Got expired session: {value}")

# Использование
if __name__ == "__main__":
    cache = TTLCache()

    # Один объект кэша используется двумя разными способами
    use_as_simple_cache(cache)   # Используется как KeyValueStorage
    use_as_ttl_cache(cache)      # Тот же объект используется как TTLStorage
```

Модулю `use_as_simple_cache` объект `TTLCache` представляется простым хранилищем, его не волнует TTL. Модуль `use_as_ttl_cache`, наоборот, использует весь функционал, связанный со временем жизни. Одна реализация (`TTLCache`) предоставляет две различные абстракции (`KeyValueStorage` и `TTLStorage`) для разных клиентов.

## Выводы

Раньше, когда я слышал слово «модульность», я думал: «У меня есть интерфейс `Database`, и я могу сделать его реализацию для `PostgreSQL`, `MySQL` и `SQLite»`. Это полезно, но оказалось, что это лишь половина картины, причем самая очевидная.

Сегодня я открыл для себя вторую, гораздо более мощную половину: одна реализация может играть разные роли и удовлетворять нескольким абсолютно независимым интерфейсам.

Раньше я сначала придумывал интерфейс, а потом «привязывал» к нему реализацию. Теперь я вижу, что это отношения «многие ко многим». Написав класс, я должен спросить себя: «А через какие еще призмы можно на него посмотреть? Какие еще роли он может исполнять в системе? Какие группы методов ему нужно предоставить, чтобы он был универсальным в системе?»

Теперь по-новому смотрю на код, который уже написан. Я начинаю видеть в больших классах не монолиты, а набор потенциальных интерфейсов. «Ага, вот эта группа методов - по сути, интерфейс `Cache`, а вон та - интерфейс `Storage`. Надо их формализовать и позволить клиентам использовать класс именно в этой роли».
