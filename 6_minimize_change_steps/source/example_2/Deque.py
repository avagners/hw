from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')


# АТД Дек
class AbsDeque(ABC, Generic[T]):

    # Конструктор
    # постусловие: создан новый пустой дек
    def __init__(self): ...

    # Команды:
    # постусловие: в голову дека добавлено новый элемент
    @abstractmethod
    def addFront(self, value: T) -> None: ...

    # постусловие: в хвост дека добавлено новый элемент
    @abstractmethod
    def addTail(self, value: T) -> None: ...

    # предусловие: дек не пустой
    # постусловие: из головы дека удалён элемент
    @abstractmethod
    def removeFront(self) -> None: ...

    # предусловие: дек не пустой
    # постусловие: из хвоста дека удалён элемент
    @abstractmethod
    def removeTail(self) -> None: ...

    # Запросы:
    @abstractmethod
    def size(self) -> int: ... # возвращает размер дека
