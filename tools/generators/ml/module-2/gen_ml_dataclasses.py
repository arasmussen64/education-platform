"""Writes the topic ml.py.dataclasses-and-typing (Module 2's third topic).
Run from the repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.dataclasses-and-typing")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.dataclasses-and-typing
kind: topic
status: ready
title: "Dataclasses and type hints"
summary: "Records with @dataclass, and type hints that a checker can read."
prerequisites: [ml.py.classes]
estimated_minutes: 45
rev: 1
objectives:
  - "Declare a record with `@dataclass`."
  - "Annotate parameters and return values, and read a checker's error."
  - "Say what type hints do and don't do when the program runs."
resources:
  - title: "The Python Standard Library: dataclasses (Python Software Foundation), the opening example and the section on default values"
    url: https://docs.python.org/3/library/dataclasses.html
    type: reading
    use: link
    license: PSF License Version 2
  - title: "The Python Standard Library: typing, the opening (Python Software Foundation)"
    url: https://docs.python.org/3/library/typing.html
    type: reading
    use: link
    license: PSF License Version 2
practice:
  - example-a-record-as-a-dataclass
  - parsons-declare-a-point
  - mcq-what-hints-do
  - predict-dataclass-equality
  - mcq-read-a-signature
  - fill-annotate-area
  - write-student-record
prove:
  build: build-order-lines
  debug: debug-record-gone-wrong
  explain:
    prompt: |
      A teammate asks why your code has this instead of a plain class or a dict:

      ```python
      @dataclass
      class Reading:
          sensor: str
          value: float
          unit: str = "C"

      def average(readings: list[Reading]) -> float:
          ...
      ```

      In your own words: what does `@dataclass` write for you that you'd otherwise type by hand? What do the hints like `value: float` and `-> float` do when the program runs, and what are they for if not that? And when would you still reach for a dict, or for a hand-written class?
    rubric:
      - id: generated
        required: true
        description: "@dataclass generates __init__ (one parameter per field, in order, with the defaults), a readable __repr__ and an __eq__ that compares field by field."
      - id: runtime
        required: true
        description: "Hints change nothing when the program runs: Python doesn't check them, and Reading('a', 'not a number') is accepted. They're for readers and for tools (checkers and editors) that catch mistakes before running."
      - id: when-dict
        required: true
        description: "A dict suits data whose keys aren't known in advance or that came in as JSON; a dataclass suits a record with fixed named fields; a hand-written class suits behaviour that needs its own __init__ or state that changes in complicated ways."
      - id: defaults
        required: false
        description: "Mentions that fields with defaults must come after fields without, or that a mutable default like a list needs field(default_factory=list)."
    model_answer: |
      @dataclass looks at the field declarations and writes the boring methods for me: an __init__ that takes sensor, value and unit in that order with unit defaulting to "C"; a __repr__ that prints Reading(sensor='t1', value=21.5, unit='C'); and an __eq__ that says two readings are equal when all their fields are. That's twenty lines I don't write and can't get wrong. The hints, value: float and -> float, do nothing when the program runs: Python doesn't check them, so Reading("t1", "warm") is accepted and only fails later, if at all. They're documentation that tools can read: a type checker or an editor flags the mistake before the program runs, and a reader knows what average expects and returns without reading its body. I'd still use a dict for data whose keys I don't know in advance or that arrived as JSON and will be sent back as JSON, and a hand-written class when the object has real behaviour: an __init__ that does work, or state that changes in ways the generated methods wouldn't fit.
review_pool:
  - review-predict-defaults
  - review-mcq-return-none
  - review-temperature-record
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: dataclass
    description: "Declare a record with @dataclass, with defaults in the right place"
  - id: hints
    description: "Annotate parameters and return values, and read a signature's hints"
  - id: runtime
    description: "Say what type hints do and don't do when the program runs"
  - id: record-methods
    description: "Give a dataclass a method that uses its fields"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Most classes you'll write are records: a few named fields, made once, compared and printed. Python can write those classes for you from a list of fields, and the same field list doubles as documentation of what each one holds. Type hints are that documentation everywhere else: on parameters and return values, where a reader or a tool can check them.

The main resource is the standard library's **dataclasses** page: the opening example and the section on default values, about 10 minutes. Then the first screen of the **typing** page, just to see the vocabulary. Watch for:

- **`@dataclass` on a class with annotated fields** writes `__init__`, `__repr__` and `__eq__` for you.
- **Fields with defaults** come after fields without.
- **Hints are for readers and tools.** `def mean(values: list[float]) -> float:` says what goes in and what comes out; Python itself doesn't enforce it.

You wrote `__init__` and `__repr__` by hand in the last topic. Here you'll see what that bought you: the understanding to read what `@dataclass` generates.

</Intro>

<Resource index={0} />

<Recap>

- **A dataclass is a class written from its fields.** `@dataclass` above `class Book:` with `title: str`, `pages: int`, `price: float = 0.0` generates `__init__(self, title, pages, price=0.0)`, a `__repr__` that prints `Book(title='Dune', pages=412, price=9.99)`, and `__eq__` that compares field by field.
- **Fields with defaults come last.** `price: float = 0.0` after `pages: int`, never before. A list default needs `field(default_factory=list)`, so every instance gets its own list.
- **Methods work as in any class:** `def average(self) -> float:` inside the dataclass uses `self.grades` like before.
- **Type hints** go after a colon for parameters and after `->` for the return: `def area(width: float, height: float) -> float:`. Common ones: `int`, `float`, `str`, `bool`, `list[int]`, `dict[str, float]`, `None` for a function that returns nothing.
- **Hints don't run.** Python doesn't check them: `area("2", 3)` still runs until something inside fails. They're for readers, for editors that complete and warn, and for checkers like `mypy` or `pyright` that read the whole program and point at mismatches before you run it. A hint is a promise, not a guard.
- **When to use what:** a dataclass for a record with fixed named fields; a dict for data whose keys aren't fixed or that came from JSON; a hand-written class when `__init__` has real work to do.
- **In machine learning:** configuration objects (`@dataclass class TrainingConfig: learning_rate: float = 0.01 ...`), hinted function signatures in every library, and a type checker catching a tensor passed where a list was expected.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-declare-a-point.yaml",
    '''id: parsons-declare-a-point
type: parsons
rev: 1
prompt: |
  Put the lines in order to declare a `Point` dataclass with two float fields, make one and print `Point(x=1.5, y=2.0)`. One line is a decoy that doesn't belong.
lines:
  - 'from dataclasses import dataclass'
  - '@dataclass'
  - 'class Point:'
  - '    x: float'
  - '    y: float'
  - 'p = Point(1.5, 2.0)'
  - 'print(p)'
distractors:
  - '    x = float'
explanation: |
  The import comes first, then the decorator directly above the class, then the fields as **annotations** (`x: float`). The decoy, `x = float`, is an assignment: it would make a class attribute whose value is the type `float`, not a field, and `@dataclass` would ignore it. The generated `__repr__` prints the fields by name.
skills: [dataclass]
''',
)

write(
    "recall/mcq-what-hints-do.yaml",
    '''id: mcq-what-hints-do
type: mcq
rev: 1
prompt: |
  Given `def double(n: int) -> int: return n * 2`, what happens when the program runs `double("ab")`?
choices:
  - 'Python raises an error because `"ab"` is not an `int`'
  - 'It returns `"abab"`: the hints are not checked when the program runs'
  - 'It returns `0`, the default for an `int`'
  - 'Python converts `"ab"` to an `int` first'
answer: 1
explanation: |
  Hints are read by people and by tools such as type checkers and editors; the running program ignores them. `"ab" * 2` is `"abab"`, so that's what comes back. A checker like `mypy` would have flagged the call before the program ran, which is the point of writing the hint.
skills: [runtime]
''',
)

write(
    "recall/predict-dataclass-equality.yaml",
    '''id: predict-dataclass-equality
type: predict_output
rev: 1
prompt: |
  Two objects with the same contents, from a dataclass and from a plain class. What does the program print?
code: |
  from dataclasses import dataclass


  @dataclass
  class Point:
      x: float
      y: float


  class Plain:
      def __init__(self, x):
          self.x = x


  print(Point(1, 2) == Point(1, 2))
  print(Plain(1) == Plain(1))
expected_output: |
  True
  False
explanation: |
  `@dataclass` generates an `__eq__` that compares field by field, so two points with the same coordinates are equal: `True`. A plain class without `__eq__` compares by identity: two separate objects are never equal, however alike, so `False`.
skills: [dataclass, runtime]
''',
)

write(
    "recall/mcq-read-a-signature.yaml",
    '''id: mcq-read-a-signature
type: mcq
rev: 1
prompt: |
  What does this signature promise?

  ```python
  def mean(values: list[float]) -> float:
  ```
choices:
  - '`mean` takes a list of floats and returns a float'
  - '`mean` takes a float and returns a list of floats'
  - '`mean` converts its argument to a list of floats'
  - '`mean` can only be called with exactly one float'
answer: 0
explanation: |
  The hint after the colon describes the parameter: `values` should be a `list` whose items are `float`. The hint after `->` describes the return value: a single `float`. It's a promise to the reader and to tools, not a conversion or a check.
skills: [hints]
''',
)

write(
    "recall/review-predict-defaults.yaml",
    '''id: review-predict-defaults
type: predict_output
rev: 1
prompt: |
  A dataclass with two defaults, used two ways. What does the program print?
code: |
  from dataclasses import dataclass


  @dataclass
  class Config:
      name: str
      retries: int = 3
      verbose: bool = False


  print(Config("job"))
  print(Config("job", verbose=True))
expected_output: |
  Config(name='job', retries=3, verbose=False)
  Config(name='job', retries=3, verbose=True)
explanation: |
  The generated `__init__` takes the fields in order, with the defaults filled in when a caller leaves them out. The second call names `verbose` so it can skip `retries`, which keeps its default of 3. The `__repr__` prints every field, defaults included.
skills: [dataclass]
''',
)

write(
    "recall/review-mcq-return-none.yaml",
    '''id: review-mcq-return-none
type: mcq
rev: 1
prompt: |
  Which hint belongs on a function that prints a report and returns nothing?
choices:
  - '`-> None`'
  - '`-> str`'
  - '`-> print`'
  - 'No hint is possible for a function that returns nothing'
answer: 0
explanation: |
  A function that falls off the end returns `None`, and `-> None` says so: it tells a reader not to expect a value, and lets a checker flag `result = report()` as a mistake. `-> str` would promise text that never comes.
skills: [hints]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-a-record-as-a-dataclass/exercise.yaml",
    '''id: example-a-record-as-a-dataclass
stage: worked_example
rev: 1
title: "A record as a dataclass"
prompt: |
  This program declares a `Book` record with `@dataclass`, makes two books and uses what the decorator generated. Press **Run**, then read how each part works.
steps:
  - label: "Declare the fields"
    lines: "1-8"
    note: "`@dataclass` above the class, then one annotated field per line. `price` has a default, so it comes last. That's the whole class: `__init__`, `__repr__` and `__eq__` are generated from these three lines."
  - label: "Make records"
    lines: "11-12"
    note: "The generated `__init__` takes the fields in order; `hobbit` leaves out the price and gets the default 0.0."
  - label: "Print and compare"
    lines: "13-15"
    note: "The generated `__repr__` prints every field by name. The generated `__eq__` compares field by field, so a second `Book('Dune', 412, 9.99)` equals the first."
  - label: "A hinted function"
    lines: "18-22"
    note: "`books: list[Book]` and `-> int` say what goes in and what comes out. Python doesn't check them; a reader and a type checker do."
''',
)
write(
    "exercises/example-a-record-as-a-dataclass/solution.py",
    '''from dataclasses import dataclass


@dataclass
class Book:
    title: str
    pages: int
    price: float = 0.0


dune = Book("Dune", 412, 9.99)
hobbit = Book("The Hobbit", 310)
print(dune)
print(hobbit)
print(dune == Book("Dune", 412, 9.99))


def total_pages(books: list[Book]) -> int:
    total = 0
    for book in books:
        total = total + book.pages
    return total


print(total_pages([dune, hobbit]))
''',
)
write(
    "exercises/example-a-record-as-a-dataclass/test_exercise.py",
    '''from checks import run


def test_the_books():
    """Prints both books, True, then 722."""
    assert run() == (
        "Book(title='Dune', pages=412, price=9.99)\\n"
        "Book(title='The Hobbit', pages=310, price=0.0)\\nTrue\\n722\\n"
    )
''',
)

write(
    "exercises/fill-annotate-area/exercise.yaml",
    '''id: fill-annotate-area
stage: fill_in
rev: 1
title: "Annotate a function"
prompt: |
  Replace each `...` with a type hint so that `area` promises float parameters and a float result, and the program prints:

  ```
  10.0
  ```

  The checks read the hints off the function, so they have to be there.
hints:
  - "A parameter's hint goes after a colon: `width: float`."
  - "The return hint goes after `->`, before the final colon."
skills: [hints]
''',
)
write(
    "exercises/fill-annotate-area/starter.py",
    '''def area(width: ..., height: ...) -> ...:
    return width * height


print(area(2.5, 4))
''',
)
write(
    "exercises/fill-annotate-area/solution.py",
    '''def area(width: float, height: float) -> float:
    return width * height


print(area(2.5, 4))
''',
)
write(
    "exercises/fill-annotate-area/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints 10.0."""
    printed = run()
    assert printed == "10.0\\n", f"Your program printed:\\n{printed}"


def test_the_hints():
    """area's parameters and return value are hinted as float."""
    area = function("area")
    assert area.__annotations__ == {"width": float, "height": float, "return": float}, (
        f"The hints on area are {area.__annotations__}"
    )
''',
)
write(
    "exercises/fill-annotate-area/wrong/hinted-as-int.py",
    '''def area(width: int, height: int) -> int:
    return width * height


print(area(2.5, 4))
''',
)
write(
    "exercises/fill-annotate-area/wrong/typed-in.py",
    '''def area(width, height):
    return width * height


print(10.0)
''',
)

write(
    "exercises/write-student-record/exercise.yaml",
    '''id: write-student-record
stage: write
rev: 1
title: "A student record"
prompt: |
  Declare a dataclass `Student` with a `name` (a `str`) and `grades` (a `list[int]`), and give it a method `average(self) -> float` that returns the mean of the grades. Then make Ada with grades 80, 90 and 100, and print the record and her average:

  ```
  Student(name='Ada', grades=[80, 90, 100])
  90.0
  ```
hints:
  - "`from dataclasses import dataclass`, then `@dataclass` above `class Student:`."
  - "Fields are annotations: `name: str` and `grades: list[int]`."
  - "The method is ordinary: `def average(self) -> float:` returning `sum(self.grades) / len(self.grades)`."
skills: [dataclass, record-methods, hints]
''',
)
write("exercises/write-student-record/starter.py", "")
write(
    "exercises/write-student-record/solution.py",
    '''from dataclasses import dataclass


@dataclass
class Student:
    name: str
    grades: list[int]

    def average(self) -> float:
        return sum(self.grades) / len(self.grades)


ada = Student("Ada", [80, 90, 100])
print(ada)
print(ada.average())
''',
)
write(
    "exercises/write-student-record/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints the record, then 90.0."""
    printed = run()
    assert printed == "Student(name='Ada', grades=[80, 90, 100])\\n90.0\\n", f"Your program printed:\\n{printed}"


def test_the_dataclass():
    """Student is a dataclass: equal records compare equal, and average works for other grades."""
    Student = function("Student")
    assert Student("Bob", [70, 75]) == Student("Bob", [70, 75])
    assert Student("Bob", [70, 75]).average() == 72.5
    assert Student.__dataclass_fields__.keys() == {"name", "grades"}
''',
)
write(
    "exercises/write-student-record/wrong/plain-class.py",
    '''class Student:
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
''',
)
write(
    "exercises/write-student-record/wrong/typed-in.py",
    '''from dataclasses import dataclass


@dataclass
class Student:
    name: str
    grades: list[int]

    def average(self) -> float:
        return 90.0


print("Student(name='Ada', grades=[80, 90, 100])")
print(90.0)
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-order-lines/exercise.yaml",
    '''id: build-order-lines
stage: build
rev: 1
title: "Order lines"
prompt: |
  Starting from a blank editor, declare a dataclass `Line` with an `item` (`str`), a `quantity` (`int`) and a `unit_price` (`float`), and a method `total(self) -> float` returning quantity times unit price. Then write a function `order_total(lines: list[Line]) -> float` that adds up the totals of the lines. Finally make two lines, 3 pens at 1.5 and 2 notebooks at 4.25, and print the first line and the order total:

  ```
  Line(item='pen', quantity=3, unit_price=1.5)
  13.0
  ```

  The checks make their own lines, compare them, and read the hints on `order_total`.
skills: [dataclass, record-methods, hints]
''',
)
write("exercises/build-order-lines/starter.py", "")
write(
    "exercises/build-order-lines/solution.py",
    '''from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self) -> float:
        return self.quantity * self.unit_price


def order_total(lines: list[Line]) -> float:
    total = 0.0
    for line in lines:
        total = total + line.total()
    return total


order = [Line("pen", 3, 1.5), Line("notebook", 2, 4.25)]
print(order[0])
print(order_total(order))
''',
)
write(
    "exercises/build-order-lines/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the first line, then 13.0."""
    assert run() == "Line(item='pen', quantity=3, unit_price=1.5)\\n13.0\\n"


def test_the_record():
    """Line is a dataclass with the three fields; equal lines compare equal; total multiplies."""
    Line = function("Line")
    assert Line.__dataclass_fields__.keys() == {"item", "quantity", "unit_price"}
    assert Line("a", 1, 2.0) == Line("a", 1, 2.0)
    assert Line("tape", 4, 0.75).total() == 3.0


def test_order_total_and_its_hints():
    """order_total adds the lines up, is 0 for no lines, and is hinted to return a float."""
    Line = function("Line")
    order_total = function("order_total")
    assert order_total([Line("a", 2, 1.5), Line("b", 1, 2.0)]) == 5.0
    assert order_total([]) == 0
    assert order_total.__annotations__.get("return") is float
''',
)
write(
    "exercises/build-order-lines/wrong/no-hints.py",
    '''from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self):
        return self.quantity * self.unit_price


def order_total(lines):
    total = 0.0
    for line in lines:
        total = total + line.total()
    return total


order = [Line("pen", 3, 1.5), Line("notebook", 2, 4.25)]
print(order[0])
print(order_total(order))
''',
)
write(
    "exercises/build-order-lines/wrong/forgets-quantity.py",
    '''from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self) -> float:
        return self.unit_price


def order_total(lines: list[Line]) -> float:
    total = 0.0
    for line in lines:
        total = total + line.total()
    return total


order = [Line("pen", 3, 1.5), Line("notebook", 2, 4.25)]
print(order[0])
print(order_total(order))
''',
)
write(
    "exercises/build-order-lines/wrong/typed-in.py",
    '''from dataclasses import dataclass


@dataclass
class Line:
    item: str
    quantity: int
    unit_price: float

    def total(self) -> float:
        return 4.5


def order_total(lines: list[Line]) -> float:
    return 13.0


print("Line(item='pen', quantity=3, unit_price=1.5)")
print(13.0)
''',
)

write(
    "exercises/debug-record-gone-wrong/exercise.yaml",
    '''id: debug-record-gone-wrong
stage: debug
rev: 1
title: "A record gone wrong"
prompt: |
  This program should declare a `Ticket` record and print one, then the price of two of them:

  ```
  Ticket(event='Concert', price=45.0, row='B')
  90.0
  ```

  It has two bugs. Run it, read the error, fix it, and run again; the second bug shows only once the first is fixed, and it's about what a default's value is, not where it sits.
skills: [dataclass, runtime]
''',
)
write(
    "exercises/debug-record-gone-wrong/starter.py",
    '''from dataclasses import dataclass


class Ticket:
    event: str
    price: float = "45.0"
    row: str = "B"


one = Ticket("Concert")
print(one)
print(one.price * 2)
''',
)
write(
    "exercises/debug-record-gone-wrong/solution.py",
    '''from dataclasses import dataclass


@dataclass
class Ticket:
    event: str
    price: float = 45.0
    row: str = "B"


one = Ticket("Concert")
print(one)
print(one.price * 2)
''',
)
write(
    "exercises/debug-record-gone-wrong/test_exercise.py",
    '''from checks import function, run

EXPECTED = "Ticket(event='Concert', price=45.0, row='B')\\n90.0\\n"


def test_the_output():
    """Prints the ticket, then 90.0."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_the_record():
    """Ticket is a dataclass whose default price is the number 45.0."""
    Ticket = function("Ticket")
    assert Ticket.__dataclass_fields__.keys() == {"event", "price", "row"}
    assert Ticket("Play").price == 45.0
    assert Ticket("Play", 10.0, "A") == Ticket("Play", 10.0, "A")
''',
)
write(
    "exercises/debug-record-gone-wrong/wrong/only-decorator-fixed.py",
    '''from dataclasses import dataclass


@dataclass
class Ticket:
    event: str
    price: float = "45.0"
    row: str = "B"


one = Ticket("Concert")
print(one)
print(one.price * 2)
''',
)
write(
    "exercises/debug-record-gone-wrong/wrong/typed-in.py",
    '''from dataclasses import dataclass


class Ticket:
    def __init__(self, event):
        self.event = event
        self.price = 45.0
        self.row = "B"


print("Ticket(event='Concert', price=45.0, row='B')")
print(90.0)
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-temperature-record/exercise.yaml",
    '''id: review-temperature-record
stage: review_code
rev: 1
title: "A temperature record"
prompt: |
  Declare a dataclass `Temperature` with one field, `celsius` (a `float`), and a method `fahrenheit(self) -> float` returning `celsius * 9 / 5 + 32`. Then print a 25-degree temperature and its Fahrenheit value:

  ```
  Temperature(celsius=25)
  77.0
  ```
skills: [dataclass, record-methods]
''',
)
write("exercises/review-temperature-record/starter.py", "")
write(
    "exercises/review-temperature-record/solution.py",
    '''from dataclasses import dataclass


@dataclass
class Temperature:
    celsius: float

    def fahrenheit(self) -> float:
        return self.celsius * 9 / 5 + 32


room = Temperature(25)
print(room)
print(room.fahrenheit())
''',
)
write(
    "exercises/review-temperature-record/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints Temperature(celsius=25), then 77.0."""
    assert run() == "Temperature(celsius=25)\\n77.0\\n"


def test_the_record():
    """Temperature is a dataclass, and 100 C is 212.0 F."""
    Temperature = function("Temperature")
    assert Temperature.__dataclass_fields__.keys() == {"celsius"}
    assert Temperature(100).fahrenheit() == 212.0
''',
)
write(
    "exercises/review-temperature-record/wrong/typed-in.py",
    '''class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return 77.0


print("Temperature(celsius=25)")
print(77.0)
''',
)

print("ml.py.dataclasses-and-typing written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
