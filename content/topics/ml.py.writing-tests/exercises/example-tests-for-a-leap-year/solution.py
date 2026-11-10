def is_leap(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def test_every_fourth_year_is_leap():
    assert is_leap(2024)
    assert not is_leap(2023)


def test_centuries_are_not_leap():
    assert not is_leap(1900)


def test_every_fourth_century_is_leap():
    assert is_leap(2000)


passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
        print(name, "passed")
print(passed, "passed")
