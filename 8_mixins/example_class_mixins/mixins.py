class AreaMixin:
    '''
    Миксин для вычисления площади фигуры.
    '''
    def calculate_area(self):

        from shapes import Circle, Rectangle

        if isinstance(self, Circle):
            return 3.14 * self.radius ** 2
        elif isinstance(self, Rectangle):
            return self.width * self.height
        raise NotImplementedError("Unsupported shape type")


class PerimeterMixin:
    '''
    Миксин для вычисления периметра фигуры.
    '''
    def calculate_perimeter(self):

        from shapes import Circle, Rectangle

        if isinstance(self, Circle):
            return 2 * 3.14 * self.radius
        elif isinstance(self, Rectangle):
            return 2 * (self.width + self.height)
        raise NotImplementedError("Unsupported shape type")
