from abc import ABC, abstractmethod


class Shape(ABC):

    @abstractmethod
    def calculate_area(self): ...

    @abstractmethod
    def calculate_perimeter(self): ...


class Circle(Shape):

    def __init__(self, radius):
        self.radius = radius

    def calculate_area(self):
        return 3.14 * self.radius ** 2

    def calculate_perimeter(self):
        return 2 * 3.14 * self.radius


class Rectangle(Shape):

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def calculate_area(self):
        return self.width * self.height

    def calculate_perimeter(self):
        return 2 * (self.width + self.height)


if __name__ == "__main__":
    shapes = [Circle(5), Rectangle(4, 6)]

    for shape in shapes:
        if isinstance(shape, Circle):
            area = shape.calculate_area()
            perimeter = shape.calculate_perimeter()
            print(f"Circle - Area: {area}, Perimeter: {perimeter}")
        elif isinstance(shape, Rectangle):
            area = shape.calculate_area()
            perimeter = shape.calculate_perimeter()
            print(f"Rectangle - Area: {area}, Perimeter: {perimeter}")
