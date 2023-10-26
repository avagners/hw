from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Optional

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
    def removeFront(self) -> Optional[T]: ...

    # предусловие: дек не пустой
    # постусловие: из хвоста дека удалён элемент
    @abstractmethod
    def removeTail(self) -> Optional[T]: ...

    # Запросы:
    @abstractmethod
    def size(self) -> int: ... # возвращает размер дека


class Deque(AbsDeque):

    def __init__(self):
        self.deque = []

    def addFront(self, value: T) -> None:
        self.deque.insert(0, value)
    
    def addTail(self, value: T) -> None:
        self.deque.append(value)

    def removeFront(self) -> Optional[T]:
        if self.deque:
            return self.deque.pop(0)
        return None

    def removeTail(self) -> Optional[T]:
        if not self.deque:
            return None
        return self.deque.pop()

    def size(self) -> int:
        return len(self.deque)