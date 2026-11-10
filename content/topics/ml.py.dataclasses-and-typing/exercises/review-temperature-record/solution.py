from dataclasses import dataclass


@dataclass
class Temperature:
    celsius: float

    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32


room = Temperature(25)
print(room)
print(room.fahrenheit())
