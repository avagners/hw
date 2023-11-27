from abc import ABC, abstractmethod


class ShapeVisitor(ABC):

    @abstractmethod
    def visit_circle(self, circle): ...

    @abstractmethod
    def visit_rectangle(self, rectangle): ...


class AreaPerimeterVisitor(ShapeVisitor):

    def visit_circle(self, circle):
        area = 3.14 * circle.radius ** 2
        perimeter = 2 * 3.14 * circle.radius
        return area, perimeter

    def visit_rectangle(self, rectangle):
        area = rectangle.width * rectangle.height
        perimeter = 2 * (rectangle.width + rectangle.height)
        return area, perimeter
