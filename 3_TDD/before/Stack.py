from abc import ABC, abstractmethod
from typing import TypeVar, Generic

T = TypeVar('T')


# АТД Стека
class AbsStack(ABC, Generic[T]):
    # Конструктор
    # постусловие: создан новый пустой стек
    def __init__(self): ...

    # Команды:
    # предусловие: в стеке менее максимального кол-ва элементов
    # постусловие: в стек добавлено новое значение
    @abstractmethod
    def push(self, value: T) -> None: ...

    # предусловие: стек не пустой
    # постусловие: из стека удалён верхний элемент
    @abstractmethod
    def pop(self) -> None: ...

    # Запросы:
    # предусловие: стек не пустой
    @abstractmethod
    def peek(self) -> T: ...
    @abstractmethod
    def size(self) -> int: ...


# Реализация стека
class Stack(AbsStack):
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if not self.stack:
            return None
        return self.stack.pop()

    def peek(self):
        if not self.stack:
            return None
        return self.stack[-1]

    def size(self):
        return len(self.stack)
