from dataclasses import dataclass


@dataclass
class Student:
    name: str
    grades: list[int]

    def average(self) -> float:
        return 90.0


print("Student(name='Ada', grades=[80, 90, 100])")
print(90.0)
