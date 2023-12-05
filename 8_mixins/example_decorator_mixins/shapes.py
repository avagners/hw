from abc import ABC

from mixins import calculate_area_mixin, calculate_perimeter_mixin


class Shape(ABC):
    def __init__(self, shape_type):
        self.shape_type = shape_type


@calculate_area_mixin
@calculate_perimeter_mixin
class Circle(Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius


@calculate_area_mixin
@calculate_perimeter_mixin
class Rectangle(Shape):
    def __init__(self, width, height):
        super().__init__("Rectangle")
        self.width = width
        self.height = height
