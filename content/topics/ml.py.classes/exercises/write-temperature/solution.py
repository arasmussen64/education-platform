class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    def __repr__(self):
        return f"Temperature({self.celsius})"


room = Temperature(25)
print(room.fahrenheit())
print(room)
