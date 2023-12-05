from abc import ABC

from mixins import AreaMixin, PerimeterMixin


class Shape(ABC):
    def __init__(self, shape_type):
        self.shape_type = shape_type


class Circle(PerimeterMixin, AreaMixin, Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius


class Rectangle(PerimeterMixin, AreaMixin, Shape):
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height
