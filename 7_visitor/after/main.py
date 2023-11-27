from shape import Circle, Rectangle
from visitor import AreaPerimeterVisitor


shapes = [Circle(5), Rectangle(4, 6)]

visitor = AreaPerimeterVisitor()

for shape in shapes:
    area, perimeter = shape.accept(visitor)
    if isinstance(shape, Circle):
        print(f"Circle - Area: {area}, Perimeter: {perimeter}")
    elif isinstance(shape, Rectangle):
        print(f"Rectangle - Area: {area}, Perimeter: {perimeter}")
