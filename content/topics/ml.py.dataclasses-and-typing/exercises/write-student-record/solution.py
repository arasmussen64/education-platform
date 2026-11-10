from dataclasses import dataclass


@dataclass
class Student:
    name: str
    grades: list[int]

    def average(self) -> float:
        return sum(self.grades) / len(self.grades)


ada = Student("Ada", [80, 90, 100])
print(ada)
print(ada.average())
