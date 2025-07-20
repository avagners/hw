# Наследование лучше композиции

## Набор тестов суперклассов

Нет, ранее я такой способ построения тестов не применял. 

После написания нескольких примеров, я был удивлен насколько это просто и мощно. 
Контрактные тесты суперкласса — это как шаблон, по которому проверяются все наследники. Мне понравилось, что можно один раз описать "ожидаемое поведение", а потом применять его к любым новым реализациям. Теперь я понимаю, как не допустить ошибки с подтипами. Тесты сразу показывают, что подкласс ломает поведение.

Этот подход позволяет:
- Зафиксировать инварианты интерфейса базового класса.
- Проверить корректность поведения новых реализаций.
- Документировать и формализовать требования к поведению.

Получается если хочется строго следовать LSP, то просто нужно оборачивать инварианты суперкласса в тесты и применять их к каждому подклассу.

```python
import os
import tempfile


# Базовый класс и его контракт
class FileStorage:
    def save(self, filename: str, data: bytes):
        raise NotImplementedError

    def load(self, filename: str) -> bytes:
        raise NotImplementedError


# Реализация 1: сохраняет в память
class InMemoryStorage(FileStorage):
    def __init__(self):
        self._data = {}

    def save(self, filename: str, data: bytes):
        self._data[filename] = data

    def load(self, filename: str) -> bytes:
        return self._data[filename]


# Реализация 2: На базе temp-файла на диске
class TempFileStorage(FileStorage):
    def __init__(self):
        self._dir = tempfile.TemporaryDirectory()

    def save(self, filename: str, data: bytes):
        path = os.path.join(self._dir.name, filename)
        with open(path, "wb") as f:
            f.write(data)

    def load(self, filename: str) -> bytes:
        path = os.path.join(self._dir.name, filename)
        with open(path, "rb") as f:
            return f.read()


# Реализация 3: Ломает контракт
class BrokenStorage(FileStorage):
    def save(self, filename: str, data: bytes):
        pass  # ничего не делает

    def load(self, filename: str) -> bytes:
        return b"garbage"  # всегда возвращает мусор


# Тест-контракт: должен работать для любой реализации FileStorage
class FileStorageContract:
    def get_storage(self) -> FileStorage:
        raise NotImplementedError

    def test_save_and_load(self):
        storage = self.get_storage()
        storage.save("test.txt", b"hello")
        assert storage.load("test.txt") == b"hello"


# Проверка соблюдения контракта LSP
class TestInMemoryStorage(FileStorageContract):
    def get_storage(self):
        return InMemoryStorage()


class TestTempFileStorage(FileStorageContract):
    def get_storage(self):
        return TempFileStorage()


class TestBrokenStorage(FileStorageContract):
    def get_storage(self):
        return BrokenStorage()
```

`TestInMemoryStorage`, `TestTempFileStorage`, `TestBrokenStorage` наследуют контракт от суперкласса `FileStorageContract` и прогоняют те же тесты. Если в будущем кто-то сделает другой `FileStorage`, он должен просто унаследоваться от `FileStorageContract` и тесты покажут, нарушил ли он контракт. Например, `BrokenStorage` нарушает контракт и тест `TestBrokenStorage` это показывает.

## Вы придерживаетесь полиморфизма подтипов как случая, только когда и полезно использовать наследование?

Нет, я мог воспользоваться наследованием так скажем "неосознанно" и поэтому легко нарушал принцип LSP.

После знакомства с материалом я понял, что это действительно единственный здравый случай, когда наследование даёт устойчивую пользу. 
Наследование ради "удобного доступа к методам", "экономии кода" или "продолжения мысли" - это ловушки. Если нельзя безопасно заменить родителя на подкласс, всё ломается.

Я намерен строго придерживаться правила: "наследование — только для подтипов, которые проходят контракт родителя без сюрпризов". то есть проходят тесты контракта.

Теперь я отчётливо вижу, что наследование - это инструмент подтипирования, а не "удобный способ переиспользовать код".
Там, где поведение отличается или нарушает контракт — нужен интерфейс + композиция, а не иерархия.

