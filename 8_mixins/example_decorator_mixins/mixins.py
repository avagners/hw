# Декоратор-миксин для вычисления площади
def calculate_area_mixin(cls):

    class ShapeWithArea(cls):

        def calculate_area(self):

            from shapes import Circle, Rectangle

            if isinstance(self, Circle):
                return 3.14 * self.radius ** 2
            elif isinstance(self, Rectangle):
                return self.width * self.height
            raise NotImplementedError("Unsupported shape type")

    return ShapeWithArea


# Декоратор-миксин для вычисления периметра
def calculate_perimeter_mixin(cls):

    class ShapeWithPerimeter(cls):

        def calculate_perimeter(self):

            from shapes import Circle, Rectangle

            if isinstance(self, Circle):
                return 2 * 3.14 * self.radius
            elif isinstance(self, Rectangle):
                return 2 * (self.width + self.height)
            raise NotImplementedError("Unsupported shape type")

    return ShapeWithPerimeter
