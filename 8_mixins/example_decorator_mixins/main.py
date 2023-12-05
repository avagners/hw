from shapes import Circle, Rectangle

shapes = [Circle(5), Rectangle(4, 6)]

for shape in shapes:
    area = shape.calculate_area()
    perimeter = shape.calculate_perimeter()
    print(f"{shape.shape_type} - Area: {area}, Perimeter: {perimeter}")
    print(type(shape))
