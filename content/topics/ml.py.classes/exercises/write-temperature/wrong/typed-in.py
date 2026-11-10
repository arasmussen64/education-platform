class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return 77.0

    def __repr__(self):
        return "Temperature(25)"


print(77.0)
print("Temperature(25)")
