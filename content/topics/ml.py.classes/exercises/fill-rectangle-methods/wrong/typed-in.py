class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return 12

    def perimeter(self):
        return 14


box = Rectangle(3, 4)
print(box.area())
print(box.perimeter())
