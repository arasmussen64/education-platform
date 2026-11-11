"""Writes the topic ml.py.classes (Module 2's second topic). Run from the
repository root. Files are written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.classes")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.classes
kind: topic
status: ready
title: "Classes and objects"
summary: "Define a class with attributes and methods, and explain self."
prerequisites: [py.m6.checkpoint]
estimated_minutes: 60
rev: 1
objectives:
  - "Define a class with `__init__`, attributes and methods."
  - "Explain `self`, and tell a class from an instance."
  - "Give a class a readable `__repr__`."
resources:
  - title: "The Python Tutorial: Classes, sections 9.3 (A First Look at Classes) and 9.4 (Random Remarks) (Python Software Foundation)"
    url: https://docs.python.org/3/tutorial/classes.html#a-first-look-at-classes
    type: reading
    use: link
    license: PSF License Version 2
  - title: "Python for Everybody, chapter 14: Object-oriented programming (Dr. Chuck)"
    url: https://www.py4e.com/html3/14-objects
    type: reading
    use: link
    license: CC BY 4.0
practice:
  - example-a-class-is-a-blueprint
  - parsons-a-counter
  - mcq-what-self-is
  - predict-two-instances
  - mcq-class-or-instance
  - fill-rectangle-methods
  - write-temperature
prove:
  build: build-inventory
  debug: debug-forgotten-self
  explain:
    prompt: |
      A friend reads this and asks three questions:

      ```python
      class Account:
          def __init__(self, owner, balance):
              self.owner = owner
              self.balance = balance

          def deposit(self, amount):
              self.balance = self.balance + amount

      ada = Account("Ada", 100)
      ada.deposit(50)
      ```

      In your own words: what is the difference between `Account` and `ada`? What is `self`, and why does `deposit` have it as a parameter when `ada.deposit(50)` passes only one thing? And what would go wrong if `__init__` said `balance = balance` instead of `self.balance = balance`?
    rubric:
      - id: class-vs-instance
        required: true
        description: "Account is the class, the blueprint; ada is an instance, one object made from it, with its own owner and balance."
      - id: self
        required: true
        description: "self is the instance a method was called on: ada.deposit(50) is Account.deposit(ada, 50), so Python fills self in with ada."
      - id: attributes
        required: true
        description: "self.balance = balance stores the value on the object so other methods can see it; a plain balance = balance makes a local variable that vanishes when __init__ ends, and deposit would fail with no balance attribute."
      - id: repr
        required: false
        description: "Mentions that each instance keeps its own state (a second account is unaffected by ada's deposit), or that __repr__ makes an object print readably."
    model_answer: |
      Account is the class: the blueprint that says every account has an owner and a balance and knows how to deposit. ada is an instance: one actual account made from the blueprint, with its own owner "Ada" and its own balance; a second Account would have its own, and ada's deposit wouldn't touch it. self is the instance the method was called on. When you write ada.deposit(50), Python turns it into Account.deposit(ada, 50): ada goes into self, 50 into amount. That's why every method lists self first and callers never pass it. Inside __init__, self.balance = balance stores the value on the object, where deposit can find it later as self.balance. A plain balance = balance would just make a local variable that disappears when __init__ returns, so the object would have no balance attribute and ada.deposit(50) would fail with an AttributeError.
review_pool:
  - review-predict-method-changes-state
  - review-mcq-when-init-runs
  - review-point-class
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: define
    description: "Define a class with __init__ and attributes"
  - id: methods
    description: "Write methods that use self to read and change the object's attributes"
  - id: instances
    description: "Tell a class from an instance, and know that each instance keeps its own state"
  - id: repr
    description: "Give a class a readable __repr__"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

So far your programs have kept data in variables, lists and dicts, and behaviour in functions. A class puts the two together: a blueprint for objects that carry their own data and know what to do with it. Every library you'll use in machine learning hands you objects made this way, so reading a class has to be second nature before writing one is.

The main resource is the official Python tutorial's chapter on classes, **sections 9.3 and 9.4**. About 20 minutes; it's dense, so read 9.3 twice and skim 9.4. Watch for:

- **A class is a blueprint; an instance is one object made from it.** `Account` against `ada = Account("Ada", 100)`.
- **`__init__`** runs when an instance is made, and stores the starting values on `self`.
- **`self`** is the instance a method was called on. `ada.deposit(50)` is `Account.deposit(ada, 50)`.
- **Attributes** live on the object (`self.balance`); local variables inside a method vanish when it returns.

Python for Everybody's chapter 14 tells the same story more slowly, if the tutorial moves too fast.

</Intro>

<Resource index={0} />

<Recap>

- **A class is a blueprint.** `class Account:` describes what every account has and does. **An instance** is one object made from it: `ada = Account("Ada", 100)`. Two instances are two separate objects with their own data.
- **`__init__`** is the method Python calls when an instance is made. Its job is to store the starting values **on the object**: `self.owner = owner`. A plain `owner = owner` makes a local variable that vanishes when `__init__` returns, and the object has no `owner` attribute.
- **`self`** is the instance a method was called on. Every method lists it first; callers never pass it. `ada.deposit(50)` is `Account.deposit(ada, 50)`.
- **Methods** are functions inside the class that read and change the object through `self`: `self.balance = self.balance + amount`.
- **Attributes** are the data on an object: `ada.balance`. You can read them from outside (`print(ada.balance)`), and methods are the polite way to change them.
- **`__repr__`** returns the text Python shows for the object: `Account('Ada', 150)` instead of `<__main__.Account object at 0x...>`. Make it look like the call that would recreate the object; `{self.owner!r}` puts quotes around a string.
- **Naming:** classes are `CapitalWords`, instances and methods are `snake_case`.
- **In machine learning:** a model is an object (`model = LinearRegression()`), training is a method call (`model.fit(x, y)`), and the learned numbers are attributes (`model.coef_`). You'll write your own in Module 8.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-a-counter.yaml",
    '''id: parsons-a-counter
type: parsons
rev: 1
prompt: |
  Put the lines in order to define a `Counter` class, make one, count twice and print `2`. One line is a decoy that doesn't belong.
lines:
  - 'class Counter:'
  - '    def __init__(self):'
  - '        self.count = 0'
  - '    def increment(self):'
  - '        self.count = self.count + 1'
  - 'clicks = Counter()'
  - 'for click in range(2):'
  - '    clicks.increment()'
  - 'print(clicks.count)'
distractors:
  - '        count = count + 1'
explanation: |
  The class comes first: `__init__` gives each new counter its own `count`, starting at 0, and `increment` adds one to **`self.count`**, the attribute on the object. Then an instance is made and its method called twice, by the loop. The decoy, `count = count + 1`, would refer to a local variable that doesn't exist, and change nothing on the object.
skills: [define, methods]
''',
)

write(
    "recall/mcq-what-self-is.yaml",
    '''id: mcq-what-self-is
type: mcq
rev: 1
prompt: |
  In `ada.deposit(50)`, where `deposit` is defined as `def deposit(self, amount):`, what is `self`?
choices:
  - 'The class `Account`'
  - 'The number 50'
  - 'The instance `ada`, which Python passes in for you'
  - 'A keyword that every function must have'
answer: 2
explanation: |
  `ada.deposit(50)` is short for `Account.deposit(ada, 50)`: the object the method was called on goes into the first parameter, by convention named `self`, and `50` goes into `amount`. `self` isn't a keyword, just the name everyone uses, and only methods have it.
skills: [methods]
''',
)

write(
    "recall/predict-two-instances.yaml",
    '''id: predict-two-instances
type: predict_output
rev: 1
prompt: |
  Two objects from one class. What does the program print?
code: |
  class Jar:
      def __init__(self, coins):
          self.coins = coins

      def add(self, n):
          self.coins = self.coins + n


  a = Jar(3)
  b = Jar(10)
  a.add(2)
  print(a.coins)
  print(b.coins)
expected_output: |
  5
  10
explanation: |
  Each instance has its own `coins`. `a.add(2)` changes `a.coins` from 3 to `5`, and `b` is untouched: `10`. That's the point of instances: the same blueprint, separate state.
skills: [instances]
''',
)

write(
    "recall/mcq-class-or-instance.yaml",
    '''id: mcq-class-or-instance
type: mcq
rev: 1
prompt: |
  After `class Dog:` ... and `rex = Dog("Rex")`, which statement is right?
choices:
  - '`Dog` is an instance and `rex` is a class'
  - '`Dog` is a class, the blueprint; `rex` is an instance, one dog made from it'
  - '`Dog` and `rex` are two names for the same object'
  - '`rex` is a method of `Dog`'
answer: 1
explanation: |
  The class is the description; the instance is a thing made from it. You can make many instances from one class (`rex`, `fido`), each with its own attributes. Calling the class like a function, `Dog("Rex")`, is what makes an instance.
skills: [instances]
''',
)

write(
    "recall/review-predict-method-changes-state.yaml",
    '''id: review-predict-method-changes-state
type: predict_output
rev: 1
prompt: |
  A method that changes the object, called twice. What does the program print?
code: |
  class Thermostat:
      def __init__(self, target):
          self.target = target

      def warmer(self):
          self.target = self.target + 1

      def __repr__(self):
          return f"Thermostat({self.target})"


  home = Thermostat(19)
  home.warmer()
  home.warmer()
  print(home)
expected_output: |
  Thermostat(21)
explanation: |
  Each `warmer()` adds one to `self.target`, the attribute on `home`: 19, 20, 21. `print(home)` shows what `__repr__` returns, `Thermostat(21)`, instead of the unreadable default.
skills: [methods, repr]
''',
)

write(
    "recall/review-mcq-when-init-runs.yaml",
    '''id: review-mcq-when-init-runs
type: mcq
rev: 1
prompt: |
  When does a class's `__init__` method run?
choices:
  - 'Once, when Python reads the `class` statement'
  - 'Every time an instance is made, as in `Account("Ada", 100)`'
  - 'Only when you call it yourself, as in `ada.__init__()`'
  - 'Every time any method of the object is called'
answer: 1
explanation: |
  `__init__` is the set-up step for a new object. Calling the class, `Account("Ada", 100)`, creates the instance and then runs `__init__` on it with those arguments, which is where the attributes get their starting values. Making a second instance runs it again, for that one.
skills: [define]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-a-class-is-a-blueprint/exercise.yaml",
    '''id: example-a-class-is-a-blueprint
stage: worked_example
rev: 1
title: "A class is a blueprint"
prompt: |
  This program defines a bank account class, makes two accounts and uses them. Press **Run**, then read how each part works.
steps:
  - label: "The blueprint"
    lines: "1-4"
    note: "`class Account:` starts the blueprint. `__init__` runs for each new account and stores its starting values on the object: `self.owner`, `self.balance`. `balance=0` is a default, used when the caller leaves it out."
  - label: "A method"
    lines: "6-7"
    note: "`deposit` changes the account it was called on, through `self`. There's no return: the point is the change to `self.balance`."
  - label: "A readable repr"
    lines: "9-10"
    note: "`__repr__` is what `print` shows. It's written to look like the call that would recreate the object; `!r` puts quotes around the owner's name."
  - label: "Two instances"
    lines: "13-18"
    note: "Two separate accounts from one class. `ada.deposit(50)` changes only Ada's balance; Bob's starts at the default 0 and gets its own deposit. `ada.balance` reads an attribute directly."
''',
)
write(
    "exercises/example-a-class-is-a-blueprint/solution.py",
    '''class Account:
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.balance = balance

    def deposit(self, amount):
        self.balance = self.balance + amount

    def __repr__(self):
        return f"Account({self.owner!r}, {self.balance})"


ada = Account("Ada", 100)
bob = Account("Bob")
ada.deposit(50)
bob.deposit(20)
print(ada)
print(bob)
print(ada.balance)
''',
)
write(
    "exercises/example-a-class-is-a-blueprint/test_exercise.py",
    '''from checks import run


def test_two_accounts():
    """Prints both accounts, then Ada's balance."""
    assert run() == "Account('Ada', 150)\\nAccount('Bob', 20)\\n150\\n"
''',
)

write(
    "exercises/fill-rectangle-methods/exercise.yaml",
    '''id: fill-rectangle-methods
stage: fill_in
rev: 1
title: "A rectangle's methods"
prompt: |
  Replace each `...` so the `Rectangle` class stores its width and height and can report its area and perimeter, and the program prints:

  ```
  12
  14
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "`__init__` stores the values **on the object**: `self.width = width`."
  - "Methods read them back through `self`: the area is `self.width * self.height`."
  - "Every method's first parameter is `self`, including `perimeter`."
skills: [define, methods]
''',
)
write(
    "exercises/fill-rectangle-methods/starter.py",
    '''class Rectangle:
    def __init__(self, width, height):
        ... = width
        self.height = height

    def area(self):
        return self.width * ...

    def perimeter(...):
        return 2 * (self.width + self.height)


box = Rectangle(3, 4)
print(box.area())
print(box.perimeter())
''',
)
write(
    "exercises/fill-rectangle-methods/solution.py",
    '''class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height

    def perimeter(self):
        return 2 * (self.width + self.height)


box = Rectangle(3, 4)
print(box.area())
print(box.perimeter())
''',
)
write(
    "exercises/fill-rectangle-methods/test_exercise.py",
    '''from checks import function, run


def test_three_by_four():
    """Prints 12, then 14."""
    printed = run()
    assert printed == "12\\n14\\n", f"Your program printed:\\n{printed}"


def test_another_rectangle():
    """A 5 by 2 rectangle has area 10 and perimeter 14."""
    Rectangle = function("Rectangle")
    other = Rectangle(5, 2)
    assert other.area() == 10
    assert other.perimeter() == 14
''',
)
write(
    "exercises/fill-rectangle-methods/wrong/typed-in.py",
    '''class Rectangle:
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
''',
)

write(
    "exercises/write-temperature/exercise.yaml",
    '''id: write-temperature
stage: write
rev: 1
title: "A temperature object"
prompt: |
  Write a class `Temperature` that stores a `celsius` attribute, has a method `fahrenheit()` returning the same temperature in Fahrenheit (`celsius * 9 / 5 + 32`), and a `__repr__` that looks like `Temperature(25)`. Then make one for 25 degrees and print its Fahrenheit value, then the object itself:

  ```
  77.0
  Temperature(25)
  ```
hints:
  - "`def __init__(self, celsius):` then `self.celsius = celsius`."
  - "`fahrenheit` takes only `self` and returns `self.celsius * 9 / 5 + 32`."
  - "`__repr__` returns an f-string: `f\\"Temperature({self.celsius})\\"`."
skills: [define, methods, repr]
''',
)
write("exercises/write-temperature/starter.py", "")
write(
    "exercises/write-temperature/solution.py",
    '''class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32

    def __repr__(self):
        return f"Temperature({self.celsius})"


room = Temperature(25)
print(room.fahrenheit())
print(room)
''',
)
write(
    "exercises/write-temperature/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints 77.0, then Temperature(25)."""
    printed = run()
    assert printed == "77.0\\nTemperature(25)\\n", f"Your program printed:\\n{printed}"


def test_other_temperatures():
    """Temperature(100) is 212.0 F, Temperature(-40) is -40.0 F, and each prints like the call that made it."""
    Temperature = function("Temperature")
    assert Temperature(100).fahrenheit() == 212.0
    assert Temperature(-40).fahrenheit() == -40.0
    assert repr(Temperature(100)) == "Temperature(100)"
''',
)
write(
    "exercises/write-temperature/wrong/no-repr.py",
    '''class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return self.celsius * 9 / 5 + 32


room = Temperature(25)
print(room.fahrenheit())
print("Temperature(25)")
''',
)
write(
    "exercises/write-temperature/wrong/typed-in.py",
    '''class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def fahrenheit(self):
        return 77.0

    def __repr__(self):
        return "Temperature(25)"


print(77.0)
print("Temperature(25)")
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-inventory/exercise.yaml",
    '''id: build-inventory
stage: build
rev: 1
title: "An inventory"
prompt: |
  Starting from a blank editor, write a class `Inventory` that keeps counts of items in a dict attribute called `counts`, starting empty. Give it `add(item, count)`, which adds to that item's count (starting it at 0 if it's new), `remove(item, count)`, which subtracts, `total()`, which returns the sum of all counts, and a `__repr__` that looks like `Inventory({'pen': 12, 'ink': 2})`.

  Then make one, add 10 pens, 2 inks and 5 more pens, remove 3 pens, and print the inventory and its total:

  ```
  Inventory({'pen': 12, 'ink': 2})
  14
  ```

  The checks make their own inventories too.
skills: [define, methods, repr, instances]
''',
)
write("exercises/build-inventory/starter.py", "")
write(
    "exercises/build-inventory/solution.py",
    '''class Inventory:
    def __init__(self):
        self.counts = {}

    def add(self, item, count):
        self.counts[item] = self.counts.get(item, 0) + count

    def remove(self, item, count):
        self.counts[item] = self.counts.get(item, 0) - count

    def total(self):
        return sum(self.counts.values())

    def __repr__(self):
        return f"Inventory({self.counts})"


stock = Inventory()
stock.add("pen", 10)
stock.add("ink", 2)
stock.add("pen", 5)
stock.remove("pen", 3)
print(stock)
print(stock.total())
''',
)
write(
    "exercises/build-inventory/test_exercise.py",
    '''from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the inventory, then its total."""
    assert run() == "Inventory({'pen': 12, 'ink': 2})\\n14\\n"


def test_counts_and_total():
    """add starts a new item at 0, remove subtracts, total adds everything up."""
    Inventory = function("Inventory")
    shelf = Inventory()
    shelf.add("cup", 4)
    shelf.add("cup", 1)
    shelf.remove("cup", 2)
    shelf.add("plate", 6)
    assert shelf.counts == {"cup": 3, "plate": 6}
    assert shelf.total() == 9


def test_instances_are_separate():
    """Two inventories keep their own counts."""
    Inventory = function("Inventory")
    first = Inventory()
    second = Inventory()
    first.add("pen", 1)
    assert second.counts == {}
    assert second.total() == 0
    assert repr(second) == "Inventory({})"
''',
)
write(
    "exercises/build-inventory/wrong/shared-counts.py",
    '''class Inventory:
    counts = {}

    def add(self, item, count):
        self.counts[item] = self.counts.get(item, 0) + count

    def remove(self, item, count):
        self.counts[item] = self.counts.get(item, 0) - count

    def total(self):
        return sum(self.counts.values())

    def __repr__(self):
        return f"Inventory({self.counts})"


stock = Inventory()
stock.add("pen", 10)
stock.add("ink", 2)
stock.add("pen", 5)
stock.remove("pen", 3)
print(stock)
print(stock.total())
''',
)
write(
    "exercises/build-inventory/wrong/add-replaces.py",
    '''class Inventory:
    def __init__(self):
        self.counts = {}

    def add(self, item, count):
        self.counts[item] = count

    def remove(self, item, count):
        self.counts[item] = self.counts.get(item, 0) - count

    def total(self):
        return sum(self.counts.values())

    def __repr__(self):
        return f"Inventory({self.counts})"


stock = Inventory()
stock.add("pen", 10)
stock.add("ink", 2)
stock.add("pen", 5)
stock.remove("pen", 3)
print(stock)
print(stock.total())
''',
)
write(
    "exercises/build-inventory/wrong/typed-in.py",
    '''class Inventory:
    def __init__(self):
        self.counts = {"pen": 12, "ink": 2}

    def add(self, item, count):
        pass

    def remove(self, item, count):
        pass

    def total(self):
        return 14

    def __repr__(self):
        return "Inventory({'pen': 12, 'ink': 2})"


print("Inventory({'pen': 12, 'ink': 2})")
print(14)
''',
)

write(
    "exercises/debug-forgotten-self/exercise.yaml",
    '''id: debug-forgotten-self
stage: debug
rev: 1
title: "The forgotten self"
prompt: |
  This program should track a player's score and print:

  ```
  Player('Ada', 30)
  30
  ```

  It has two bugs. Run it, read the error carefully, fix it, and run again; the second bug only shows once the first is fixed. Both are about `self`.
skills: [define, methods]
''',
)
write(
    "exercises/debug-forgotten-self/starter.py",
    '''class Player:
    def __init__(self, name):
        self.name = name
        score = 0

    def add_points(points):
        self.score = self.score + points

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
ada.add_points(10)
ada.add_points(20)
print(ada)
print(ada.score)
''',
)
write(
    "exercises/debug-forgotten-self/solution.py",
    '''class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def add_points(self, points):
        self.score = self.score + points

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
ada.add_points(10)
ada.add_points(20)
print(ada)
print(ada.score)
''',
)
write(
    "exercises/debug-forgotten-self/test_exercise.py",
    '''from checks import function, run

EXPECTED = "Player('Ada', 30)\\n30\\n"


def test_the_output():
    """Prints Player('Ada', 30), then 30."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_a_new_player_starts_at_zero():
    """A new Player has a score of 0, stored on the object."""
    Player = function("Player")
    bob = Player("Bob")
    assert bob.score == 0
    bob.add_points(7)
    assert bob.score == 7
''',
)
write(
    "exercises/debug-forgotten-self/wrong/only-parameter-fixed.py",
    '''class Player:
    def __init__(self, name):
        self.name = name
        score = 0

    def add_points(self, points):
        self.score = self.score + points

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
ada.add_points(10)
ada.add_points(20)
print(ada)
print(ada.score)
''',
)
write(
    "exercises/debug-forgotten-self/wrong/only-attribute-fixed.py",
    '''class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0

    def add_points(points):
        self.score = self.score + points

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
ada.add_points(10)
ada.add_points(20)
print(ada)
print(ada.score)
''',
)
write(
    "exercises/debug-forgotten-self/wrong/typed-in.py",
    '''class Player:
    def __init__(self, name):
        self.name = name
        self.score = 30

    def add_points(self, points):
        pass

    def __repr__(self):
        return f"Player({self.name!r}, {self.score})"


ada = Player("Ada")
print(ada)
print(ada.score)
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-point-class/exercise.yaml",
    '''id: review-point-class
stage: review_code
rev: 1
title: "A point and its distance"
prompt: |
  Write a class `Point` with `x` and `y` attributes and a method `distance_from_origin()` that returns the square root of `x ** 2 + y ** 2`. Then print the distance of the point (3, 4):

  ```
  5.0
  ```
skills: [define, methods]
''',
)
write("exercises/review-point-class/starter.py", "")
write(
    "exercises/review-point-class/solution.py",
    '''class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_from_origin(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


print(Point(3, 4).distance_from_origin())
''',
)
write(
    "exercises/review-point-class/test_exercise.py",
    '''from checks import function, run


def test_three_four():
    """Prints 5.0."""
    assert run() == "5.0\\n"


def test_other_points():
    """Point(6, 8) is 10.0 from the origin, and the attributes are x and y."""
    Point = function("Point")
    p = Point(6, 8)
    assert p.x == 6
    assert p.y == 8
    assert p.distance_from_origin() == 10.0
''',
)
write(
    "exercises/review-point-class/wrong/typed-in.py",
    '''class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_from_origin(self):
        return 5.0


print(5.0)
''',
)

print("ml.py.classes written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
