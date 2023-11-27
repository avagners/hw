from abc import ABC, abstractmethod

from visitor import ShapeVisitor


class Shape(ABC):

    @abstractmethod
    def accept(self, visitor: ShapeVisitor):
        pass


class Circle(Shape):
    def __init__(self, radius):
        self.radius = radius

    def accept(self, visitor: ShapeVisitor):
        return visitor.visit_circle(self)


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def accept(self, visitor: ShapeVisitor):
        return visitor.visit_rectangle(self)
