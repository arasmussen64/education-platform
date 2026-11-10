class Student:
    def __init__(self, name, grades):
        self.name = name
        self.grades = grades

    def average(self):
        return sum(self.grades) / len(self.grades)

    def __repr__(self):
        return f"Student(name={self.name!r}, grades={self.grades})"


ada = Student("Ada", [80, 90, 100])
print(ada)
print(ada.average())
