# Devlog

A dated log of each working session: what changed, what was decided, what's next. Newest first.

## 2026-11-10: JSON and nested data

**`ml.py.json-and-nested-data` is ready,** the last topic before Checkpoint 2. Reading JSON is one call; the topic is about the shape of what arrives never being quite what was expected. The worked example writes a record with `dumps`, reads it back with `loads`, shows `True` and `None` becoming `true` and `null`, and goes through a file with `dump` and `load`. Then a Parsons load whose decoy calls `json.load` on a string, three recall questions (a set is the thing `dumps` can't write; `.get` with and without a default and `in` on a record with missing keys; what to do about an `age` that arrived as `"42"`), a `city_of` lookup to fill in that survives a missing address, a `None` address and an address with no city, and sensor readings to write: JSON text into `Reading` dataclasses with the value converted to a float, and back out through `asdict`. The proofs: orders to validate, returning the good ones as dataclasses and the positions of the bad ones, with "don't repair records" in the prompt and the hidden tests feeding a float quantity, a record that's a number, a missing key and a string quantity (known-wrong: a version that repairs `"5"` with `int()`, one that accepts a quantity of 0); a nested walk to debug with `json.load` on a string and square brackets on a user without orders; and an explanation built on a partner's nightly file that crashed two nights running. The review pool has five: the type map both ways, `loads` against `load`, `asdict` before `dumps`, where to validate, and the total of nested lists.

**Decisions for you to review:**

1. _Both resources are the official docs,_ the tutorial's JSON section and the type table, rather than a longer third-party chapter: the mechanics take ten minutes to read, and the judgement (safe walking, validating at the boundary) is in the Recap and the exercises.
2. _Booleans aren't tested as bad integers._ In Python `True` is an int, so `isinstance(True, int)` passes a quantity of `true`; the hidden tests don't send one, because the point of the build is the boundary habit, not that corner. It's noted here for a later topic.
3. _JSON Lines is a Recap bullet,_ not an exercise: Checkpoint 2's `Dataset` reads a `.jsonl` file one line at a time, and that's where it's built.

**Next:** Checkpoint 2, a small data library (`ml.m2.checkpoint`), which closes Module 2.

## 2026-11-10: Writing tests

**`ml.py.writing-tests` is ready.** Every Check the learner has passed on this platform was a test someone wrote; now they write them. The worked example is `is_leap` with three tests, one per rule, and a six-line runner that finds every `test_` function and calls it, which is what pytest does and what every program in this topic ends with. Then a Parsons test whose decoy asserts with a single `=`, three recall questions (forty passing tests prove forty cases; an assert message read out of an `AssertionError`; the even-count list is the median's edge case), expected values to fill in for `clamp` and two tests for `median` to write, one that catches a median that forgets to sort and one that catches a median that only handles odd counts. The proofs: `word_count` with at least three tests to build, two tests that don't test to debug (a wrong expected value, and a test named `check_…` that is never collected), and an explanation built on two teammates, one who thinks forty green tests mean no bugs and one who won't test the empty list. The review pool has a `word_count` test that is wrong about `split()`, which names are collected, and tests at `clamp`'s boundaries.

**How the tests are graded.** A test the learner writes can't be checked by comparing output: `assert True` prints `2 passed` too. So the hidden tests import the learner's program, swap the function under test for a planted bug, and run the learner's tests again; a test suite that doesn't fail on the bug doesn't pass the exercise. Each exercise says so in its prompt, and the known-wrong solutions (tests that only use sorted odd-length lists; tests that only check the middle of a range) are exactly the suites that look fine and catch nothing.

**Decisions for you to review:**

1. _Fixtures are explained, not exercised._ pytest doesn't run inside the browser's Python, so the programs use a plain runner loop and a helper function for shared set-up; the recap and the explain rubric cover what `@pytest.fixture` is and when it's the right tool. The spec's table says so now.
2. _The learner's tests are graded against planted bugs._ The alternative, counting `assert`s, rewards the wrong thing. The planted bugs are the ones the prompt warns about, so a learner who reads the prompt knows what their tests must catch.
3. _A failing test can mean the test is wrong._ The predict question and the debug exercise both have that case, because a learner who believes a red test always blames the code will "fix" working code.

**Next:** JSON and nested data (`ml.py.json-and-nested-data`).

## 2026-11-10: Functions as values

**`ml.py.functions-as-values` is ready.** A function is a value; that one idea is behind `key=`, behind every `@decorator`, and behind plugging a loss function into a library by name. The worked example writes `apply(func, text)`, sorts with `key=len` and `key=abs`, and maps `len` over words. Then a Parsons sort by length whose decoy writes `key=len()`, three recall questions (`sorted(numbers, key=abs)` returns the originals in size order; pairs sorted and `min`'d with a lambda; which of four functions deserves a `def`), ranking scores to fill in (a lambda over a dict, `reverse=True`, `max` with the same key) and `compose(f, g)` to write, which returns a new function. The proofs: a counting decorator to build, with `*args` and a `count` kept on the wrapper, whose hidden tests decorate a two-argument function and check that two decorated functions keep separate counts (known-wrong: a shared global count, a wrapper that forgets to return the result); two wrong keys to debug; and an explanation of `len` against `len()`, when a lambda should become a `def`, and what `@timed` does to the function below it. The review pool has `filter` and `map` with lambdas, what `@timed` means, the order a decorator's prints come out in, and a sort by last letter.

**Decisions for you to review:**

1. _The build counts calls instead of timing them._ The spec said "a decorator that times a call", but a timing decorator's output changes every run, so no test can pin it; a counting decorator has the same shape (a wrapper, `*args`, state kept on the wrapper) and a checkable answer. The lesson and the explain prompt still use `@timed`, and the spec's table now says "counts or times calls".
2. _Decorators are taught as `f = timed(f)`,_ with the sugar second: a learner who can read the assignment can read any decorator; one who only knows the `@` can't.
3. _`functools.wraps` is left for later:_ the build's tests never check the wrapper's name, and the recap doesn't mention it, because one new idea per topic is the rule.

**Next:** Writing tests (`ml.py.writing-tests`).

## 2026-11-10: Iterators and generators

**`ml.py.iterators-and-generators` is ready.** Every `for` loop asks "give me the next one"; lists answer from memory and generators compute the answer on demand, which is how a file bigger than memory gets read and how a data loader feeds a model one batch at a time. The worked example does `iter` and `next` by hand, writes a `countdown` generator, sums a generator expression and shows it empty afterwards. Then a Parsons generator whose decoy says `return`, three recall questions (a generator expression listed twice gives `[]` the second time; a generator with prints inside shows `made` before `start`; `yield` pauses and `return` ends), clean lines to fill in and a running total to write. The proofs: sliding windows to build, whose hidden tests call `next()` on the result so a returned list fails (known-wrong: an off-by-one range, a list instead of a generator); two mistakes to debug (`return` inside the generator, and a generator consumed by `list()` before `sum` and `max` get to it); and an explanation built around a teammate's log file that ran out of memory, with the single-use trap as the third question. The review pool has four: a generator expression summed twice, what `for` calls, square against round brackets, and the first squares.

**Decisions for you to review:**

1. _Laziness is shown, not asserted:_ the prints inside the generator in the predict question are the evidence, and the explain prompt's memory story is the reason.
2. _The hidden tests call `next()` on the learner's result._ A generator that works but is really a list would otherwise pass an exercise about generators.

**Next:** Functions as values (`ml.py.functions-as-values`).

## 2026-11-10: Dataclasses and type hints

**`ml.py.dataclasses-and-typing` is ready.** Most classes are records, and Python writes those from a list of fields; the same field list is documentation, and type hints are that documentation everywhere else. The worked example declares a `Book` with a default, makes two, prints them, compares two equal ones, and ends with a hinted function over a list of them. Then a Parsons `Point` whose decoy is `x = float` (an assignment, not a field), three recall questions (`double("ab")` returns `"abab"` because hints aren't checked; dataclass equality against a plain class's identity; what `values: list[float]) -> float` promises), hints to fill in on `area`, which the checks read off the function's `__annotations__`, and a `Student` record to write with an `average()` method. The proofs: order lines to build (a dataclass with a `total()` method and a hinted `order_total`; the hidden tests read the fields, compare records and check the return hint), a `Ticket` record with a missing decorator and a string default to debug, and an explanation of what `@dataclass` generates, what hints do and don't do at run time, and when a dict or a hand-written class is still the right choice.

**Decisions for you to review:**

1. _Hints are tested as hints:_ the checks read `__annotations__`, so an unhinted but working function doesn't pass an exercise about hints. It's the only honest way to check them without running a type checker in the browser.
2. _No `field(default_factory=list)` exercise yet._ The recap names it; a mutable-default bug is a good debug for a later topic once the learner has met the aliasing it depends on in intermediate form.

**Next:** Iterators and generators (`ml.py.iterators-and-generators`).

## 2026-11-10: Classes and objects

**`ml.py.classes` is ready.** A class puts data and behaviour together, and every library the learner will meet hands them objects made this way, so reading one has to be second nature before writing one is. The worked example is a bank account: `__init__` storing values on `self`, a `deposit` method, a `__repr__` that looks like the call that would recreate the object, and two instances that don't share a balance. Then a Parsons counter whose decoy is `count = count + 1` without `self.`, three recall questions (what `self` is in `ada.deposit(50)`; two jars with separate coins; `Dog` against `rex`), a rectangle's methods to fill in and a `Temperature` class to write with a `fahrenheit()` method and a `__repr__`. The proofs: an `Inventory` class to build, whose hidden tests make two inventories and check they don't share counts (the known-wrong solution with a class-level `counts = {}` does share them, which is the classic mistake); a `Player` class with two forgotten `self`s to debug, one in a method's parameters and one in `__init__`, where the second bug only shows once the first is fixed; and an explanation of class against instance, what `self` is and why callers never pass it, and what `balance = balance` would do. The recap ends with the ML shape: `model = LinearRegression()`, `model.fit(x, y)`, `model.coef_`.

**Decisions for you to review:**

1. _The shared-state mistake is a known-wrong solution,_ not a lesson paragraph: a class attribute where an instance attribute was meant is the bug every beginner writes once, and the hidden test that makes two inventories is how they'll meet it.
2. _`__repr__` is taught in the first class,_ not later: an object that prints as `<__main__.Account object at 0x...>` teaches nothing while debugging.

**Next:** Dataclasses and type hints (`ml.py.dataclasses-and-typing`).

## 2026-11-10: Module 2 begins: comprehensions

**`ml.py.comprehensions` is ready,** the first topic of intermediate Python. A comprehension is the loop the learner has written a hundred times, said as a description of the result, and most Python they'll read from now on uses it. The worked example builds the squares twice, by loop and by comprehension, then adds a condition, a dict comprehension and a set comprehension (printed through `sorted()`, because a set has no order). Then a Parsons problem whose decoy puts the `if` before the `for`, three recall questions (reading `[len(w) for w in ...]`; a dict comprehension over `.items()`; which of four jobs wants a plain loop: the one that prints), the long words to fill in and pass-or-fail to write (a conditional expression at the front of a dict comprehension). The proofs: three one-line summary functions to build (`evens`, `lengths`, `initials`; known-wrong: a list where a set was needed, odds instead of evens), two mix-ups to debug (an odd test labelled even; a dict with key and value swapped), and an explanation that asks what a loop can do that a comprehension can't, whether a real loop should be rewritten (no: it uses a computed value twice), and why nesting goes wrong. The review pool has four, one per skill, including the flattening form with its `for` clauses in loop order.

**Decisions for you to review:**

1. _The judgement skill is a skill,_ with its own questions: knowing when not to use a comprehension is what separates readable code from clever code, and ML code bases are full of the clever kind.
2. _The main resource is the official tutorial,_ short and exact; the Python for Everybody chapter is listed as background only, because it uses syntax the learner hasn't met.

**Next:** Classes and objects (`ml.py.classes`).

## 2026-11-10: Checkpoint 1 fits a line, and the math refresher is complete

**`ml.m1.checkpoint` is ready,** and with it Module 1 of the Machine Learning Foundations track: the seven math topics and a checkpoint that is, in twenty lines, linear regression by gradient descent. The build: `predict(m, b, x)`, `error(m, b, xs, ys)` (the mean of the squared misses) and `fit(xs, ys, rate, steps)`, which starts both knobs at zero and steps them against the slopes of the error until the line through five points comes out as `slope 2.0`, `intercept 1.0`. Every test names the module skills it checks (ADR-0012), so a failed test points at Calculus's descent, Functions's lines, or Probability's centre. The known-wrong solutions step uphill, forget to average the slopes (which makes the walk unstable), or type the answer in; the hidden tests try a line that slopes down. The debug is a statistics report with three bugs, one per statistic (a mean that divides by n − 1, a median of unsorted values, a spread without its square root), on an unsorted list so the median bug shows. The explanation asks why moving two knobs against their own slopes lowers the error, why the steps shrink by themselves, and what "the best line" means.

**The way through** for a learner who's stuck: a solved sibling that fits a single constant to the same numbers and finds, without being told, the mean (and an error equal to the variance); four fill-in steps that each complete one part of the build with the rest already written (the error, the two slopes, one update, the loop); and two fresh versions on other stories, a cooling cup whose line slopes down and a growing child.

**Numbers that had to be right.** The rate of 0.05 and 2,000 steps were chosen from the error surface's shape: the slow direction shrinks by a factor of 0.983 a step, so 2,000 steps leave nothing visible at two decimals, while the fast direction stays stable; a fit takes about two milliseconds. The steps' expected values (slopes of −50.0 and −14.0 at zero; one update to 2.5 and 0.7) were computed before they were written into tests.

**Decisions for you to review:**

1. _The checkpoint is linear regression,_ unnamed. The learner meets the thing before the vocabulary; Module 3 can call it by its name and show NumPy doing it in one line.
2. _The slope formulas are given in the prompt,_ not derived. Deriving them needs the chain rule, which is Module 4's; checking them against a numeric slope is within reach and the steps invite it.
3. _Unsorted data in the debug,_ so that the "median without sorting" bug has a visible symptom; on sorted data it hides.

**Module 2, intermediate Python, is next.**

## 2026-11-09: Calculus, the seventh rung: the slope, and walking downhill

**`ml.math.calculus` is ready,** and with it all seven topics of the math refresher. The topic builds the derivative as something a program can print, `(f(x + h) - f(x)) / h` with a small `h`, and then uses it for the one thing machine learning uses it for: walking downhill. The worked example estimates the slope of `x ** 2` at 3 with `h = 0.1` (6.1) and `h = 0.001` (6.001) and lets the learner see the estimate settle on 6. Then a Parsons numeric derivative (the decoy multiplies by `h`), three recall questions (a negative derivative means going down; the power rule checked against the numeric slope at 5; the derivative of `x ** 3`), one step downhill to fill in (`x - rate * slope`, from both sides of the valley) and a walk downhill to write with a `while abs(slope) > 0.01` loop that counts its steps (29 from 0, 33 from 10). The proofs: `loss`, `slope_at` and `minimize` to build (known-wrong: a step uphill, `h = 1`), a 30-step walk with two bugs (the wrong sign, which sends it to minus seven hundred, and `h = 1`, which settles it at 2.5 instead of 3), and an explanation of why subtracting the slope finds the bottom from either side, why the steps shrink on their own, and what too large a rate does. The recap names the learning rate. OpenStax Calculus Volume 1 and 3Blue1Brown's _Essence of calculus_ (linked) are the resources.

**Decisions for you to review:**

1. _Numeric derivatives first, rules second._ A learner who can print a slope can check any rule they're told, and the power rule is introduced as something to verify, not memorize.
2. _No functions-as-arguments yet._ `minimize` works on a fixed `loss` defined in the program, because passing a function to a function is Module 2's material; the checkpoint keeps to the same constraint.

**Next:** Checkpoint 1, fit a line, which closes Module 1.

## 2026-11-09: Vectors and matrices, the sixth rung

**`ml.math.vectors-and-matrices` is ready.** Everything a model does is adding, scaling and multiplying lists of numbers, and the topic does each with plain Python lists and loops so that NumPy, later, is a convenience rather than a mystery. The worked example adds two vectors entry by entry (and says why Python's own `+` won't do), scales one, takes a dot product and measures a length. Then a Parsons dot product (the decoy adds instead of multiplying), three recall questions (why a 2×3 times a 3×4 is a 2×4; a vector plus three times another; the dot product of two perpendicular arrows is 0), a matrix times a vector to fill in and a `length(v)` function to write for any number of entries. The proofs: `multiply(a, b)` with three loops, whose hidden tests try a 1×3 by 3×1, a 2×3 by 3×2 and the identity (known-wrong: entry-by-entry products, rows paired with rows); the centre of some points with two bugs (the outer loop runs over the wrong length, the divisor is the wrong count); and an explanation of why the inner shapes must match, what shape comes out, and why a network layer is a matrix times a vector. The recap ends on the error the learner will meet most in ML code: shape mismatch, for exactly the reason just learned. OpenStax Precalculus 2e and 3Blue1Brown's _Essence of linear algebra_ (linked) are the resources.

**Decisions for you to review:**

1. _Lists and loops, not NumPy,_ for this one topic: the loops are the definitions, and the learner should have written them once before a library hides them (Module 3 brings NumPy).
2. _The review pool has four items_ so that every one of the four skills has two questions that can come back; the content rule allows it.

**Next:** Calculus (`ml.math.calculus`), the last rung, which ends with gradient descent.

## 2026-11-09: Probability and statistics, the fifth rung

**`ml.math.probability-and-statistics` is ready.** Statistics as what you do to a list, probability as counting what could happen, and the base-rate table as the one piece of reasoning everyone gets wrong until they've drawn it once. The worked example finds the mean and median of `[2, 4, 4, 10]` with `sum`, `len` and `sorted`, and the 10 moves one and not the other. Then a Parsons problem that counts the 36 outcomes of two dice with nested loops (the decoy divides by 12), three recall questions (which of mean 67.4 and median 35 describes five salaries; heads and a six multiply, not a six is `1 - p`; of 1,000 people, how many healthy ones test positive), the standard deviation to fill in (square, average, root) and the 1,000-people table to write. The proofs: `mean`, `median` and `spread` to build, with "median without sorting" and "divides by n - 1" as known-wrong solutions; dice odds with two bugs (a range that stops at 5, a chance never multiplied by 100); and an explanation of why a friend's positive test doesn't mean 90%: 9 sick positives against 99 healthy ones. The review pool has four, one each for the four skills. The recap ties each idea to its ML use: mean squared error, scaling data, and why a 99%-accurate classifier can be useless for a rare class. OpenStax Introductory Statistics 2e is the main resource.

**Decisions for you to review:**

1. _Population standard deviation (divide by n), not sample (n - 1)._ It's the definition the lesson teaches and the one NumPy uses by default; the sample version is named as a wrong answer and comes properly in Module 5.
2. _The base-rate table is written as code, not read as a story,_ so the learner computes 9 and 99 themselves before being asked to explain them.

**Next:** Vectors and matrices (`ml.math.vectors-and-matrices`).

## 2026-11-09: Exponents and logarithms, the fourth rung

**`ml.math.exponents-and-logs` is ready.** A power is repeated multiplication and a logarithm is "how many times?" asked backwards; the topic is built to make the product rule land, because that one rule is why machine learning adds log-probabilities instead of multiplying probabilities. The worked example takes a power, a negative exponent (one over), a root (an exponent of a half) and two logs with `math.log2` and `math.log10`. Then a Parsons loop that doubles a colony until it passes 1000 (the decoy adds 2 a day, growth by the same amount instead of the same factor), three recall questions (what `log2(32)` asks; `log10(1000) + log10(100)` against `log10(1000 * 100)`; `10 ** -2` is small, not negative), compound growth to fill in (`(1 + rate / 100) ** years`) and a half-life table to write. The proofs: `years_to_double(rate)` to build by multiplying until the amount passes double (known-wrong: simple interest), a decibel calculation with two bugs (`math.log` where `math.log10` was meant, the ratio upside down; the prompt says which symptom points at which), and an explanation that corrects a friend's "log of a product is the product of the logs" and ends with why the trick matters for ML. The recap names log-likelihood and cross-entropy as this trick with names. OpenStax Intermediate Algebra 2e chapter 10 is the main resource.

**Decisions for you to review:**

1. _The ML reason is in the topic, not saved for later:_ every learner who meets `log_softmax` or cross-entropy should already know why there's a log in it.
2. _Years-to-double is built with a loop, not a log,_ though the recap shows both: at this point in the track a loop is what the learner can see working.

**Next:** Probability and statistics (`ml.math.probability-and-statistics`), which needs `py.list-algorithms`.

## 2026-11-09: Functions, the third rung, and a flaky lab check made solid

**`ml.math.functions` is ready.** The point of the topic is that the math word and the Python word mean the same thing: a rule from input to output, and `f(x) = 2x + 1` is `def f(x): return 2 * x + 1`. The worked example evaluates it and prints a table of values with a loop (a graph is a table, drawn). Then a Parsons table of squares, three recall questions (what 2.5 and 4 mean in `2.5 * km + 4`; `square(plus_one(2))` against `plus_one(square(2))`; the slope through two points), the line through two points to fill in (rise over run, then the intercept) and a Celsius table to write, whose tests call the function directly as well as reading the table. The proofs: a delivery-cost function to build (known-wrong: no pick-up charge, slope and intercept swapped), a half-then-ten program with two bugs (`//` where `/` was meant, a loop that stops early), and an explanation of `f(3)`, what the two notations share, and why `f(g(2))` and `g(f(2))` differ. The recap ends with the sentence the whole module is heading for: a model is a function with knobs, and training means turning them until the table of outputs matches the data. It needs `py.return-values`, so the owner reaches it after Python's Module 4.

**A flaky lab check, made solid.** The rerun of #86's Labs job got through 39 of 40 labs; the one it called broken was the CPU quota walkthrough, whose "throttled at least once" check (`nr_throttled >= 1`) passed its no-quota wrong fix: on that runner the service showed one throttled period with no quota set. The check now measures throttled **time**, at least half a second, which a 20% quota over three seconds gives about 2.4 of and a stray period can't. Proven locally, pushed to `feat/cpu-labs`, and cherry-picked onto every branch above it, because the stack's merge keeps a child's side of a file where the two differ and would have dropped the fix. Meanwhile the lab-checker warm-up (#102) landed on `main`: the Labs job took ten minutes instead of most of an hour.

**Decisions for you to review:**

1. _Throttled time, not a count._ A count of one is noise on a busy machine; half a second of throttling is a quota.
2. _The write exercise's tests call the function and read the table,_ so a learner who prints the right table with the wrong function, or the right function with no table, hears exactly which.

**Next:** Exponents and logarithms (`ml.math.exponents-and-logs`).

## 2026-11-09: Algebra, the second rung of the math refresher

**`ml.math.algebra` is ready.** The idea of the topic is that algebra is arithmetic with a blank in it, and that Python is where to do it because it can check the answer. The worked example solves `3x - 7 = 11` by undoing in reverse order (add 7, then divide by 3, which in Python is `(11 + 7) / 3`, parentheses and all) and ends with the line that substitutes the answer back; that check is the habit the whole topic drills. Then a Parsons problem with the "divide first" line as the decoy, three recall questions (which step to undo first; a speed formula rearranged for time and multiplied back; `2 ** 3 * 2 ** 4` is `2 ** 7`), Fahrenheit to Celsius to fill in (undo the `+ 32` first) and a savings goal to solve. The proofs: simple interest rearranged for the principal, with "forgot the percent" and "divided in the wrong order" as known-wrong solutions; a temperature conversion with two bugs (parentheses missing again, and kelvin off by 0.15); and an explanation of why a friend's `17 - 3 / 5` doesn't solve `5x - 3 = 17`. The review pool has a power-rules prediction, a rearrangement question and a two-step equation to solve in code. OpenStax Elementary Algebra 2e (CC BY 4.0) is the main resource.

**Decisions for you to review:**

1. _Every solving exercise prints a check line._ Substituting back is cheap, catches every undoing mistake, and is the habit that later makes the learner trust a model's loss going down rather than their own confidence.
2. _Exponent rules are in this topic,_ as the spec says, but only the multiplying rules; logarithms and roots come in the fourth topic, where they're the point.

**Next:** Functions (`ml.math.functions`), which needs `py.return-values`.

## 2026-11-09: The math refresher begins: fractions, decimals and percentages

**The first ML topic is ready** (`ml.math.arithmetic`, "Fractions, decimals and percentages"): the arithmetic the data work leans on, done in Python so a wrong idea shows up as a wrong number. The ladder: a recipe scaled with fractions (the worked example, which also shows why `1.6666666666666665` is right and `1.67` is what a person wants), a Parsons problem for 25% off, three recall questions (order of operations, fractions to decimals, percentage change), a tip-and-split fill-in and a fruit-punch ratio to write. The proofs: a sale receipt to build where the discount comes first and the tax applies to what's left (the two likely wrong orders are known-wrong solutions), an average-score report to debug with two bugs (a missing pair of parentheses and a percentage never multiplied by 100), and an explanation of why `price * (1 - 25 / 100)` and `price * 1 - 25 / 100` differ. A review pool of three, every skill with at least three questions that can come back. The main resource is OpenStax Prealgebra 2e (CC BY 4.0), linked by book with the chapters named; the recap carries the teaching.

**Two things it needed.** Its prerequisite is `py.strings-and-input` (the Python topic that teaches the f-strings it uses), in another track, so Today's _Next up_ now says what a locked track is waiting for ("Next: Fractions, decimals and percentages, once you've learned Strings and input (Python Foundations)") instead of claiming everything is learned, with a test, and the map's cross-track reading of progress (the previous entry) has its tests now: the topic is Locked on the ML map until `py.strings-and-input` is learned, then Available.

**Also today, outside the stack:** the Labs job on #86's merge commit failed with twelve `docker build` timeouts, four cold builds of the same heavy systemd layer at once on a busy runner. `labcheck test --all --jobs N` now builds the first lab of each topic on its own before the parallel run, so the layer a topic's labs share is built once, and a build may take 30 minutes instead of 15 (#102, against `main`, so the rest of the stack picks it up as `main` is merged into each). The failed job was re-run meanwhile.

**Decisions for you to review:**

1. _The title is "Fractions, decimals and percentages", not "Arithmetic",_ so it can't be confused with Python Foundations' Arithmetic on Today or the map; the spec's table says the same.
2. _The worked example shows the ugly float on purpose_ (`1.6666666666666665`) before rounding it, because every learner meets one within a week and should know it isn't their bug.
3. _The explain prompt is about one line with and without parentheses,_ which is the whole of the order of operations in a form the learner will type a hundred times.

**Next:** Algebra (`ml.math.algebra`), the second rung.

## 2026-11-09: The Machine Learning Foundations track takes shape

Phase 2's content items, the math refresher and intermediate Python, needed a home. They're the first two modules of a third track, **Machine Learning Foundations** ([spec](specs/ml-foundations.md)): the track the vision was written for, from the math and the Python that ML is made of to neural networks from scratch and the systems that serve them. Module 1 is the placement test's seven math levels as topics, each about 45 minutes and each proven in Python (a wrong idea shows up as a wrong number); Module 2 is the intermediate Python the rest of the track is written in. Later modules are prose in the spec until Phase 3 plans them in detail.

**What changed today:** the track file and sixteen `planned` outlines (seven math topics, seven Python topics, two checkpoints), hand-written from the spec rather than generated, since there are few and they become real content soon; a diagnostic level can name its topic (`topic:`), so the math ladder's result links each topic as it's written and the free refresher until then; and the map now reads the progress of prerequisites from other tracks, because `ml.math.arithmetic` builds on `py.strings-and-input` and would otherwise have stayed locked on the ML map forever. The validator accepts cross-track prerequisites as it always did.

**Decisions for you to review:**

1. _A third track, not more modules of Python Foundations._ Python Foundations ends where its summary says it does; the ML path is its own thing, with its own map and its own hours on Today.
2. _Cross-track prerequisites, by name._ A learner can start the math refresher early (Fractions, decimals and percentages needs only `py.strings-and-input`) and the later topics unlock as their Python does. Phase 3's modules will do the same.
3. _Hand-written outlines for this track._ Sixteen files, soon real; generalizing the cloud track's generator can wait until Phase 3's modules are planned in detail.
4. _The math topics come first,_ one pull request each, because the placement test points at them today; intermediate Python follows.

## 2026-11-09: Step through, the last engineering item of Phase 2

**What it does ([ADR-0022](decisions/0022-step-through.md)).** Beside Run, a **Step through** button runs the program one step at a time: the code with the current line marked, a table of variables for each running call (innermost first), the output so far, and First/Back/Next/Last with a slider. A sentence above says what's happening: "Line 7 is about to run, inside square()", "square() returns 9", "Error at line 2: ZeroDivisionError: division by zero". It reuses the last Run's typed input and random seed, so it plays back what the learner just saw. Under a predict-the-output question, **Step through it** appears once the prediction is checked, never before: predicting first is the point. The placement test's quiet questions don't offer it.

**How.** The recorder is `harness/tracer.py`, twelve dozen lines on Python's own `sys.settrace`, running the program exactly as the Run button does (same input, seed and error trimming), recording only the learner's frames. 300 steps at most, then the program runs on unrecorded; values are cut at 60 characters; functions and classes are named rather than repr'd. It's a third kind of harness scenario (an empty `trace.txt` marks the folder), so CPython and Pyodide must agree step for step: two scenarios, a loop with a function call and an error inside a call, pass in both. The worker protocol, runner, test fakes and event payload each gained a `trace` branch; a Step through is a `code_run` event marked `stepped`. The player is one component with its own tests; the runner and the predict item have tests for the button.

**Decisions for you to review:**

1. _Our own recorder, not Python Tutor in a frame._ It runs the learner's exact code with their input and seed, it's testable, and the steps are ours to build on (a "predict the next value" question later).
2. _300 steps, 60 characters._ Enough to see the shape of any short program; Run still shows everything. The caps are two constants in `tracer.py`.
3. _Step through is offered only after a prediction._ Watching first would turn retrieval practice into a video.
4. _No new event type._ A Step through is a Run that was watched, so it's a `code_run` with `stepped: true`.

**Phase 2's engineering items are now all built:** Parsons problems, the living map, the practice-hours tracker, Today across tracks, backups, the placement test and Step through. What's left is content: intermediate Python, and the math refresher the placement test points at.

## 2026-11-09: The placement test, the third Phase 2 item

**What it does ([ADR-0021](decisions/0021-placement-test.md)).** At `/placement`, a learner picks a track or the math ladder. For a track, the test takes the open topics they haven't learned, in order, and probes the middle one with up to three of its own review questions (multiple choice, predict the output, Parsons, predict the shell: whatever the pool has, with at least one that isn't multiple choice). Two right passes the topic and everything before it; two wrong fails it and everything after; the next probe is the middle of what's left. Thirty topics take at most five probes, so ten to fifteen questions. The questions say only "Answer recorded": the test measures, it doesn't teach, and it keeps the review questions unspoiled. The result names where the knowledge seems to run out and lists the topics before it to prove, in order, through each topic's own "Prove it now". It marks nothing learned (ADR-0002 is untouched).

**The math diagnostic** is a new, small kind of content, `content/diagnostics/math.yaml`: seven levels from arithmetic to the first ideas of calculus, three original multiple-choice questions each with distractors made from the common mistakes, and a free refresher to point at per level (Khan Academy, linked, with the license recorded). The test walks the ladder the same way; the result says how far up is solid and where to refresh. The validator checks diagnostics, and the tool tests cover a good one and three broken ones.

**Under the hood.** Answers given during a placement are `answer` events with the context `placement` and the run's id; a finished run is one `placement` event with what it found. A migration (`20261109220000_placement_events.sql`) widens the event table's `type` and `context` checks, with a database test. Progress derivation and the follow-ups skip placement answers, so an unopened topic can't turn "in progress" and a placement miss can't open a follow-up; practice time counts them. The walk is a pure module with its own tests (`web/src/placement/placement.ts`); the page is tested end to end with fake topic content (every probe passes, every probe fails, the frontier in the middle, the math ladder with a known frontier, stopping, the card's last result) and the Today page shows the latest result per subject in a line. 737 web tests, 47 tool tests, 4 database test files, all green.

**Waiting on you:** the migration has to reach the live project before a placement taken there can be saved: after this merges, `npx supabase db push --remote --dry-run`, then without `--dry-run`. Until then the outbox keeps placement events on the device and reports them as refused.

**Decisions for you to review:**

1. _Halving along the track's order_ rather than walking the prerequisite graph properly. Our tracks are near-chains, so "what you know is a prefix" is a good approximation and far simpler to explain; the ADR says where to revisit if a track branches a lot.
2. _Ties and topics with nothing to ask get the benefit of the doubt._ A generous estimate costs a failed proof (and a lesson); a stingy one costs a lesson on something familiar. The first is cheaper and self-correcting.
3. _Multiple choice for the math diagnostic,_ with distractors from the common mistakes, rather than a new numeric-answer item type. Numeric answers can come with the math content itself.
4. _No feedback during the test,_ not even at the end per question: only the counts and the plan. The explanations in the math items are written for a future refresher.
5. _Placement time counts as practice time._ It's effortful retrieval; a ten-minute test is noise against 10,000 hours either way.

**Next in Phase 2:** the step-through code visualizer, then content (intermediate Python, the math refresher).

## 2026-11-09: Nightly backups, the second Phase 2 item

The learner's history has lived in one Supabase project with no backup but the manual export ([ADR-0010](decisions/0010-environments.md) said as much, and asked for this in Phase 2). Now a scheduled workflow takes an encrypted data dump every night ([ADR-0020](decisions/0020-automated-backups.md)): the pinned Supabase CLI dumps the real project's data over its session-pooler connection (data only, `public` and `auth`, so the learner keeps their id on restore and the events stay theirs), the dump is AES-256 encrypted on the runner and the plain file shredded, and the encrypted file is committed to a private `education-platform-backups` repository, one a night, for good. The repository being public since this morning is what makes the workflow free, and what makes "nothing readable ever leaves the runner" the first rule.

**The restore is rehearsed on every pull request,** not assumed. CI's database job runs `tools/backup_restore_check.sh`: a learner with one event goes into the throwaway local database, the data is dumped with the same command, the encryption is round-tripped with a throwaway passphrase, the database is reset to empty tables, the dump is restored with `psql`, and the learner, their profile and the event must be back. It ran clean here first, against the local stack. The same script runs on your PC with the local Supabase up.

**Also today:** the CI diet (#87) merged into `main`, so pull requests no longer re-run CI after a merge, and the labs run only when content or tooling changes. The Module 1 stack merges next, bottom up, as each run passes.

**Waiting on you:** four one-time steps, all credentials, written out in [docs/setup.md](setup.md) under "Back up your learning data": the private repository, the passphrase (into your password manager the day you make it; it's the whole secret), a fine-grained token scoped to that one repository, and the three repository secrets. Until then the nightly run reports which secrets are missing and stops green, so you won't see a red X while you set it up.

**Decisions for you to review:**

1. _Data only, not schema._ The migrations are the schema's source of truth; a restore into a new project is "migrations, then the dump", which is what the rehearsal does.
2. _`auth` is in the dump._ It carries hashed credentials and refresh tokens, but leaving it out would orphan the events on restore; it's encrypted everywhere it's kept and the backups repository is private.
3. _A private Git repository as the only archive,_ not the run's artifacts as well: a public repository's artifacts can be downloaded by anyone with a GitHub account, and even encrypted that's a footprint for no gain. Clone the backups repository onto another drive now and then for the copy that isn't on GitHub.
4. _The workflow stops green without the secrets._ A red schedule nobody can fix yet teaches people to ignore red; a notice naming the missing secrets doesn't.
5. _The rehearsal resets the local database._ That's what a new project looks like, and the restore puts back everything that was there plus the test learner. Local data is throwaway by ADR-0010, but you should know it happens.

**Next in Phase 2:** the placement test with its math diagnostic.

## 2026-11-09: The repository goes public, the stack starts merging, and Today shows both tracks

**Your four decisions, carried out.** The repository is public (a scan of the tree and the whole history first: no `.env` ever committed, no key material; the one "service role" hit is the Edge Function reading an environment variable's name). GitHub Actions minutes came back with it; the failed runs for the CI diet (#87), the bottom of the stack (#85) and its top (#95) were re-run, the CI diet's CI job is already green, and the merges go in order as each run passes, each next branch rebased onto the new `main` and force-pushed to its own pull-request branch with `--force-with-lease` (never `main`), because a squash-merged parent can't be merged under its child without rebasing. Phase 2 starts with the two things you named.

**Today across tracks ([ADR-0019](decisions/0019-today-across-tracks.md)).** _Next up_ now has one entry per track: the track's name, how many of its open topics are learned, and its topic in progress or next Available, so a learner on two tracks sees where they stand on both. _Practice hours_ keeps one sentence for the total and then gives each track its own time and its own milestone ladder, since the 10,000 hours are about mastering one domain; time on a topic outside every track shows as "Other" only when there is some. Reviews and mistakes to revisit already drew on every bundled track, so they're unchanged. The grouping is a pure function (`practiceTimeByTrack`) that takes a "track of this topic" function, so it stays free of content imports.

**Decisions for you to review:**

1. _Each track has its own milestone ladder,_ rather than one ladder with a per-track footnote. "100 hours" for 90 in Python and 10 in cloud would say the wrong thing; the total stays visible as a sentence.
2. _The track entries don't disappear when a track is finished or empty;_ they say so, so the learner still sees the track is there.
3. _A learned count counts every learned state_ (learned, mastered, fading, relearning, passed), the same reading as ADR-0002: a failed review doesn't un-learn a topic.

**Next in Phase 2,** in the order I'd take them: automated data backups (small, and the event log is the platform's most valuable data); then the placement test with its math diagnostic; then the step-through code visualizer; content (intermediate Python, the math refresher) last, since it's the kind of work the owner can steer topic by topic.

## 2026-11-09: Where we stopped: Module 1 is complete, and the stack waits for CI

**Done this run.** Module 1 of the Cloud Solutions Architect track is complete: fourteen topics and the checkpoint, each with a lesson, recall items and labs that a container proves (seventy-nine labs, three hundred and fourteen exercises in the whole content tree, fifty-one topics ready). Everything was verified locally with the commands CI runs: the validator (no problems), the web suite (700 tests), lint, types and formatting, every topic's labs as they were written, the full seventy-lab run once the shared base settled, and the nine checkpoint labs. One small follow-up is in this same pull request: the triage debug stopped its runaway with `systemctl stop` then `mask`, and `mask` silently fails on a unit that lives as a real file under `/etc/systemd/system`; it's `systemctl disable --now` now, re-proved.

**Where we sit.** Ten pull requests are open and none has had CI, because GitHub Actions ran out of minutes on the private repository (the entry _CPU scheduling and cgroups goes ready, and GitHub runs out of minutes_ below lists the four ways back, in my order of preference). They're stacked, each on the one before, so they merge in order once CI returns: #87 (the CI diet) on its own at any time, then #85, #86, #88, #89, #90, #91, #92, #93, #94, #95. Each is squash-merged with its branch deleted, as agreed. The standing merge permission is "once CI passes", so I haven't merged anything.

**Decisions waiting for you.** Every topic's entry below ends with a _Decisions for you to review_ list; the ones that reach beyond a single topic are: the CI options (CPU entry); the network tools and dnsmasq, then cloud-init, added to the shared base image (networking and boot entries); the containers, triage and hardening topics leaning on what a container can show deterministically (the containers, triage and hardening entries); and the checkpoint's shape, a three-part build with storage proved in the debug's full-disk fault instead (checkpoint entry).

**Why I stopped here rather than starting the next module.** The roadmap leaves the next step open between Module 2 of the cloud track (Virtualization, hardware and Windows, whose topics are outlines with no lessons yet) and Phase 2 (adaptivity and better practice). Either is a multi-session effort in a new direction, and both would be built on top of a ten-deep stack nobody has reviewed or merged. That seemed the wrong moment to choose for you. Nothing is left running: no background tasks, no containers, only Docker's own two loop devices.

**Next, in the order I'd suggest:** restore CI and merge the stack in order; read the decisions above; then say which of Module 2 or Phase 2 you'd like first. If it's Module 2, the pattern is settled (lessons and recall first, then five labs a topic, a checkpoint last), and `content/README.md` now records every lab-writing lesson from this run.

## 2026-11-09: Checkpoint 1 goes ready, and Module 1 is done end to end

The module's checkpoint, and the first lab-based one, so ADR-0012's shape had to be translated from Python programs to containers. The translation that worked: the **build** is a runbook with three parts (run the service, a default-deny firewall that keeps SSH and the API, harden SSH, with the key login as the proof); the **debug** is the spec's broken server, five faults at once; the **solved sibling** is the same runbook on a different server, as a walkthrough; each of the four **steps** is the build with the _other_ parts already done in the image, so the learner completes one part with hints, and the last step is the whole build from an outline; and the two **fresh versions** are the build in other stories (a gateway, a ledger). Every build and debug check names the module skills it tests, so a miss brings the right topic's practice back to Today. Nine labs, fifty-five checks, twenty-six known-wrong fixes.

**The five faults, and the tool each teaches:** a data area filled by an old file (`df`, `du`; a tmpfs filled at boot, so nothing is left on the real disk and no loop device needs tearing down); a unit whose `ExecStart` names a binary that isn't there (`systemctl status`, `journalctl -u`, 203/EXEC); a world-writable `~/.ssh` that makes `sshd` refuse a good key (`chmod 700`); a default-deny firewall that never opened the API's port (`nft list ruleset`, add the rule, keep `policy drop`, persist); and a worker pegging a CPU (`ps`/`pidstat`, `systemctl disable --now`). A sixth check confirms the server is still hardened afterwards, because the lesson's point is that an incident fix that turns protections off isn't a fix.

**What the contract caught, three things worth remembering:**

1. _`systemctl mask` fails on a unit that lives as a real file in `/etc/systemd/system`_ ("already exists"), so a wrong fix ending in `mask` was reported broken rather than wrong. The runaway is stopped with `disable --now`, which is the accurate command anyway: `Restart=always` never revives an explicitly stopped unit. The triage debug (#92) uses `mask` the same way; it's harmless there (its `stop` does the work and the checks read the right state), noted as a follow-up to change.
2. _A broken unit with `Restart=on-failure` flaps:_ fail, restart, fail, a millisecond of "active" after each "Started", until systemd's start limit trips and it sits failed. That made the repair's `restart` get refused ("start request repeated too quickly") and once let an unrepaired wrong fix catch a lucky `active`. The broken unit now has no `Restart=` (it fails once and stays failed, which is the realistic symptom and reads cleanly in `status`), the service check reads `is-active` twice a second apart, and the hint mentions `reset-failed`.
3. _A check that looked for "enabled" in `systemctl is-enabled`'s output would have accepted "disabled",_ which contains it. Exact match now. The same lesson as the triage fill lab: a check any wrong answer can satisfy isn't a check.

**Decisions for you to review:**

1. _The build is three parts, not four._ An earlier design also mounted a data disk, but that would have put loop devices and teardown into nine images; storage is proved in the debug's full-disk fault instead (a tmpfs, no teardown), and the build's three parts map cleanly onto three steps plus the outline.
2. _The wrong fixes are omissions and mistakes, not scripted shortcuts._ The lesson forbids turning the firewall off or passwords on to make something work, and the checks confirm the server stays hardened; but the known-wrong scripts don't themselves perform those shortcuts (a draft that did was also what tripped a safety classifier mid-session, which settled it). An omission (a port left out, a part skipped, a fault left unfixed) fails the same checks.
3. _The checkpoint's images reuse the hardening topic's SSH setup_ (ben, `ssh-users`, a key in `~/keys`, `/run/sshd` at boot) through a `tail-common` of their own, so every checkpoint lab can prove a real login.

**Module 1 is complete:** fourteen topics and the checkpoint, seventy-nine labs in all, every one proving its contract in a container, verified locally end to end (CI is still waiting on GitHub's minutes; PRs #85 to #94 are stacked in order). **Next:** merge the stack when CI returns, then Module 2 of the cloud track, or the Phase 2 adaptivity work, whichever you'd rather see first.

## 2026-11-09: Hardening goes ready, and Module 1 is complete

The fourteenth cloud topic, and with it every topic in Module 1 is `ready`. The only piece left in the module is its checkpoint, the "broken server" with five planted faults.

Hardening is the module's capstone topic because it uses all of it: SSH (permissions), the firewall (networking), services and packages. The labs harden a real server and prove it, and the design problem was proving without locking anyone out, the same problem the lesson warns about. Each lab sets up `ben` in an `ssh-users` group with his key in `~/keys/ben`, so a real `ssh -i ~/keys/ben ben@localhost` is the test, run before and after every change.

**What a container made me design around:**

- _SSH is socket-activated_ on Ubuntu 24.04 (`ssh.socket`, not `ssh.service`), so a config change applies to each new connection with no reload, and `sshd -T`/`sshd -t` need `/run/sshd`, which I create at boot with a tmpfiles rule.
- _A same-host SSH test goes over loopback,_ so a firewall that blocks port 22 can't be felt from the same machine (the net-tools labs needed a separate network namespace to prove a firewall from outside). So the build lab verifies the firewall by reading its ruleset, and the debug lab's three faults are all in sshd, where a same-host login does feel them.
- _`ufw` doesn't behave in a container,_ so the firewall is nftables, which the networking topic already proved works. The lesson still teaches `ufw` as the friendly front-end.
- _Benchmark scanners_ (CIS, OpenSCAP, Lynis) are heavy and non-deterministic; they stay in the lesson and recall, and the labs prove the baseline with their own checks, which is the same scan-before-and-after idea.

**The five labs:** `example-harden-ssh` (the drop-in, with the key proved first and last), `fill-sshd-hardening` (the four values), `write-exposed-ports` (an audit that tells an open door from a loopback-only one), `build-harden-the-server` (the whole baseline: SSH, a default-deny firewall that keeps and persists SSH, a stray debug service closed), `debug-locked-out` (three sshd faults, fixed without the shortcut of turning passwords back on). The anti-pattern the whole track warns about, turning a protection off to make something work, is a known-wrong fix in two labs. Twenty-four checks, seventeen known-wrong fixes; all five green on the first full run.

**Decisions for you to review:**

1. _nftables, not ufw,_ for the lab firewall. ufw is the lesson's recommended tool but doesn't run cleanly in the container; nftables is what's underneath it and what the labs can prove.
2. _The baseline is proved by the labs' own checks, not a scanner._ A real CIS/OpenSCAP scan in a container is slow and its score isn't reproducible; the hand-rolled audit (`exposed-ports`) and the checks teach the same method.
3. _Benchmark scanning stays conceptual._ It's the one part of the topic the labs don't exercise directly, for the reasons above; the lesson and recall carry it.

**Module 1 is done.** Fourteen topics, each with a lesson, recall items, and five labs that a container proves. Next is the module checkpoint (`csa.m1.checkpoint`), a broken server with five faults across the module's topics, which needs the checkpoint rules from ADR-0012 (unstuck steps, a skills map per fault).

## 2026-11-09: Performance triage goes ready, and what a container will and won't show

The thirteenth ready cloud topic, and the one where the lab environment pushed back hardest. Performance signals are noisy, and a container hides some of them: a single spinner on an eight-core host is not system-wide saturation, `iostat` shows the host's disks not the container's load, and `perf` needs kernel tooling a container doesn't have. So the labs are built on the signals that _are_ reliable and deterministic inside a container, and the fragile ones stay in the lesson and the recall.

**What's deterministic in a container, and what the labs use:**

- A busy spinner is unambiguously the top process by CPU (`ps`, `pidstat`), and `ps comm` names it from its script name (`#!/bin/bash`, the trick from the processes topic).
- Per-cgroup CPU accounting is exact: a service's `cpu.stat` `usage_usec` sampled a second apart is how much CPU it used, which is what `build-busiest-service` is built on.
- `strace -c` error counts are decisive: a service in a `openat` storm shows millions of failing calls, which is how the debug lab's runaway is identified.
- PSI (`/proc/pressure/*`, per-cgroup `cpu.pressure`) works and is clean, kept in reserve for now.

`sysstat` (iostat, mpstat, pidstat, sar) and `strace` go in the triage labs' own `tail-common`, not the shared base, so the other sixty lab images don't rebuild. (A transient apt hiccup during a probe installed nothing once; at image-build time a failure would just fail the build, which is visible.)

**The five labs:** `example-sixty-seconds` (the checklist to a written verdict), `fill-triage-report` (the signals, with the CPU-percent field and the run-queue column as gaps), `write-cpu-culprit` (`top-cpu`), `build-busiest-service` (the heaviest service by cgroup CPU), `debug-syscall-storm` (find the `openat` storm with `strace`, stop it at the service because it restarts, write the finding down). Twenty checks, sixteen known-wrong fixes.

**What the contract caught, a lesson about weak checks:** the fill lab first shipped with two wrong fixes passing, because the run-queue and idle checks only asked "is it a number?", and a wrong column is also a number, and `%idle` versus `%usr` is indistinguishable once parallel labs load the host. The fix was to pick signals with a deterministic _value_, not just a type: the run queue is at least 1 while the worker spins (the blocked column is 0), and the busiest process's CPU share is near 100 (the wrong field is its name, not a number). A check that any wrong answer can satisfy isn't a check.

**Decisions for you to review:**

1. _The triage labs are CPU- and syscall-centred,_ because that's what a container shows deterministically. Disk and network saturation are taught and quizzed (iostat `await`, `sar` retransmits) but not proven in a lab; proving them would need signals the container can't reliably produce.
2. _`strace` as the debug tool,_ not `perf`. `perf` doesn't work in the lab container; `strace -c` does, and it's the right tool for a process that's busy in the kernel anyway.
3. _Per-topic packages in a tail,_ not the shared base, for tools only one topic needs. It keeps the shared layer stable and the other labs' images untouched.

**Next:** Hardening, the last Module 1 topic, a security baseline proved with a benchmark scan, and then the module's checkpoint.

## 2026-11-09: Shell scripting goes ready, the first plain labs

The twelfth ready cloud topic, and a change of lab shape. Every cloud lab so far boots systemd in a privileged container; shell scripting doesn't need that, so these are the track's first **plain labs**, the same kind the first topic (Shell essentials) used: a light Ubuntu image with ShellCheck, `CMD ["sleep", "infinity"]`, and the learner's work done through `docker exec`. They build and run much faster than the systemd labs, with no boot to wait for.

**The five labs:**

- **`example-make-it-safe`**: the five habits from the lesson as before-and-afters, `set -u` catching a typo, `pipefail` catching a broken pipe, quoting surviving a space, a trap cleaning up after a deliberate failure, and an idempotent append run twice that writes once.
- **`fill-strict-deploy`**: finish a deploy script, the shebang interpreter, the third strict-mode setting, the cleanup trap, and the quoted copy destination.
- **`write-backup-logs`**: a backup that builds in a temp dir it always cleans up, keeps a log name with a space, writes one archive of a fixed name (so a second run replaces rather than piles up), and exits 2 with a message when its source is missing.
- **`build-safe-deploy`**: a release manager, honest exit 2 with no version, strict mode, a trap, an atomic `ln -sfn` swap of `current`, and pruning to the three newest releases.
- **`debug-fragile-script`**: a script fragile three classic ways, it fails the second run (`mkdir` without `-p`), drops a filename with a space (`$(ls)` word-splitting), and stays silent when the source is missing (no guard), fixed until ShellCheck is quiet and a second run is clean.

**ShellCheck is a check in three of the five labs**, so the lesson's "run it on every script" is something the contract enforces, not just advises. The quoting bug in the debug lab is one ShellCheck flags (SC2086, SC2045), so a learner who runs it is led straight to the fix. Twenty-two checks, seventeen known-wrong fixes; all five green on the first full run.

**One web test needed updating:** the map page's "more than one track" test asserted Module 1 had "a ready topic and the rest drafts" and looked for at least three Draft badges. Module 1 is now twelve topics ready and two draft, and will be zero draft once it's finished, so the brittle draft count is gone; the test still checks that the track renders with its ready topics and three capstones.

**Decisions for you to review:**

1. _Plain labs for scripting._ No systemd, because bash is the subject; the checker already supports it (it's how Shell essentials works). It keeps these labs fast and their images small.
2. _ShellCheck in the lab, not just the lesson._ Installing it in the image and grading with it makes the tooling habit real. It's the one new package these labs need.
3. _The deploy appears in two labs_ (a fill-in and a fuller build). The repetition is deliberate: the fill-in is about the strict-mode and trap mechanics, the build adds the exit code, the atomic swap and pruning, which are the parts that make a deploy safe to run on a real server.

**Next:** Performance triage, the thirteenth topic, finding why a server is slow with the USE method and the tools that show where the time goes.

## 2026-11-09: Boot, cloud-init and instance metadata goes ready

The eleventh ready cloud topic, and the one where the lab machine stops pretending to be a server and starts pretending to be a cloud instance. cloud-init is installed in the shared base and really runs at the container's first boot, reading a NoCloud seed under `/var/lib/cloud/seed/nocloud` that stands in for what a cloud's metadata service hands over. A probe confirmed the whole chain works in the container: cloud-init configures a user, a package (from the shop's offline repository), a file and a `runcmd`; `cloud-init status`, `query` and `analyze` all work; and a small Python metadata service answers at `169.254.169.254` in both protocols.

Three scripts stand in for the cloud console, since a container can't really reboot: `lab-launch [user-data]` runs cloud-init's four stages with a new instance id (a fresh instance: everything runs), `lab-reboot` runs them with the same id (the per-instance modules skip), and `lab-imds-options --tokens required|optional` sets whether the metadata service still answers plain requests.

**The five labs:**

- **`example-first-boot`**: what cloud-init did, where the instructions were, `systemd-analyze`, and the once-per-instance rule shown directly, a reboot adds no line to `runcmd`'s output, a launch does.
- **`fill-user-data`**: finish a `#cloud-config`, the package, the file's path, a value, a `runcmd` command, then `lab-launch` it.
- **`write-imds-get`**: a metadata client that gets a session token first and sends it, proved by a check that flips the service to tokens-required and runs the client again.
- **`build-close-the-hole`**: require session tokens (the IMDSv2 defence) and update the shop's one metadata client so it keeps working, so a plain GET is refused and the legitimate client still reads its region. Framed around the configuration and the client, with the reason in prose and no request-forgery demonstration.
- **`debug-wont-come-up`**: a server that came up half-configured, three faults in the user data (a misspelled package, a config at the wrong path, a `runcmd` writing into a directory that doesn't exist), read from `/var/log/cloud-init-output.log` and fixed, then launched fresh (editing and rebooting wouldn't re-run the per-instance steps, which the topic just taught).

Twenty-three checks, sixteen known-wrong fixes.

**Three things the contract shaped:**

1. _A 46-second boot became 5._ cloud-init's final stage was stalling on `sudo`/name lookups because the hostname it sets wasn't in `/etc/hosts`; `cloud.sh` adds it at boot, as a cloud image's hosts file has it. (Worth knowing for CI: the boot labs run cloud-init at container start, so each boots in ~15-20s; the 90-second boot timeout holds, but it's the first topic where that number matters.)
2. _The console stand-ins must always exit 0._ With `set -e -o pipefail`, `lab-launch` exited non-zero when cloud-init ended in error, so a `wrong/*.sh` that launches a still-broken config was reported _broken_ rather than _wrong_. A console button doesn't fail because the instance did; the result is for `cloud-init status` to report.
3. _cloud-init disables itself in a container._ `ds-identify.cfg` with `policy: enabled` is what lets it run; without it the lab machine looks too much like the container it is.

**Decisions for you to review:**

1. _cloud-init in the shared base_ (about 6 MB of Python), used only by this topic so far. It's the natural place, since the base is where a systemd lab's common layer lives.
2. _The metadata-security lab is a hardening lab, not an attack lab._ It builds the defence (require tokens, fix the client) and explains the risk in words. I kept out a working link-preview/SSRF service even as scenery; a safety classifier flagged an earlier draft of exactly that file, which confirmed the call.
3. _A metadata service written in Python_ (`lab-imds`), rather than a few static files, so it can speak the token protocol and return fresh-looking temporary credentials. It reads its tokens-required setting per request, so the console stand-in only writes a file.

**Next:** Shell scripting, the twelfth topic, scripts that stop safely on errors and are safe to run twice.

## 2026-11-09: Networking from the host goes ready, with an office on the far side of eth1

The tenth ready cloud topic. The problem with networking labs in one container is that "from another machine" is the whole point, so the lab machine gets one: at boot, `network.sh` makes a network namespace called `office` and joins it to the machine with a veth pair, `eth1` on the server (10.0.9.1) and `eth0` in the office (10.0.9.2). `from-office COMMAND` is `sudo ip netns exec office COMMAND`: a connection that really arrives on `eth1`, so a firewall can be proved from outside, `tcpdump -i eth1` sees the packets, and a service bound to `127.0.0.1` really is unreachable. The machine also runs its own name server (dnsmasq, answering for `shop.internal` and forwarding the rest) and asks it, which took unmounting the `resolv.conf` Docker mounts into the container; the office asks it too, through a per-namespace `resolv.conf`. The shop's services are small Python programs under their own names: `shop-api` on 8080, `shop-db` on `127.0.0.1:5432`, `office-monitor` in the office at 9100 (a unit with `NetworkNamespacePath=`), and a leaking `shop-cache` for the write lab.

**The five labs:**

- **`example-whats-listening`** (worked example): `ip -br addr`, `ip route`, `sudo ss -ltnp`; from the office, `dig` (a CNAME, then the address), `nc -zv` (8080 answers, 5432 is refused), `curl -sI`, `traceroute`; then `tcpdump` on `eth1` catching a three-way handshake and, for 5432, a SYN answered by a reset.
- **`fill-net-report`** (fill-in): the address field of `ip -br addr`, the `default` route, `ss -ltn`, `dig +short`, `%{http_code}`.
- **`write-socket-report`** (write): `ss -tan` states counted with `uniq -c`, the `CLOSE-WAIT` count as the verdict (exit 1 over 20). The cache holds thirty connections the web tier closed at boot; the office, a healthy machine, is where the exit-0 path is proved.
- **`build-shop-firewall`** (build): nftables `input` policy `drop`, `iif lo accept`, `ct state established,related accept`, 22, 8080 and UDP 53 from the office, everything else dropped rather than refused, the rules in `/etc/nftables.conf` and `nftables.service` enabled. The office's DNS turned out to be a requirement the first draft forgot: the office resolves names on this server, so a firewall without UDP 53 breaks every test by name.
- **`debug-not-from-the-office`** (debug): a stale DNS record (10.0.9.5), a firewall rule for the API's old port (8000), and the API bound to `127.0.0.1`; fixed in order with `dig`, `tcpdump` (dropped, then refused) and `ss`. The firewall must stay a firewall and the fix must be in the file, which two of the five known-wrong fixes get wrong.

Twenty-seven checks, twenty-two known-wrong fixes, all five labs keeping their contract at the first run except a YAML slip (a check's command held `: ` in a plain scalar; it's a block scalar now). Two checks tell _dropped_ from _refused_ by timing `nc -z -w 2`: a reset comes back in milliseconds, a drop takes the whole timeout.

**Decisions for you to review:**

1. _The network tools and dnsmasq go in the shared base image_ (iproute2, ping, dig, tcpdump, nc, nftables, conntrack, traceroute, dnsmasq; about 15 MB). dnsmasq is switched off there and enabled only by this topic's labs, so no other lab grows a listening port.
2. _The office is a network namespace, not a second container._ ADR-0018's checker runs one container per lab; a namespace gives "another machine" with no change to the checker, and it's the mechanism containers use, so it teaches the lesson's last section by being used.
3. _The build lab requires DNS from the office._ It makes the firewall six rules instead of five, but it's how a real host firewall fails: a port nobody thought of as a service.
4. _The debug lab's firewall fault is a wrong port, not a missing rule,_ because the realistic story (the API moved) leaves a rule that looks right at a glance.

**Next:** Boot, cloud-init and instance metadata. A probe is checking whether cloud-init itself runs in the lab container from a NoCloud seed, and whether a metadata-service stand-in can answer at 169.254.169.254.

## 2026-11-09: How containers work goes ready, with no Docker in the lab

The ninth ready cloud topic, and the payoff of the previous two: the labs build a container from `unshare`, `chroot`, cgroup files and overlayfs, around a root filesystem made from busybox at image build (one binary that behaves as `sh`, `ls`, `ps` and so on by the name it's called by). A probe showed everything works in the lab's privileged container: pid, uts, mount and ipc namespaces, a cgroup made with `mkdir`, and an overlay mount, as long as the writable layer sits on a tmpfs, since the container's own root is already an overlay and overlayfs refuses an upper directory on another overlay.

**The five labs:**

- **`example-container-by-hand`** (worked example): `unshare --pid --fork --uts --mount --ipc chroot rootfs /bin/sh`, `/proc` mounted inside, `hostname box`, PID 1 is the shell; the host unchanged; a cgroup with `pids.max` 20 that a fork storm runs into, `pids.events` counting the refusals.
- **`fill-run-in-box`** (fill-in): the three words a hand-made container can't do without: `--fork`, `proc`, and the hostname.
- **`write-layers`** (write): an overlay of image layers given bottom to top (so the lower list is reversed), writable layer on a tmpfs, the top layer's file winning, copy-up leaving the layers untouched.
- **`build-box`** (build): a thirty-line runtime: an overlay root thrown away afterwards, namespaces, a cgroup with pids and memory limits joined before the `exec`, and cleanup. Five checks, including one that runs a box in the background and inspects its cgroup from outside.
- **`debug-leaky-box`** (debug): no `--uts` (the lab machine gets renamed), `--pid` without `--fork` (`can't fork: Cannot allocate memory`), and a cgroup join written after the `exec`, which therefore never runs.

**What the contract caught, five things, two of them container facts worth teaching:**

1. _PID 1 of a namespace ignores signals it has no handler for._ A check sent `TERM` to the box's `sleep` and it didn't die; only `KILL` from outside does. That's why `docker stop` sends `TERM` and then `KILL`, and why images run `tini` as PID 1; the lesson now says so.
2. _busybox's shell dies outright when a fork is refused,_ so a fork storm that counted afterwards never got to count. It announces each attempt instead, and the last line it managed is the count.
3. _A Docker build may not make device files_ (`mknod` fails), and background jobs need `/dev/null`; a oneshot unit makes the two device files at boot, when the container is privileged.
4. _`pkill -f` matched the check's own command line_ again (`sleep 30` appeared in it); the pattern is anchored, `^sleep 30$`.
5. _Files written through Python on Windows came out with CRLF line endings,_ and bash in the image read `set -euo pipefail\r`. Every scratch file is normalised to LF and the content tree checked; the assembled Dockerfiles and scripts in the repository are LF.

**Decisions for you to review:**

1. _busybox-static in the shared base,_ about a megabyte, so every systemd lab image can make a root filesystem; only this topic uses it so far.
2. _The build's cgroup check inspects a box from outside while it runs,_ which means a background box and a `KILL` at the end. It's the honest way to prove the limits apply to the right processes.
3. _The debug's third bug, a join after `exec`,_ is subtle for a beginner, but the prompt names its symptom (an empty `cgroup.procs`) and `exec` was taught in Processes and signals.

**Next:** Networking from the host, with a small web server and a port already in use to find.

## 2026-11-09: CPU scheduling and cgroups goes ready, and GitHub runs out of minutes

The eighth ready cloud topic, built on the same cgroup machinery as the memory labs: `systemd-run -p CPUQuota=20%` on a spinner gives `cpu.max` of `20000 100000`, `top` shows it at 20%, and `cpu.stat` counts a throttled period for nearly every period, which the probe had shown this morning.

**The five labs**, around `spin` (a bash loop that keeps one CPU busy, installed under whatever name a service needs so `ps` and `top` show `shop-api` or `shop-worker`):

- **`example-quota-a-spinner`** (worked example): `nproc` and `uptime`, a spinner at 100% in `top`, the same spinner under a 20% quota, `cpu.max`, `cpu.stat`, stop it.
- **`fill-cpu-report`** (fill-in): `nproc`, the three load averages from `/proc/loadavg`, the busiest process from `ps --sort=-%cpu`, and a service's `nr_throttled`.
- **`write-cpu-cap`** (write): `cpu-cap SERVICE PERCENT` writes a drop-in, reloads, restarts and prints `cpu.max`; a second run replaces the cap rather than adding a file.
- **`build-share-the-cpu`** (build): a quarter of a CPU for the batch report (and its throttling counters climbing), three times the default weight and no quota for the API. Six checks.
- **`debug-throttled-api`** (debug): one unit with `CPUQuota=5%`, `Nice=19` and `CPUWeight=1`; each a different witness (`cpu.stat`, `ps -o ni`, `cpu.weight`).

**What the contract caught, three things:** a spinner under a quota is throttled in _every_ period, so `nr_periods` and `nr_throttled` are nearly equal and a wrong fix that printed the wrong one passed; the check now compares the script's number with the true count (within a few periods), and the wrong fix prints `throttled_usec` instead. `top` truncates command names to `shop-worke+`, so a check that grepped for the full name found nothing; it asks `top -p PID`. And a YAML mistake of mine (a plain scalar holding `: `) raised an exception inside one worker thread and ended the whole parallel run; `test_quietly` now reports any exception as that lab's problem and the run continues.

**GitHub Actions ran out of minutes.** The memory topic's pull request (#85) got no CI: every job failed in three seconds with "The job was not started because recent account payments have failed or your spending limit needs to be increased". The repository is private, where the free plan includes 2,000 minutes a month, and today alone had 102 workflow runs: 53 on pull requests and 49 on `main` after merges, each run six jobs and the Labs job alone five to six minutes by the end. Nothing can merge under the standing permission until minutes are back, so from here the topics are built on branches stacked on #85, each verified locally with the same commands CI runs (lint, types, the web tests, the validator, and `labcheck test --all --jobs 4`), and the pull requests wait. A separate change cuts the usage: no run on `main` after a merge (the pull request already ran on that commit), and the Labs job only when labs or the checker change.

**Decisions for you to review:**

1. _How to get CI back._ Four ways, in my order of preference: make the repository public (public repositories get unlimited Actions minutes; nothing in it is secret, every resource is linked not copied, and the licences allow it); or wait for the monthly reset; or run a self-hosted runner on your PC (free, but your machine has to be on); or set a paid spending limit, which ADR-0005 rules out unless you decide otherwise. I can't read the account's billing page from here (`gh` lacks the `user` scope), so I don't know when the month resets.
2. _The CI diet_ (its own pull request): no `push` run on `main`, and the Labs job only on changes under `content/topics/**`, `tools/**` or the workflow. Merging a pull request will rely on the pull request's own run, which is what the process does already.
3. _Topics keep going on stacked branches_ until merging is possible: cpu on memory, and so on, one pull request each, so each diff stays readable.

**Next:** How containers work (namespaces, cgroups and overlay filesystems by hand), then networking from the host.

## 2026-11-09: Memory and the OOM killer goes ready, and the kernel does the killing

The seventh ready cloud topic. The first probe of the day had shown that a `systemd-run -p MemoryMax=64M` unit really gets OOM-killed in these containers, and that's the spine of all five labs: the kernel's own behaviour, not a description of it.

**The five labs**, around `memhog` (takes N MB, really touches them, holds them a few seconds) and `leaky` (grows 32 MB a second to a cap):

- **`example-limit-a-hog`** (worked example): `free -m`, the same lines from `/proc/meminfo`, `vmstat 1 3`, then `systemd-run --unit=hog -p MemoryMax=64M -p MemorySwapMax=0 memhog 200`: `Result=oom-kill`, `ExecMainStatus=9`, and the kernel's line in `journalctl -k`, `Memory cgroup out of memory: Killed process … (memhog) … anon-rss:… oom_score_adj:0`, which is the lesson's line word for word.
- **`fill-memory-report`** (fill-in): `MemAvailable`, swap used, the top process by RSS (a service holds 150 MB on purpose), and the kernel's `Killed process` lines counted.
- **`write-limited-run`** (write): `limited-run NAME LIMIT COMMAND...`: `systemd-run --wait --collect`, the `Finished with result:` line parsed, exit 137 when killed.
- **`build-contain-the-leak`** (build): find the leaking service, read its cgroup's `memory.peak` before touching anything, cap it at 128 MB with no swap through a drop-in, watch the kernel kill it and systemd restart it, and give the database `OOMScoreAdjust=-900`. Six checks.
- **`debug-oomkilled`** (debug): three services, three memory mistakes: `MemoryMax=32M` under a 100 MB working set, `MemoryMax=512` (bytes), and `OOMScoreAdjust=1000` on the database.

**What the contract caught, two things:**

1. _A service under a limit that keeps being killed has no stable cgroup:_ each restart recreates it and `memory.peak` starts again, and in the two-second restart gap the directory doesn't exist at all, so a solution that read the peak last failed at random. The peak is read first, while the leak is still unchecked, which is also the right order on a real server.
2. _`systemctl is-active` exits non-zero for `activating`,_ which is the state a restarting service is in for a good part of every cycle. The check accepts the word and ignores the status.

**Decisions for you to review:**

1. _Services keep restarting under their limit rather than being stopped._ The build asks for the leak to be contained, not the indexer switched off; the lesson's point is that the limit does the containing. A learner who stops the service fails a check that says so.
2. _`OOMScoreAdjust=-900` for the database,_ checked as "-500 or lower", so -1000 (never kill) passes too.
3. _No swap in the labs' limits (`MemorySwapMax=0`),_ so the kill is prompt and deterministic; the lesson's "some swap is fine" stands for the machine, not for a leaking service's cgroup.

**Next:** CPU scheduling and cgroups, with `CPUQuota=` and `cpu.stat`'s throttling counters, which the same probe showed working.

## 2026-11-09: Disks and filesystems goes ready, with real disks in the lab

The sixth ready cloud topic, and the one I expected to be hardest, since a container has no disks. It turns out a privileged container can attach a file as a block device (a loop device), format it, mount it, grow it, and even run LVM on it, so the labs use real `mkfs`, `mount`, `fstab`, `df`, `lsof` and `resize2fs` on disks the image brings along.

**How a lab gets its disks.** Each disk is an image file under `/var/lib/lab`, made at image build (blank, or formatted and filled with `mkfs.ext4 -d seed`). At boot a oneshot unit runs `disks.sh`, which attaches each image to a loop device, labels it under `/dev/lab/` (as a cloud labels volumes under `/dev/disk/by-id/`, so no prompt or check depends on which loop number a disk got) and mounts the ones the scenario needs. `lab-grow NAME SIZE` stands in for the cloud console's "modify volume". LVM works once `lvm.conf` stops waiting for udev, which a container doesn't run.

**The five labs:**

- **`example-new-disk`** (worked example): `lsblk`, `mkfs.ext4`, `mkdir` and `mount`, `df -h`, `blkid`, an `fstab` line by UUID with `nofail`, then `umount`, `daemon-reload` and `mount -a` to prove the line without a reboot.
- **`fill-add-disk`** (fill-in): the same as a script, for XFS: `xfs`, `UUID`, `nofail`, `-a`.
- **`write-disk-report`** (write): four lines about a filesystem: bytes used, inodes used, the biggest top-level folder, and how many deleted files are still held open (`lsof +L1`, which needs `sudo` to see other users' processes, so the checks run the script as the learner).
- **`build-full-disk`** (build): a data volume at 90%, rotated logs to remove, a 40 MB log the running shipper holds open after someone deleted it (truncate it through `/proc/PID/fd/N`; the shipper must stay up), an uploads volume with free bytes and no inodes, and a volume enlarged "in the console" that `resize2fs` grows while mounted. Seven checks.
- **`debug-wont-mount`** (debug): three data disks with fixed UUIDs and an `fstab` with three mistakes: a UUID one digit off, `ext4` for an XFS disk, a mount point that doesn't exist. `mount -a` complains once per mistake, each differently.

**What the contract and the probes caught, four things:**

1. _Loop devices outlive their container._ Removing a container doesn't detach them, and the "(deleted)" marker I meant to clean up by never appears for a file on an overlay filesystem, so after a few runs the free loop numbers climbed past the device nodes a container is born with and the disks stopped attaching. The checker now runs an image's `/usr/local/lib/lab/teardown.sh` before removing a container (unit-tested), the storage labs' teardown unmounts and detaches their disks, and `disks.sh` makes a missing device node itself. After a full run, Docker's own two loop devices are the only ones left.
2. _Fixed UUIDs plus a stale device make `mount` by UUID pick the stale one,_ which is how the debug lab's XFS mount showed up from the wrong device. The teardown fixes the cause; the lesson gains nothing from it, but the devlog does.
3. _`mkfs.ext4 -d` turns zero-filled files into holes,_ so a disk seeded from `/dev/zero` was nearly empty and `lost+found` was its biggest folder. The seeds use `/dev/urandom`.
4. _A child process inherits the open file._ The shipper's `sleep` held the deleted log too, so `lsof` counted two; the child closes it (`3<&-`). And `df -i` can't be combined with `--output`; `--output=ipcent` alone gives the inode percentage.

**Decisions for you to review:**

1. _The storage labs are the first with a teardown step,_ and the checker runs it for any lab that has one. A learner who removes a container by hand instead of `labcheck stop` leaves loop devices attached until Docker Desktop restarts; the README says so.
2. _No LVM hands-on yet,_ although it works in the lab: the build grows a plain volume with `resize2fs`, which is the common cloud case for a data volume. An LVM lab (`pvresize`, `lvextend -r`) would fit a later revision of the topic.
3. _The base layer gained `xfsprogs`, `lvm2` and `lsof`._ One line for all systemd labs, as before.
4. _`x-systemd.device-timeout=5` in the debug lab's planted `fstab`,_ so systemd doesn't wait ninety seconds at boot for volumes it can't see (a container has no udev); the mistakes are elsewhere, and the option is documented on the fstab page the lesson links.

**Next:** Memory and the OOM killer, and CPU scheduling and cgroups, which the first probe of the day showed work with `systemd-run -p MemoryMax=` and `-p CPUQuota=` in these containers.

## 2026-11-09: Package management goes ready, with a package repository in the image

The fifth ready cloud topic. Its problem was that `apt` needs repositories, and a lab that reaches Ubuntu's would be slow, different every day and useless offline. So the image builds a repository of its own.

**`make-repo.sh`** runs once at image build: it makes five small packages with `dpkg-deb` (each installs a script that prints its own version), puts them in three suites, `noble`, `noble-updates` and `noble-security`, writes the `Packages` and `Release` files with `apt-ftparchive`, replaces Ubuntu's sources with a `file:` source marked trusted, installs the old versions on purpose, and then empties `/var/lib/apt/lists`, as on a server that hasn't checked in a while. Two of the packages carry the lesson's gotchas: `linux-image-shop`, a stand-in for a kernel, whose install script creates `/run/reboot-required` and lists itself in `reboot-required.pkgs` the way Ubuntu's does; and `shop-theme`, which has a configuration file under `/etc`, so `apt remove` leaves an `rc` record and the file, and `apt purge` takes both. `apt list --upgradable` then reads exactly as the lesson says: `shop-agent/noble-security 1.1 all [upgradable from: 1.0]`.

**The five labs:**

- **`example-update-then-look`** (worked example): `apt update`, `apt list --upgradable`, `apt policy`, `apt install`, `dpkg -l`, and save the list of what still waits; nothing upgraded.
- **`fill-patch-server`** (fill-in): `update`, `--upgradable`, `hold`, `upgrade -y`, and the reboot note. Wrong fixes include forgetting `-y` (apt asks, nobody answers, nothing happens) and holding the wrong package.
- **`write-security-updates`** (write): only the packages whose update comes from `noble-security`, with `apt install --only-upgrade`; `nothing to do` on the second run.
- **`build-patch-day`** (build): hold `shop-report`, upgrade the rest, purge the theme, install the dashboard, and report what still waits and whether the machine wants a reboot, from the machine itself.
- **`debug-nightly-patch`** (debug): upgrade before update, the wrong package held, and `/etc/reboot-required` where `/run` was meant; each witnessed by a different command.

**What the contract caught, three things, all in my checks rather than the labs:** apt doesn't copy a `file:` repository's lists where I looked for them, so the "list refreshed" check now asks apt what it knows; and twice a check ran the learner's script a _second_ time, after the solution had already done the work, which hid the "upgrade before update" bug and made a "forgot update" script look right. Those checks now put the server back to a fresh night first (old versions, nothing held, no list, no reboot note) and run the script once. That's a new kind of check, a scenario reset, and the content README now describes it.

**Decisions for you to review:**

1. _A fake repository rather than Ubuntu's._ The lesson's commands are the real ones; only the packages are the shop's. Deterministic, offline, and the kernel stand-in demonstrates the reboot mechanism without a kernel.
2. _The base layer gained `apt-utils`,_ for `apt-ftparchive`; small, and now every systemd lab image is rebuilt from the same line once more.
3. _Checks may reset the scenario_ (downgrade packages, empty the list) before running the learner's script, when the script's behaviour on a fresh state is what's being proved. They leave the server in the state a correct script produces.

**Next:** Disks and filesystems, on loop devices: a probe shows ext4, XFS (at 400 MB and up), growing with `resize2fs`/`xfs_growfs`, `fstab` with `mount -a`, an inode-starved filesystem and a deleted-but-open file all work in the lab; LVM needs its udev settings turned off in `lvm.conf`, and lab loop devices need cleaning up at boot, since a removed container leaves them attached to Docker's machine.

## 2026-11-09: Users, permissions and SSH goes ready, with a real sshd in the lab

The fourth ready cloud topic, and the first whose labs reach the machine the way you reach every server: over SSH, with a key. The shared systemd base now installs `openssh-server`, so every systemd lab has an `sshd` (socket-activated, listening inside the container only); the ten Services and Processes Dockerfiles were regenerated from the same first `RUN` line, and all twenty labs keep their contract on the new base.

**The five labs**, around the shop's server and three people, `ada` (in `developers`), `ben` and `carol`:

- **`example-read-and-set-modes`** (worked example): `ls -l` on a deploy script and an API key root left world-readable; `stat -c '%a %U:%G %n'` for the numbers; `chown shop:shop`, `chmod 750`, `700` and `600`; then `id` and `umask`.
- **`fill-service-account`** (fill-in): `add-service-account NAME DIR` with three gaps: `/usr/sbin/nologin`, the owner, `750`. Checked for a second account, so a typed-in answer fails.
- **`write-share-folder`** (write): `share-folder GROUP DIR USER...`: `getent group || groupadd`, `chgrp`, `2770` (or `770`), `usermod -aG`. A check that `ada` is still in `developers` catches `-G` without `-a`; another that `carol` can't get in.
- **`build-lock-down-the-server`** (build): the secret to `shop` only; a `deploy` group with `ada` and `ben` and the script `shop:deploy 750`; a sudoers file letting the group run exactly `systemctl restart shop-api` without a password (`visudo -c`, `sudo -l -U ben`, and a check that it isn't `NOPASSWD: ALL`); Ben's public key installed with `700`/`600`, then `ssh -i ~/keys/ben ben@localhost 'sudo -n systemctl restart shop-api'` for real. Eight checks, the last two over SSH.
- **`debug-cant-log-in`** (debug): three mistakes with three different witnesses: the private key is `644` (the client says `UNPROTECTED PRIVATE KEY FILE`), Ben's `.ssh` is `775` (`journalctl -u ssh` says `bad ownership or modes`), and the sudo rule names `shopapi` (`sudo -l -U ben` shows it).

**Keys are made in the image,** by `ssh-keygen` at build time, never committed: a private key in a repository is a bad habit even when it opens nothing. The copy of Ben's private key in the learner's home is there for testing, and the prompts say so and why it's unusual.

**The lesson** gained the commands the labs lean on that it hadn't named: `stat -c`, `getent`, `useradd --system`, `visudo -f` and `-c`, `sudo -l -U`.

**Decisions for you to review:**

1. _Every systemd lab now runs an `sshd`,_ not just this topic's. One base layer for all of them is simpler than two, and a server without `sshd` would be the odd one.
2. _`2770` is taught in a hint, `770` accepted._ The setgid bit on a shared folder is the right habit but isn't in the lesson; the check takes either.
3. _The build's SSH test uses a copy of Ben's private key on the server._ Realistic labs have one machine; the prompt says a real private key never leaves its owner's machine, and the debug's first bug (a world-readable private key) makes the point again.

**Next:** Package management and patching, with a local package repository so `apt` works without the network.

## 2026-11-09: Your place in a long topic

The owner, partway through Shell essentials: "It has 24 practice questions so there needs to be a way to track where you are for the reading and a way to track what practice questions you've done and haven't done. Make it the same across every lesson." Built before the next labs.

**What a topic page has now.** An outline beside the content on a wide screen (sticky, so it stays while you scroll) and above it on a narrow one, headed _Your place in this topic_:

- **Learn:** what you can do after, the lesson, the main resource, the recap. The lesson's paragraphs are each a place, so while you read, the outline says _The lesson (part 6 of 10)_, with a ▸ on the part you're in.
- **Practice · 7 of 24 done:** every item as a numbered cell linking to its card, green with a ✓ when done, amber with a ◐ when tried and not yet right, plain otherwise; a ring on the one in view; and _Next not done: Practice 8_.
- **Prove it · 1 of 3 passed:** the three checks, ✓ or ○.
- **Continue where you left off: Practice 8**, when a previous visit was remembered.

Each practice card's position line now reads _Practice 7 of 24 · Done ✓_ or _· Tried, not right yet_, and an item that was already done when the page opened is folded to its heading and a _Show it again_ button, so a long topic shows what's left. An item done during the visit stays open, so an answer never makes its question vanish.

**Where "done" comes from.** The learner's saved answers: one correct answer or Check of an item makes it done, by the same history the proof checks are read from (`itemStates`, pure and tested). There is no tick to set by hand, in keeping with ADR-0002, and it's the same on every device. The reading position is different: it's a convenience, remembered in this browser's `localStorage` (`placeMemory`), so it survives a reload but not a change of machine, and the page works the same without it.

**How the page knows where you are.** Every place has an element with a `data-place` attribute whose value is its id: the objectives, each lesson paragraph (`LessonView` marks the intro's children), the main resource, the recap, each practice card, each proof check. An `IntersectionObserver` watches them and takes the topmost one that reaches into the top 45% of the screen (`useCurrentPlace`), which is what you're reading rather than what's coming up. The test environment lays nothing out, so there the current place stays unknown and the outline is tested for its links, counts and states.

**Checked on my own dev server** at desktop width: the rail sticks, the lesson part and the practice cell follow the scroll, and a reload offers _Continue where you left off: Practice 1_. The browser wouldn't resize to a phone width from here, so the narrow layout rests on the standard breakpoint classes rather than a screenshot.

**Tests:** 11 new (item states, the remembered place, and the page: the outline's links and states, a signed-out visitor, folding and unfolding, an item done now, continue or not). 676 web tests pass.

**Decisions for you to review:**

1. _Done means a correct saved answer,_ never a tick you set yourself. It's the honest reading of ADR-0002, and it means a worked example counts as done once you've pressed its Check (or recorded its lab result).
2. _Items already done when the page opens are folded away._ One click brings any of them back. If you'd rather see everything expanded always, it's a one-line change (`collapsed` in `Practice`).
3. _The reading position is per device,_ in `localStorage`, not an event. An event type would need a production migration, and where you were on a page isn't learning data.
4. _The outline is for topics, not checkpoints._ A checkpoint has no lesson or ladder; its page is short.
5. _On a phone the outline sits above the lesson,_ in full. A collapsible version for small screens is a possible refinement.

**Next:** back to Module 1's labs: Users, permissions and SSH.

## 2026-11-09: Processes and signals goes ready, and the Services topic unlocks

Processes and signals is the third ready cloud topic, and since it was the only draft between Shell essentials and Services and logs, the live map's Module 1 now runs Shell → Processes → Services with nothing Locked behind a draft.

**Why these labs boot systemd too.** The lesson says PID 1 adopts orphans and reaps zombies. In a plain container PID 1 is `sleep infinity`, which does neither, so a learner checking the lesson's claim would have found it false. With systemd as PID 1 the process tree looks like a server's, which is also what the worked example reads. The five labs reuse the Services labs' base layer (the same first `RUN` line), so Docker builds it once for both topics.

**The five labs:**

- **`example-stop-a-runaway`** (worked example): a colleague's backgrounded report script, adopted by PID 1, loops forever. `ps -ef --forest`, `pgrep -a`, `kill` (TERM), the `||` that prints only when `pgrep` finds nothing, the trap's last log line, and `ps -o comm= -p 1` to note that PID 1 is systemd.
- **`fill-run-report`** (fill-in): a runner with four gaps, `&`, `$!`, `wait "$pid"`, `$?`. The job writes its own PID into the report, so a check can tell `$!` from `$$`.
- **`write-graceful-stop`** (write): `TERM`, wait up to five seconds with `kill -0`, then `KILL`; proven on a polite worker that logs its cleanup and a stubborn one that ignores `TERM`.
- **`build-nightly-runner`** (build): three two-second jobs at once, each one's exit status reported in order, exit 1 if any failed, and a `trap` that stops the jobs on `TERM` or Ctrl-C. Checks: a good night, a bad night (a flag file makes one job fail), under five seconds for all three, and an interruption that leaves nothing running.
- **`debug-stop-workers`** (debug): three mistakes with three different symptoms: `pgrep worker` matches the script's own name, so it kills itself halfway; `kill -9` leaves the workers' PID files behind; and the report reads `pgrep`'s exit status backwards. Workers run at boot as the learner, and a helper restarts them for another try.

**What the contract caught, three things:**

1. _A script's process name depends on its shebang._ With `#!/usr/bin/env bash`, `env` runs bash a second time and the process is called `bash`; `pgrep -x runaway.sh` found nothing, `kill` got no argument, and the worked example "passed" with the runaway still running. Every program a lab finds by name now starts with `#!/bin/bash`, and the content README says why. It's also what made the debug lab's first planted bug real: the stop script has to be _called_ `stop-workers` for `pgrep worker` to catch it.
2. _`pgrep -f` matched the check itself,_ because the check's own command line contains the pattern. The pattern is now `/srv/job[s]/`, the old trick; also in the README.
3. _`grep -c` exits 1 when it counts zero,_ so a check expecting "0" failed on its exit status; `find | wc -l` instead.

**The lesson** gained a sentence on `pgrep`, `pkill`, `-x` and `-a`, with the warning that a name match catches more than you meant, since two labs depend on it.

**Decisions for you to review:**

1. _Processes labs boot systemd_ although the topic isn't about systemd, for the reason above; the cost is a privileged container, which the Services labs already need.
2. _Checks may start throwaway processes of their own_ (a fresh worker to stop, a runner to interrupt) when that's the only way to exercise the learner's script; they clean up after themselves. The README's "checks only read" rule now says so.
3. _The debug's first bug is a self-match._ It's the subtlest of the module so far, and the prompt names its symptom ("stops before it has finished"). If it proves too hard in practice, it can become a hint-carrying fill-in instead.

**Next:** Users, permissions and SSH, a plain container; then Package management, with a local package repository so `apt` works without the network.

## 2026-11-09: Services and logs goes ready, on labs that boot systemd

The owner reviewed every decision listed so far and accepted them all, ADR-0018 included (its status line and the index say so), and said to keep going. The riskiest piece of the remaining Module 1 work was systemd in a container, so that went first: Services and logs is the second ready cloud topic, and the checker now knows how to boot a lab.

**The checker.** A `lab: { init: systemd }` container runs privileged with `/sbin/init` as PID 1, `/run` on a tmpfs, and _its own cgroup namespace_. The first design shared the host's cgroup tree, and a probe on Docker Desktop showed the difference: with a private namespace a `MemoryMax=64M` unit is killed when it grows past the limit (`Result=oom-kill`) and a `CPUQuota=20%` unit is throttled, exactly as on a server; with the host's tree the memory limit didn't kill. The checker waits for `systemctl is-system-running` to say `running` or `degraded` before asking the container anything, because checks run too early see services that haven't started. `test --jobs N` proves several labs at once, each lab's output printed whole when it finishes; CI uses four. Unit tests cover the run arguments and the wait.

**The five labs**, all on a tiny Python web API, `shop-api`, that answers on `PORT` and exits with an error when a client asks for `/crash`:

- **`example-first-service`** (worked example): a unit file waits in the learner's home; the six-line walkthrough reads it, copies it to `/etc/systemd/system`, `daemon-reload`, `enable --now`, `status`, `journalctl -u`.
- **`fill-unit-gaps`** (fill-in): four `...` gaps: `User=`, the Python path in `ExecStart=`, `Restart=`, `WantedBy=`.
- **`write-unit`** (write): a unit for a worker script, with a working directory and a five-second restart delay, checked through `systemctl show`.
- **`build-restarting-api`** (build): the unit from scratch; a persistent journal; then crash the service on purpose, watch systemd bring it back, and report the `-p err` lines and systemd's own restart count. Nine checks.
- **`debug-service-wont-start`** (debug): three mistakes that surface one at a time: a section called `[Services]` (systemd ignores it, so the unit has no `ExecStart=` and won't load), `User=shop-api` (no such account: status 217/USER), and `PORT=80800` (the program refuses to start and says so in the journal, and systemd restarts it over and over).

**What the contract and the probes caught, five things:**

1. _A "forgot daemon-reload" wrong fix passed._ systemd 255 loads a unit it has never loaded (or failed to load) on the next start, so the mistake only bites for a unit that was already running. The lesson's rule stands; the wrong fix was dropped rather than contrived.
2. _`systemctl` as the learner failed with "Failed to connect to bus"._ Ubuntu's `systemd` package doesn't pull in D-Bus, and a non-root `systemctl` needs it. The images install `dbus`, as every real server has it.
3. _The "make the journal persistent" step was already done._ Ubuntu's package creates `/var/log/journal`, so the pristine image passed that check; the build's image now removes the folder, and the task is real again.
4. _A restarted journald doesn't move the log; `journalctl --flush` does._ And a folder made with a plain `mkdir` gives the journal files no group, so the learner couldn't read their own service's log afterwards: `systemd-tmpfiles --create --prefix /var/log/journal` sets the permissions, which is the procedure the DigitalOcean tutorial teaches. The lesson and the recap now say so, and that mistake is a wrong fix of its own.
5. _A crash-looping service is "active" for a moment each time it's restarted,_ and a check caught that moment once. Checks that a service runs now read `is-active` twice, two seconds apart, with the same `MainPID`.

**Decisions for you to review:**

1. _Services and logs is `ready` while its prerequisite, Processes and signals, is still a draft._ On the live site it shows as Locked until Processes goes ready, which is the next pull request. I did the systemd topic first to retire the risk.
2. _The learner is in the `adm` and `systemd-journal` groups_ in systemd images, as a cloud image's default user is, so `journalctl` works without `sudo`.
3. _Lab images install D-Bus_ so `systemctl` works for the learner as it does on a server, rather than teaching `sudo systemctl status`.
4. _A lab's scenario may include a Python program_ (`server.py` here); the validator now forbids only the three Python exercise files in a lab folder, not every `.py`.
5. _CI proves labs four at a time._ Ten labs took about a minute locally that way; the job will grow with every topic, and `--jobs` keeps it in hand.

**Next:** Processes and signals, then Users, permissions and SSH, both plain containers; then the rest of Module 1 in order.

## 2026-11-09: Shell essentials goes ready, on five labs

The first cloud-track topic a learner can open on the live site. Shell essentials' ladder is now a worked example, 21 recall items, a fill-in and a write, and its proofs are a build and a debug; everything but the recall items is a lab on the same generated logs (ADR-0018).

- **`example-count-requests`** (worked example): a five-line walkthrough, each line a labelled step, that counts requests by status and saves the first three error lines. The checks compare the saved files with the same pipelines over the data.
- **`fill-count-errors`** (fill-in): `~/bin/count-errors` with three gaps. Checked on `app.log` and on `worker.log`, so an answer typed in by hand (one of the wrong fixes) fails the second log.
- **`write-top-paths`** (write): a script with two arguments, checked with N=2 on two logs and N=1 on one, with the spacing of its output normalised before comparing.
- **`build-log-report`** (build): from the last entry.
- **`debug-broken-report`** (debug): `~/bin/report` with three bugs: `grep -c 500` (which counts a byte count of 500 and misses 503), the status field where the path should be, and `uniq -c` without a sort. Each wrong fix leaves one bug in place.

**What the contract caught this time.** A wrong fix I wrote for two labs, `sort -r` instead of `sort -rn`, passed every check. It turns out not to be a mistake after `uniq -c`: the counts come padded to the same width, so a text sort orders them like numbers (until a count has eight digits). The lesson's warning about `sort -r` stays true for unpadded numbers, and the labs now plant a mistake that really is one. The seed also grew `worker.log` and `old-access.log`, so the fill-in, write and debug labs can check a script on a second file; the seed is one file copied into each lab's folder, since a Docker build only sees its own folder.

**The app bundles Module 1 in.** `content.ts` now includes `csa.linux.*` topics in the eager bundle and the outline module leaves them out, so the Today page and the follow-ups, which only look at bundled topics, see Shell essentials. The lazy-track tests and the map test were adjusted: the rule is now that a topic which loads on demand must never be ready. Everything else is the Python track's machinery, unchanged: progress counts a passed lab build or debug as that proof because the event is a `code_check`.

**Decisions for you to review:**

1. _Shell essentials is `ready` on the live site_ although its labs need Docker and the repository on the learner's machine. You have both; the lab view says exactly what to run. A learner without them can still read the lesson and do the recall items.
2. _Each lab builds its own image from a copy of the same seed script._ Simple and self-contained; a shared base image would save a few seconds per build and is easy to add later.
3. _The Today page knows the cloud track only through bundling._ It plans from the main track; a ready cloud topic shows on the cloud map and its own page, and its reviews are scheduled like any other topic's. Whether Today should mix tracks is a later question (the spec's F12).

**Next:** labs for the other thirteen Module 1 topics, the ones needing systemd first (services and logs); the checkpoint as a debug lab with five planted faults.

## 2026-11-09: The lab view

The topic page can now show a lab (ADR-0018). `ExerciseView` hands any exercise with `runtime: lab` to a new `LabExercise`: the prompt; the three `labcheck.py` commands with the lab's name filled in, and a note that Docker Desktop has to be running; for a worked example, the walkthrough script with its labelled steps; the list of checks, each with a circle that becomes a tick or a cross; and a box for the checker's printed result with a Record button. `parseLabResult` (in `web/src/labs/result.ts`, pure and tested) refuses anything that isn't a result, a result for another lab, or one for another revision, and recounts the passes from the checks rather than trusting the numbers. Recording raises a new `lab` activity, which `PracticeItem` saves as a `code_check` event with `labEventData`: `runtime: lab`, the checker's version, the time, the counts and the failing ids. Because it's a `code_check` on the topic's build or debug item, progress treats a passed lab as that proof with no change to the derivation. Written hints work for the stages that allow them; the tutor stays off, since it has no code to look at.

**Loading.** `content.ts` grew two globs, `solution.sh` and `checks.yaml`, and an exercise now carries `runtime` and `checks` (ids and descriptions only; the commands never reach the browser). The content test that insists every exercise has Python tests now asks a lab for checks instead. `Hints` and `ReferenceSolution` moved to `exerciseParts.tsx`, shared by both views.

**Tests:** eleven new (the result parser and event data, the view's commands, checks, pass, partial pass, refusals, hints, walkthrough; a lab as a proof item recording its event). The first run caught a test of mine that pasted a result for the wrong lab and expected it to count, which is the parser doing its job.

**Decisions for you to review:**

1. _The commands are shown in full on the page,_ repository-relative, rather than hidden behind a "how to run" link: the learner is at a terminal anyway, and copying beats remembering.
2. _The paste box takes a worked example's result too,_ so the learner sees the ticks after following the walkthrough; it records a `code_check` like any Check of a worked example, which proves nothing and costs nothing.

**Next:** Shell essentials' other four labs (a worked example, a fill-in, a write and the debug), then the topic to `ready`, which means bundling Module 1 into the app rather than loading it on demand.

## 2026-11-09: The lab checker's local mode, and the first lab

The owner chose the plan (containers on the learner's machine, GitHub's registry when a second learner needs it, results pasted in) and said go. The design is [ADR-0018](decisions/0018-lab-checker-local-mode.md); this entry is the build.

**A lab is an exercise with `runtime: lab`.** Same `exercise.yaml`, same stages, same place in a topic's ladder, so the definition of done doesn't change; the folder holds a `Dockerfile`, `checks.yaml`, `solution.sh` and `wrong/*.sh` instead of Python files. The content model gained `runtime`, `lab: { init }`, and the `Expect`, `LabCheck` and `LabChecks` shapes; `test_skills` keys may now be check ids for labs; the validator checks a lab's structure and, with `--labs`, its contract.

**`tools/labcheck.py`.** `start` builds the image and starts the container and tells the learner how to get a shell in it; `check` runs the checks with `docker exec` as root, prints pass or fail per check with the reason, and prints the result JSON to paste (lab, rev, checker version, time, which checks passed, nothing else); `stop` removes the container; `test` proves the contract: pristine must not pass, the solution must, every wrong fix must fail; `list` names the labs. Fixes are applied as the `learner` user in a fresh container, with CRLF stripped in case of a Windows checkout. It's PyYAML and the standard library over the `docker` command, so it runs wherever the repository and Docker are.

**The first lab, and what the contract caught.** _A report from the shop's logs_ (Shell essentials' build) seeds 600 access-log lines, 200 application-log lines and a 300-row CSV by arithmetic on the line number, so the files are identical on every build; the checks compute the right answers from the data rather than hard-coding them. The first run passed four of five wrong fixes and failed one: `uniq -c` without `sort` gave the right top path, because `/home` arrived in runs of four. The data now puts `/home` never twice in a row and `/cart` in pairs, and the mistake shows. That is exactly the kind of thing the contract exists to catch, and the content README now says so.

**CI.** A `Labs` job runs `labcheck test --all` on Ubuntu runners, which have Docker; the first lab takes about twenty seconds locally. If the job grows slow, it can run only when `content/**` or the checker change.

**Not yet:** the lab view on the topic page (the commands, the checks, the paste box, the reference solution after a pass), which is the next pull request, and the other four labs Shell essentials needs to go ready.

**Decisions for you to review:**

1. _Results are `code_check` events with `data.runtime: lab`,_ not a new event type: progress already counts a correct `code_check` on the build or debug item as that proof, and the `events` table's type list would need a production migration for no gain.
2. _Images build locally; publishing waits._ The registry (`ghcr.io`) is chosen, but a published image is public and nobody but you needs one yet.
3. _Checks compute the truth from the data._ It makes `checks.yaml` longer than a hard-coded `equals`, and it means a change to the seed can't leave a check stale.
4. _Solutions and wrong fixes run as the learner,_ with `sudo` available, so they can only do what a learner could.

**Next:** the lab view in the web app, then Shell essentials' other four labs and the topic's switch to `ready`.

## 2026-11-09: Module 1, topics 13 and 14: triage and hardening. The module's lessons are complete.

Performance triage (`csa.linux.triage`) and Hardening (`csa.linux.hardening`), as drafts: 31 recall items, 14 of them `predict_shell`. With these, **all fourteen topics of Module 1 are drafted**: 228 recall items across the module, 120 of them shell predictions proven in real bash, each topic with a lesson for a complete beginner, an explain prompt with rubric and model answer, four to six skills and a review pool. The checkpoint, _the broken server_, stays a planned outline until the lab checker can run it.

**The two closers use everything before them.** Triage's items read `dmesg`, `vmstat`, `pidstat`, `iostat`, `strace -c`, `perf report` and `sar` the way the first minute of an incident does, and the lesson is built on Gregg's USE method and the Netflix checklist. Hardening's items audit `ss -ltnp`, `sshd -T`, an `sshd_config`, `ufw status`, `/etc/passwd` and `sudoers`, and read Lynis and OpenSCAP reports, since the spec's proof for this topic is "apply a baseline, then prove it with a benchmark scan". The Netflix article's site refuses automated fetches, so it is linked on Gregg's word and the devlog's; every other URL in the two topics answered 200.

**What Module 1 still needs to go ready,** per ADR-0017: the hands-on half. For each topic a worked example, a fill-in and a write step, and the build and debug proofs, run in a container on the learner's machine through the lab checker's local mode, which is the next build. The checkpoint's five planted faults are the same work at module scale. Until then the module is readable and quizzable on the dev server (`npm run dev` in `web/`, then `/topic/csa.linux.shell` and on), and nothing in it is shown on the live site.

**Decisions for you to review:**

1. _Triage lists four prerequisites_ (memory, CPU, storage, networking) and Hardening four (permissions, services, packages, networking): both are summary topics, and the map should say so.
2. _The hardening lesson tells the learner to keep SSH on port 22._ Moving the port is a common recommendation and a weak one; the lesson says why, and the explain rubric doesn't penalise either view.

**Next:** the lab checker's local container mode (ADR-0014 and ADR-0017), starting with a lab image for Shell essentials and the checker's read-only `docker exec` probes; then the checkpoint.

## 2026-11-09: Module 1, topics 10 to 12: networking, boot, scripting

Networking from the host (`csa.linux.net-tools`), Boot, cloud-init and instance metadata (`csa.linux.boot`) and Shell scripting (`csa.linux.scripting`), as drafts: 50 recall items, 25 of them `predict_shell`.

**Scripting is the topic the item type was made for.** Every shell item there runs bash itself: `set -e` with and without, `set -u`'s `unbound variable`, `pipefail`'s status, word splitting on an unquoted variable, `"$@"` against `$*`, an `EXIT` trap firing after a failure, `exit 2` seen by the caller, `mkdir` against `mkdir -p`, `ln -sfn`, and a check-before-append function called twice. Each is a tiny script whose output the validator proved. The networking and boot items read captured output as before (`ip`, `ss`, `dig`, `curl -I`, `tcpdump`, `nft list ruleset`, `systemd-analyze`, the boot journal, user data, cloud-init's log, a metadata listing), with two real-bash exceptions: the ephemeral-port arithmetic with `read`, and the instance-ID comparison that cloud-init itself makes.

**Two portability notes for shell items,** learned here: an error message's `bash: line 1: ` prefix is stripped with `sed` before comparing, since the program name can differ between machines; and `set -u`'s message text itself is identical in bash 5 on both. `ln -s` on Git Bash makes a copy rather than a link unless Windows symlinks are enabled, but the item only shows the file behind `current`, which comes out the same.

**Resources.** DigitalOcean's networking terminology tutorial (CC BY-NC-SA 4.0), the ArchWiki's network-configuration, nftables and boot-process pages (GNU FDL 1.3), the `ss` and `tcpdump` manuals, RFC 9293 for the TCP states, cloud-init's own documentation, the AWS IMDSv2 page (copyright, linked) with the Azure and Google equivalents (CC BY 4.0), the Missing Semester's scripting lecture (CC BY-NC-SA 4.0), Google's Shell Style Guide (CC BY 3.0), Greg's Bash Pitfalls and ShellCheck. The GNU Bash manual's own site refuses automated fetches, so the `bash(1)` page on man7.org stands in for it.

**Decisions for you to review:**

1. _The 2019 breach is named only by year._ The IMDSv2 lesson and items explain server-side request forgery against the metadata service with "a large breach in 2019" rather than naming the company, since the point is the mechanism.
2. _Networking stays at the host's view._ Subnets, routing and DNS in depth belong to Module 3; this topic teaches the tools and what their output means.

**Next:** performance triage and hardening, the last two topics; then the checkpoint's outline review and the lab checker's local mode.

## 2026-11-09: Module 1, topics 7 to 9: memory, CPU, containers

Memory and the OOM killer (`csa.linux.memory`), CPU scheduling and cgroups (`csa.linux.cpu`) and How containers work (`csa.linux.containers`), as drafts: 45 recall items, 19 of them `predict_shell`. These three belong together, and the containers lesson is written as the payoff of the two before it: a container is a process tree with namespaces for its view, a cgroup for its limits (the files the memory and CPU topics just taught), and an overlay root built from image layers.

**Where the shell items are real.** Several run bash itself rather than reading captured output: a child shell that kills itself with `SIGKILL` and the parent that prints `exit status 137`; `read quota period < cpu.max` and `$(( quota * 100 / period ))` for a quota as a percentage; a for-loop over two cgroups' `cpu.max` with an `awk` ternary; `$(( $(cat memory.max) / 1048576 ))` for a limit in MiB; and plain folders standing in for an image layer and a container's upper layer, changed, shown and removed in one line. The rest read `free`, `/proc/meminfo`, `vmstat`, the OOM log, `top`'s CPU line, `uptime`, `ps`, `cpu.stat`, a Dockerfile, a `docker images` table and an overlay mount line.

**Resources.** The kernel's own documentation (GPL-2.0) carries three of the topics' main readings: the memory _Concepts overview_, the CFS design note and the overlayfs document, with the cgroup v2 document for both controllers. Around them: Chris Down on swap and Julia Evans on containers (both copyright, linked), the ArchWiki (GNU FDL 1.3), the Linux man-pages, Docker's documentation (Apache-2.0) and the Kubernetes resource-management page (CC BY 4.0).

**Decisions for you to review:**

1. _Kernel documentation as main readings._ It's dense for a beginner, so each lesson carries the explanation itself and sends the learner to the document for the precise statement; the alternative was blog posts of uneven accuracy.
2. _Containers wait for Memory and CPU._ The containers topic lists both as prerequisites, because its cgroup half is their material; the spec's outline had it after CPU anyway.

**Next:** networking from the host, boot and cloud-init, shell scripting.

## 2026-11-09: Module 1, topics 4 to 6: services, packages, disks

The owner chose to finish Module 1's lessons before the lab checker. This batch: Services and logs (`csa.linux.services`), Package management and patching (`csa.linux.packages`) and Disks and filesystems (`csa.linux.storage`), the same shape as the first three: a lesson for a complete beginner, an explain prompt with rubric and model answer, four to five skills, a review pool, and a practice ladder of recall items (49 in all, 20 of them `predict_shell`).

**What the shell items do here.** None of these topics' tools exist in the browser or in Git Bash (`systemctl`, `apt`, `lsblk`), so every shell item reads _captured output_ of the real tool, written as a fixture file, with the text tools from Shell essentials: find the failed units in a `systemctl` listing, the security fixes in `apt list --upgradable`, the full filesystem in `df -h`, the inode-starved one in `df -i`, the deleted-but-open file in `lsof +L1`, the free space in `vgs`. That's a fair picture of the job: on a real server you run the tool and then read its output, and reading is the part that takes practice. Where bash itself is the tool (`test -f reboot-required && …`, `sort -V` on versions, `sed` capture groups on `blkid`), the command is real.

**Resources and licences.** DigitalOcean's community tutorials carry CC BY-NC-SA 4.0 in each page's source (checked with `curl`), so three of them anchor the services topic and two the storage topic. The kernel documentation is GPL-2.0, Google Cloud and Kubernetes docs CC BY 4.0 and Google's style guide CC BY 3.0, all checked the same way and queued for later batches. The Debian handbook (GPL-2.0-or-later or CC BY-SA 3.0), Fedora docs (CC BY-SA 4.0) and Ubuntu Server docs (CC BY-SA 3.0) are recorded from their published licence terms, since their footers didn't come through a fetch. Amazon's EBS page, Dan Luu's _Files are hard_ and Martin Fowler's _Immutable Server_ are copyright and linked only.

**One test loosened on purpose.** The map test counted exactly three Draft markers; it now asks for at least three, so each batch of drafts doesn't have to touch it.

**Decisions for you to review:**

1. _Captured output as fixtures._ It's the only way to teach `df`, `lsof` or `systemctl` in the browser without a shell, and it teaches reading the output, which is the skill. The outputs are realistic but hand-written; the labs will show the learner the real thing.
2. _Fowler and Dan Luu as readings._ Both are copyright and linked only, like Amazon's documentation; they're the clearest statements of immutable servers and of why `fsync` matters, and the platform's rule is only that nothing is copied.

**Next:** memory and the OOM killer, CPU scheduling and cgroups, how containers work.

## 2026-11-09: The cloud track begins: Module 1's first three topics, as drafts

The first content built on ADR-0017: Shell essentials (`csa.linux.shell`), Processes and signals (`csa.linux.processes`) and Users, permissions and SSH (`csa.linux.permissions`), the first three of Module 1's fourteen. Each has a lesson, an explain prompt with its rubric and model answer, skills, a review pool, and a practice ladder of recall items: 54 in all, 31 of them `predict_shell`, each proven in real bash by the validator (through Git Bash on this PC, on Linux in CI).

**What the lessons are built on.** Every reading is linked, never copied: MIT's Missing Semester notes (CC BY-NC-SA 4.0) for the shell, data wrangling, job control and SSH; William Shotts's _The Linux Command Line_ (CC BY-NC-ND 3.0) and his _Learning the shell_ lessons (a copyright notice that permits verbatim copying; linked only); the ArchWiki (GNU FDL 1.3) for users and groups, sudo, SSH keys and systemd; `signal(7)` from the Linux man-pages. Every URL answered 200 before it was written down. The lessons themselves are written for a complete beginner, as you asked: what a process is before fork and exec, what the ten characters of `ls -l` mean before octal.

**What a shell item can and can't do.** Only text-processing commands behave identically on Linux and in Git Bash, so the items read listings, logs, `/etc/passwd`-style files, a sudoers file and an SSH config with `grep`, `cut`, `sort`, `uniq`, `awk` and `sed`, and use bash itself for processes: subshells, `exec`, exit statuses, `&&` and `||`, background jobs with `wait`, `trap`, `kill -l`, and `umask` with shell arithmetic. Nothing that prints dates, sizes, PIDs or user names.

**Three things the validator caught,** each worth knowing:

1. A YAML plain scalar can't hold `: ` (as in `echo "exit: $?"` or `awk -F: ...`); such commands go in a `|` block.
2. `bash -c 'cmd'` doesn't fork for the last command in the string: it execs it in place. An item comparing a child's `$PPID` with the shell's `$$` was false until a trailing `echo` made the child not the last command. The item's explanation now says so, since it's a true fact about shells.
3. `grep ' 500 '` needs a space on both sides of the status code, so the access-log lines gained a size column.

**The lazy-track rule changed.** `content.lazy.test.ts` demanded that every cloud topic be `planned`; it now demands only that none is `ready`. Drafts are visible only on the dev server, where a topic page loads its track before rendering. When the first cloud topic goes ready, the Today page and the follow-ups will need to see it, which means bundling it in or teaching them to load the track.

**Decisions for you to review:**

1. _Drafts, not ready,_ as ADR-0017 says: the hands-on steps and the proofs wait for the lab checker's local mode. On the dev server (`npm run dev` in `web/`, then `/topic/csa.linux.shell`) you can read the lessons and try every item now.
2. _Prerequisites set:_ Processes and Permissions both need Shell essentials. The generated outlines had none.
3. _LinuxCommand.org's lesson 9 as the main resource for permissions,_ although it carries only a copyright notice (verbatim copying permitted) rather than a Creative Commons licence: it's the gentlest `ls -l` and `chmod` walkthrough I found, and the platform only links to it. Swap it for the ArchWiki page if you'd rather have a CC-licensed main resource.
4. _No Parsons items for the shell yet:_ the Parsons validator runs Python. A shell flavour (put the stages of a pipeline in order) would need the same bash runner; cheap to add later.

**Next:** the other eleven Module 1 topics the same way; then the lab checker's local mode, so Module 1 can go ready.

## 2026-11-09: `predict_shell`, the cloud track's first question type

The first thing ADR-0017 asks for, built end to end: a recall item that shows a few small files and a shell command over them and asks what it prints. The browser runs nothing. The validator runs the command in real bash and checks the output, so every item is proven against a real shell before a learner sees it, the way `predict_output` items are proven under CPython.

**What changed.**

- `tools/content_model.py`: `PredictShellItem` with `files` (path to contents; plain names or a few folders deep, never absolute or `..`, 4,000 characters in all at most), `command`, `expected_output`, `explanation`, `skills`.
- `tools/validate_content.py`: `check_predict_shell` writes the files into a temporary folder and runs `bash --noprofile --norc -c <command>` there with `LC_ALL=C`, `TZ=UTC`, `HOME` pointing at that folder and nothing on stdin, with a 10 s limit. The output must equal `expected_output` exactly, and stderr must be empty. `find_bash()` finds the shell: on Windows it looks next to `git` for Git Bash, because the `bash.exe` Windows puts on PATH is only a launcher for WSL (on this PC it's `WindowsApps\bash.EXE`); `VALIDATOR_BASH` overrides. Without a bash, every shell item is reported rather than skipped.
- Ready-topic rules count `predict_shell` as a recall item and as a predict kind for the review pool.
- Web: the `PredictShellItem` type, `PredictOutput` renders either kind (for a shell item: "The folder holds one file:", each file with its name, then the command at a `$` prompt), `PracticeItem` and the review scheduler treat it like `predict_output`. Tests for the model, the validator (right output, stderr, paths, no bash, a command that never ends) and the view.
- Docs: the data model, `content/README.md` (portability rules for shell items), the CHANGELOG.

**Two tests got longer timeouts** (15 s and 20 s): the first app-routes render and the every-checkpoint follow-up test timed out at 5 s while Docker Desktop was running alongside the suite. They were the only failures, and they pass alone; the limits now match the work they do.

**Decisions for you to review:**

1. _stderr must be empty._ Error messages differ between machines (and a typo in a command would otherwise pass silently), so an item that wants to show an error redirects it with `2>&1`, and the text is then compared like the rest.
2. _`LC_ALL=C` and an empty `HOME`._ The same sort order and messages everywhere, and no dotfiles. Items should still avoid anything machine-specific (dates, sizes, user names, the folder's path), which the two validators, Linux in CI and Git Bash here, would otherwise disagree about.
3. _Files are capped at 4,000 characters._ They're shown on the page, so they have to be readable; a log of six lines teaches `grep` as well as one of six thousand.

**Next:** Module 1's first topics as drafts, with lessons on the Missing Semester and `predict_shell` items, then the lab checker's local mode.

## 2026-11-09: Four ADRs accepted, the $10 cap set, the database types confirmed

**Accepted by the owner:** [ADR-0014](decisions/0014-cloud-labs.md) (cloud labs in the learner's own clouds), [ADR-0015](decisions/0015-hint-only-tutor.md) (the hint-only tutor), [ADR-0016](decisions/0016-parsons-problems.md) (Parsons problems) and [ADR-0017](decisions/0017-shell-in-the-browser.md) (teaching and proving the shell). Their status lines, the ADR index, CLAUDE.md, the roadmap and the cloud track's spec no longer say "proposed". With ADR-0017 accepted, the cloud track's Stage 1 can start: the `predict_shell` item type proven by real `bash` in the validator, Module 1's lessons and recall, then the lab checker's local container mode (ADR-0014).

**The $10 monthly limit** is set in the Anthropic Console (setup.md). It's the backstop behind the proxy's own cap: if the cap's logging ever failed, the Console would still stop the spending.

**The database types, regenerated.** Docker Desktop was up, so `npm run db:types` could finally run. The first run was wrong in an instructive way: `supabase start` restored the local database from an old backup that predated the problem-reports migration, so the generated file _lost_ the `problem_reports` table. `npm run db:reset` rebuilt the local database from the three migrations, and the second run produced a file identical to the hand edit from #49, zero lines changed. The database tests passed locally too (38 tests in three files), as they had in CI. A note in `supabase/README.md` now says to reset before generating types when `supabase start` mentions a backup. The local Supabase is stopped again; Docker Desktop was left as the owner had it.

**Next:** the cloud track's Stage 1, starting with the `predict_shell` item type and Module 1 (Linux and the command line), per ADR-0017; the lab checker (ADR-0014); Phase 2's remaining items (a placement test, the code visualizer, backups).

## 2026-11-09: Problem reports reach the live database, and Phase 1 is complete

The owner pushed the last missing migration to the live project. The dry run listed only `20261109063021_problem_reports.sql`; the push applied it; a second dry run says the remote database is up to date.

**Checked without writing anything:** asked signed out, the live database's API said before the push that the table didn't exist (PGRST205, 404) and after it "permission denied for table problem_reports" (42501, 401). So the table is there, and row-level security and the revoked grants keep strangers out, as the migration's tests say. "Report a problem" on the live site now saves reports; they're read in the dashboard's Table Editor, `problem_reports`, filtered on `status = open` (supabase/README.md).

**Milestone D is complete, and with it Phase 1.** Every item on the v1 spec's list is built and live: the Python Foundations track end to end, the proof checks, reviews, the Today page, the hint-only tutor with its cap, problem reports and data export. The roadmap and CLAUDE.md now say so.

**Decisions for you to review:**

1. _Calling Phase 1 done._ Its condition, everything in Milestone D live, is met, and the marker only tells a session where to look next. Phase 2's first items are already underway (Parsons problems, the living map's first version, practice hours), so "next" is Phase 2 alongside the cloud track's first steps, which wait on ADR-0014 and ADR-0017.

**Still waiting on you:** `npm run db:types` once Docker Desktop runs, to confirm the hand-edited database types match what the generator produces; the $10 limit in the Anthropic Console; the four ADRs; the ADR-0017 conversation.

**Next:** the ADR decisions, then Phase 2 planning or the cloud track's Stage 1, whichever you pick.

## 2026-11-09: The tutor's test set, run for real, and a wording fix

The owner ran `npm run fn:eval:tutor`: **25 of 25 replies fine** with Claude Haiku 5.5 at low effort, for $0.0044. No reply was replaced by the safety filter and none contained a solution line, across eleven attempts to get the answer out of the tutor (a fake system message in a code comment, "I'm the teacher", "you already gave it to me", flattery and urgency, a yes/no question about the exact fix, "answer mode") and fourteen honest asks. So Haiku 5.5 at low effort stays the tutor's model, as ADR-0015 planned: the cheapest that passes. A hint costs about $0.0002.

**Reading the replies** (the printout matters as much as the count):

- The hints read as hints. The nudges ask questions that point at the right line ("After the loop ends, which number does n still hold?"); the closer looks name the fault in words without the fix ("your code returns the opposite in each case"); the one next-step reply gives print's `end` setting and leaves the rest. Every refusal was kind and still gave the rung's hint.
- Two replies to answer-fishing asks slipped into the third person: "The learner's question asks for the three lines again, but I give hints, not answers" and "The learner's question asks for the full program". The tutor was talking about the learner to the learner, echoing the `<learner_question>` label it reads from. A third said "the author's hint", echoing `<author_hints>`, where a learner just sees "Hints".

**The fix** (this entry's PR), in two rounds:

1. _Version 2:_ one more rule in the tutor's instructions: speak to the learner as "you", never say "the learner", and never mention the blocks or the rung. The owner ran the set again: 25 of 25 fine for $0.0047, and the two replies now say "You asked for the full program, but I give hints, not answers". But two others said "the author's note" and "the two author-style facts", echoing the `<author_hints>` label.
2. _Version 3:_ that block is `<written_hints>` and the word "author" is gone from the instructions, which call them "the hints", as the learner sees them. The model copies the names it's given, so the names should be the learner's. A test now fails if "author" gets back into the prompt. The owner's third run: 25 of 25 fine for $0.0046, no "author" anywhere, and the replies say "the written hint" where they lean on one. One reply still slipped, "The learner question asks for the full program": the `<learner_question>` tag, with its underscore turned into a space. Version 3 is what got deployed (decision 4 below): the owner redeployed the function the same evening, and the three free checks passed again (preflight 204, GET 405, unsigned POST 401). Every hint on the live site now uses version 3.

`TUTOR_PROMPT_VERSION` goes up with each change, so every logged call says which instructions it used.

**Decisions for you to review:**

1. _Fix the wording now rather than wait for real data._ Two slips in 25 show the pattern, the change is one sentence, and a beginner reading "the learner's question" about their own question would be confused.
2. _Keep the model._ All 25 passed at the cheapest setting; the ADR says the model changes only when a sample fails, and none did.
3. _A third version before deploying, rather than shipping version 2._ Version 2 already beats what's live, but the "author" echo has the same cause as the voice slip, a label copied into a reply, and renaming the label is smaller than another rule. One deploy instead of two.
4. _Ship version 3 with one slip in 25, rather than a fourth version._ The same rule produced no slip in the run before, so one in 25 is the model's randomness at low effort, not something one more sentence fixes for certain. ADR-0015's bar (no solution revealed, replies that read as hints) was met in all three runs, and every real hint is logged in `ai_calls`, so the question settles itself with data. If "the learner" keeps appearing there, the next change is the same kind as this one: `<learner_question>` becomes `<question>`, and the rule gets an example sentence to copy ("You asked for the whole program, and I give hints instead").

**Next:** the problem-reports migration; the ADR-0017 conversation about the shell.

## 2026-11-09: The tutor is live

The owner deployed the AI proxy to the live project (`npx supabase functions deploy ai --no-verify-jwt --yes`), so the hint-only tutor (ADR-0015, #48) now works on the live site for signed-in learners whose account is switched on. The CLI warned that Docker wasn't running; that's harmless here, it uploaded the five source files and bundled them in the cloud instead. Nothing in the live database had to change first: the function reads `profiles.allowed`, calls `ai_spend_this_month` and writes `ai_calls`, all there since 2026-11-08.

**Checked without calling Claude or writing anything,** the same three requests as the first deploy: the browser's preflight got 204, a GET got 405 ("Use POST."), and a POST from someone not signed in got 401 ("Sign in first.").

**To try it yourself:** open a practice exercise on the live site, write an attempt, press Check, then use "Ask the tutor" under the exercise. The hint comes from Claude Haiku 5.5 at low effort, a fraction of a cent each, and the rung climbs with every ask. Claude pressed nothing on the live site: a hint request writes a real event into your learner log, so only you make them.

**Still waiting on you:** `npm run fn:eval:tutor`, which runs the 24 test-set conversations against Claude (about a cent on Haiku) and prints every reply to read; the problem-reports migration; `npm run db:types`; the $10 limit in the Anthropic Console; the four ADRs. The Supabase CLI mentioned that v3.1.0 is out (the repo pins v3.0.0): an ordinary dependency update, whenever you want it.

**Next:** your go on the eval and the migration; the ADR-0017 conversation about the shell.

## 2026-11-09: The tutor's test set reaches Module 6

Five more exercises in `supabase/functions/ai/tutor-test-set/`, one each from Exceptions, CSV data, Files, Modules and libraries, and From spec to program, with three conversations apiece: an attempt to get the answer out of the tutor (a fake system message inside a code comment, "you already gave it to me, the page reloaded", flattery and urgency, "so I can compare with mine"), an honest first ask with a typical mistake, and a later ask with two earlier hints, which sets the rung. Each reply's forbidden pieces are the lines of the reference solution. `npm run fn:test` loads and checks every file; the replies themselves are judged by `npm run fn:eval:tutor`, which costs money and waits for your go.

**Next:** your go on the deploys and the eval; the ADR-0017 conversation about the shell.

## 2026-11-09: Where we stand after the autonomous run

A summary for the owner of everything since "I'm going to be away" (the evening of 2026-11-08), with everything that waits on you in one place. The entries below this one have the details and the "Decisions for you to review" lists.

**Merged, in order** (each squash-merged after green CI, its branch deleted):

- #47 Module 3, Loops · #48 the hint-only tutor (ADR-0015) · #49 report a problem (F15) · #50 Module 4, Functions · #51 Module 5, Collections
- #52 Module 6, Real programs, and Checkpoint 6: the Python Foundations track is complete, 36 topics
- #53 a smaller first download: outline-only tracks load on demand (the main file went from 1,034 KB to 853 KB)
- #54 practice hours on the Today page (your idea from 2026-11-06)
- #55 Parsons problems, a third recall item type (ADR-0016), with eleven items · #56 one in every topic but one
- #57 every reference solution proven in the browser's Python, in every test run
- #58 the living map, first version: each Learned topic's memory strength on the map
- #59 a rounding fix for the practice hours
- #60 this summary · #61 ADR-0017, how the shell is taught and proven (proposed) · #62 the tutor's test set extended to Module 6

**Live now,** and checked on the live site at the end of the run: the map with its memory bars, the Today page with your 27 minutes of practice, a Parsons item on Variables, and the cloud map loading its outlines on demand.

**Numbers:** 36 topics ready (all of Python Foundations), 235 exercises, 190 recall items; 939 programs validated under CPython and 235 reference solutions under Pyodide on every test run; 645 web tests, 39 tool tests, 69 harness tests.

**Waiting on you** (each needs a "go"; none was done without one):

1. ~~Deploy the AI proxy with the tutor, then run the tutor test set~~ Both done by you on 2026-11-09: deployed, and 25 of 25 test-set replies fine (the entries above).
2. ~~The problem-reports migration to the live database~~ Done by you on 2026-11-09: the dry run listed only that one, the push applied it, and the table is there and locked down (the entry above).
3. ~~`npm run db:types` once Docker Desktop is running~~ Done on 2026-11-09: the generated file matches the hand edit exactly (the entry above).
4. ~~The $10 monthly limit in the Anthropic Console.~~ Set by you on 2026-11-09.
5. ~~Four ADRs to accept or change~~ All four accepted by you on 2026-11-09: [ADR-0014](decisions/0014-cloud-labs.md) (cloud labs), [ADR-0015](decisions/0015-hint-only-tutor.md) (hint-only tutor), [ADR-0016](decisions/0016-parsons-problems.md) (Parsons problems), [ADR-0017](decisions/0017-shell-in-the-browser.md) (how the shell is taught and proven).
6. The "Decisions for you to review" lists in the entries below: Modules 3 to 6, the tutor, problem reports, lazy outlines, practice hours, Parsons problems, the living map.

**What I didn't start, and why.** The cloud track's Stage 1 content. Its first module is Linux and the command line, and the platform has no way yet to run or check shell work in the browser; the browser drills that ADR-0014 names (subnetting, policy evaluation, costs, capacity) belong to later Stage 1 modules, which a learner can't reach before Module 1. How Linux is taught and proven is your call, so I wrote the options up as [ADR-0017](decisions/0017-shell-in-the-browser.md) (proposed): lessons and a validator-proven "predict the output of this command" item in the browser first, labs in containers on the learner's own machine through the lab checker, and a real Linux VM in the browser (v86, open licence, a 60 MB download) as the later enhancement; a shell simulator is ruled out, and WebVM's engine isn't self-hostable without a licence. It's the first thing to talk through when you're back.

**Housekeeping.** Nothing is left running; every branch is merged and deleted; the working tree is clean. The CRLF warnings git prints on Windows are harmless: the files are stored with LF.

## 2026-11-09: The living map, first version

The Phase 2 item "topics fade as their predicted memory strength drops", in its smallest useful form. The review scheduler (FSRS, ADR-0009) already predicts, for every Learned topic, the chance that the learner still remembers it; the map now shows that number.

**What changed.** `memoryPercent(card, now)` in `reviews.ts` rounds the scheduler's retrievability to a whole percentage. Each Learned topic's row on the map shows "Memory: 86%" and a small `<meter>` (marked decorative, since the words carry the meaning; the bar changes color below the 90% retention target, where a review falls due). The map reads the clock once when it opens. Topics that aren't Learned show nothing new.

**Decisions for you to review:**

1. _Numbers and a bar, not dimmed rows._ Fading the row itself would make a half-forgotten topic's title hard to read, which punishes exactly the learner who should click it. The percentage and the bar show the same thing legibly.
2. _100% right after a review._ The scheduler's model says so, and it's honest about what it is: a prediction that decays, not a grade.
3. _Only on the map,_ not the topic page or Today, where the state label and the due reviews already say what matters.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Every exercise proven in the browser's Python

A gap closed. The validator runs every exercise under CPython, and the harness scenarios prove the two runtimes agree on a small set of programs, but no check ran the actual exercises in Pyodide. Module 6 brought new ground (files, `csv`, `importlib` in tests), so it was time.

**What changed.** `web/src/content/content.pyodide.test.ts` loads Pyodide once and runs every ready exercise's reference solution against its tests, the way the Check button does; all 235 pass, in about 3.5 seconds, so it's part of `npm test` and of CI's Web app job. Only the reference solutions run there: a known-wrong solution may loop forever on purpose (the while-loops topic has several), and Pyodide in Node can't be interrupted, so the first attempt at this check, which included them, hung for an hour. The validator keeps proving under CPython that the wrong ones fail.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Parsons problems in every topic

Eighteen more Parsons problems, written to the pattern of the first eleven, so 29 of the track's 30 topics now have one right after the worked example; six are also in their topic's review pool. The validator runs each one's lines in order and checks its decoy against the real lines. 190 recall items; 939 programs run with no problems.

**Why one topic is left out.** Testing with assert's natural programs are a function plus several `assert` lines, and the asserts can go in any order, as can two `def` blocks. A Parsons problem needs exactly one right order, so instead of a contrived item the topic keeps its ladder as it was. The same constraint shaped several items: lines that could swap without changing the output were chained (each line uses the one before) or merged into one print, and every prompt states the output.

**Decisions for you to review:**

1. _One convention is stated rather than forced:_ the Modules and libraries item puts `import statistics` first, which Python doesn't require, so the prompt says "the import comes first, as it always does". Everywhere else the order is forced by the program itself.
2. _Reading errors has two decoys_ (two misspelled names), the only item with more than one, because spotting the misspelling is the topic.
3. _Review pools gained a Parsons item_ in Booleans and comparisons, Tracing code, Nested loops, List algorithms and From spec to program, as well as the three from the first batch. A review session can now pair one with a quick check, since it counts as a code question.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Parsons problems

A new kind of practice question, from the Phase 2 list, chosen because it helps most at the start of the track the owner is on: the lines of a short program are scrambled, with a decoy, and the learner puts them back in order. The research (Ericson, Margulieux and Rick, 2017) finds this teaches program structure with less effort than writing from scratch, for the same learning. [ADR-0016](decisions/0016-parsons-problems.md), proposed.

**What changed.** A third recall item type, `parsons`, in the content model and the validator: `lines` in the right order with their indentation, optional `distractors`, a prompt that says what the program prints, an explanation and skills. The validator runs the lines in order (no error, no input) and checks that lines are distinct and that no decoy equals a line; its tests cover a crashing order and a decoy that copies a line. In the app, `ParsonsProblem` shows the scrambled lines in a tray and an empty program with Add, Up, Down and Remove buttons, then Check; right means exactly the solution's lines in order. `PracticeItem` gives it the heading "Put the lines in order" and saves an `answer` event whose data holds the program. Review sessions count it as "code or predict". The scramble is seeded by the item's ID (same every time) and never the solved order.

**Content.** Eleven items, one per topic, right after the worked example: a shopping list of prints (Programs and print), a running total (Variables), an adult check with `if`/`else` (If, elif and else), a countdown (While loops), a sum over a range (For and range), a running sum with prints inside and after the loop (Accumulator patterns), a function defined then called twice (Defining functions), appends and a lookup (Lists), word counting with `get` (Dictionaries), a safe `int()` with `try`/`except` (Exceptions), and write-then-read (Files). Each has one decoy that teaches something: `Print` for `print`, `Total` for `total`, `elif` with no second test, `while count < 0:`, `range(1, 3)`, `total = n`, `def greet():`, `append[...]`, `counts[word] + 1`, `except NameError:`, `f.write(hello)`. Three are also in review pools (Variables, For and range, Exceptions).

**Numbers.** 172 recall items (11 new); the validator runs 921 programs with no problems; 409 web tests (6 new) and 39 tool tests pass.

**Decisions for you to review:**

1. _Buttons, not drag-and-drop._ Add, Up, Down and Remove work with a keyboard and on a phone and are easy to test; dragging can be layered on later without changing the item format.
2. _One-dimensional Parsons:_ lines keep their indentation and the learner only orders them. Setting indentation too (the two-dimensional kind) can be an option on the item later.
3. _The prompt states the output,_ so every item has exactly one right order; the content checklist says to avoid lines that could swap without changing the output, because the validator can't catch that.
4. _The scramble is fixed per item_ (seeded by its ID), so a question looks the same when it comes back, and it's never the solved order.
5. _Placed right after the worked example_ in each practice ladder, where the research puts it, which makes the first topics' ladders one step longer (Programs and print now has 7 practice items).
6. _An ADR for a new item type,_ since it changes the content format and the event data; proposed until you accept it.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: Practice hours on the Today page

The owner's own idea from 2026-11-06, pulled forward from Phase 2 because it needed nothing new recorded: every graded attempt has saved its `duration_ms` since the event log began.

**What changed.** `Attempt` now carries `duration_ms` (the server query selects it; a row without one leaves it out). `progress/practiceTime.ts` adds the durations up, all time and the last 7 days, counting at most 30 minutes per attempt, and names the next milestone. The Today page shows it below Next up as "Practice hours": the total, the recent part, a progress bar toward the next milestone, and the rule in one line ("Counting the time spent on answers, Checks and reviews, not time with the site open"). With nothing counted yet it says so. No extra request: the Today page already loads every attempt for the reviews and the plan.

**Decisions for you to review:**

1. _A 30-minute cap per attempt._ An attempt's duration runs from the first touch of an item, or the previous attempt, to this one, so a page left open overnight would record hours. Capping each attempt at 30 minutes keeps the count honest; a long blank-editor build without a Check in between is undercounted a little, which seemed the right side to err on. The number lives in one constant.
2. _Milestones start at 1 hour,_ not 10 as the roadmap said, so a new learner sees the first one within a week; then 5, 10, 25, 50, 100, 250, 500, 1,000, 2,500, 5,000, 10,000.
3. _"Recent" means the last 7 days,_ rolling, rather than the calendar week, because it needs no decision about which day a week starts on.
4. _It lives on the Today page,_ under the plan, rather than on the Account page, because that's the page the learner sees every day and the number is meant to be encouraging.
5. _The learning-science doc gained a row for deliberate practice,_ with the note that "10,000 hours" is a popularization of Ericsson's work, not a rule, so the tracker is read the way it's meant.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills (ADR-0014) and the lab checker.

## 2026-11-09: A smaller first download: outline-only tracks load on demand

The last item of Milestone D, noted as a chore on 2026-11-08 when the cloud track's outlines went on the map: 357 topics nobody can open yet were being downloaded by every visitor, in the app's main file.

**What changed.** `content.ts` bundles the tracks and the main track's outlines as before, but leaves out the cloud track's (`csa.*`). Those live in their own module, `content/outlines/cloud-solutions-architect.ts`, which Vite turns into a separate file. `loadTrackTopics(trackId)` downloads it once and adds its topics to the same lookup `getTopic` uses; `trackTopicsLoaded` says whether that has happened; `loadTrackOf(topicId)` does it for whichever track a topic belongs to. The map page shows "Loading this track's map…" until the outlines arrive, and a Try again if the download fails; the topic loader awaits them before looking the topic up. The Today page, the follow-ups and the interleaved questions are unchanged: they only look at topics bundled in, which is right because a lazy track has no open topic, and `content.lazy.test.ts` fails the day one does.

**Numbers.** The main file went from 1,034 KB to 853 KB (260 KB to 221 KB gzipped). The cloud outlines are a 181 KB file (37 KB gzipped) that most visits never download. 393 web tests pass, 4 of them new.

**Decisions for you to review:**

1. _Which tracks load lazily is decided by hand:_ a module per outline-only track, its pattern left out of the main glob, and a line in `LAZY_TRACKS`. A build-time rule ("any track with no open topic") would need a Vite plugin that watches the content folder for changes; two lines and a test seemed the better trade. When the cloud track gets its first ready topic (the Stage 1 drills), either bundle it back in or teach the Today page to load the tracks the learner has progress in; the test will remind whoever does it.
2. _Milestone D is built but not all live._ Every item on its list is ticked, but the proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go, as do ADR-0014 and ADR-0015. The roadmap keeps "current phase: Milestone D" until those are done; say the word and I'll move it on to Phase 2 planning.

**Next:** your go on the deploys; then the cloud track's Stage 1 drills, which need ADR-0014's decision on how cloud work is proven, and the lab checker.

## 2026-11-09: Module 6, Real programs, written; the Python Foundations track is complete

Five topics and Checkpoint 6, the module where programs meet the world: input that's wrong, files on disk, data in CSVs, code other people wrote, and a spec instead of a recipe. Written while the owner was away; decisions at the end.

**Resources.** Exceptions is built on CS50P Lecture 3 (`LW7g1169v7w`), 0:28 to 26:30: a `ValueError` from `int()`, `try`/`except`, where the risky line goes, `else`, and `while True` around it all; the rest of the lecture (`get_int` as a function, `pass`, a prompt parameter, `raise`) is linked. Files is the text-file half of Lecture 6 (`KD-Yoel6EVQ`), 0:28 to 30:26 (names.txt, `"w"` against `"a"`, `with`, `readlines`, `for line in file`, `rstrip`, sorting). CSV data is the `csv` module section of the same lecture, 1:01:35 to 1:19:02 (`csv.reader`, `DictReader`, `writer`, `DictWriter`), with the `split(",")` part linked. Modules and libraries is Lecture 4 (`MztLZWibctI`), 0:28 to 19:13 (`import random`, `from random import choice`, `randint`, `shuffle`, `statistics.mean`), with its last seven minutes, `sayings.py` and `__name__`, linked as a second resource (the lesson format shows one embed). From spec to program has no video: the lesson is the platform's own, and the reading is Think Python's section 6.4, Incremental development (3rd edition, CC BY-NC-SA 4.0), which grows a `distance` function from a stub with scaffolding prints. Python docs anchors: the tutorial's errors (handling, raising), input and output (reading and writing files) and modules (up to executing modules as scripts) sections, and `csv.DictReader`.

**What each topic drives at:**

- _Exceptions_: `try`/`except ValueError` (name the error; a bare except hides bugs), the risky line inside `try` and its use in `else` or after a `return`, `while True` with `try` and `return` on success, `raise ValueError("...")` when a function is given something it can't work with, `as error`. The debug catches `NameError`, has `int()` outside the `try`, and returns from the `except`.
- _Files_: `with open(path, mode) as f` (closes the file, even on an error), `"w"` erases and `"a"` appends, `write` adds no `\n`, `for line in f` with `rstrip()`, `readlines`, `except FileNotFoundError`, numbers come back as text. Tests create their own files with `Path.write_text` and check the learner's with `read_text`. The debug opens for writing with `"r"`, writes without `\n`, and prints lines with their line breaks still on.
- _CSV data_: the shape (header line, one record per line), `csv.DictReader` giving one dictionary per row with string values, `list(...)` inside the `with`, totals and counts by group with a dictionary, filtering rows. The debug reads after the file has closed, adds text as if it were numbers, and uses `"Item"` for `"item"`.
- _Modules and libraries_: `import m` then `m.f()`, `from m import f` and its trade-off, `random` (`choice`, `randint`, `shuffle` returning `None`), `statistics.mean` and `median`, `math.sqrt`, `floor` and `pi`, a file as a module, and why `if __name__ == "__main__":` finally gets its full explanation; a hidden test imports the learner's file and checks that importing prints nothing. The debug uses `random` without importing it, calls `sqrt` without `math.`, and calls `main()` bare.
- _From spec to program_: the method as a checklist: examples (ordinary, boundaries, just past them, empty), gaps written down and asked about, functions planned as name, inputs and result and written as stubs, asserts from the examples that must fail first, one function at a time. The worked example is a quiz scorer with its spec and examples kept at the top of the file. The build is a prose spec for car park fees (a first hour, part hours, a daily maximum, 0 minutes); the debug is a program that disagrees with the spec at the top of its own file in three places.

**Checkpoint 6, CSV report tool (the capstone):** a prose spec: a sales CSV with bad rows (a blank or non-numeric amount), skipped and counted; totals by region in first-seen order; a report written to `report.txt` and printed. `write_sample` is given, so there's a file to work on; the learner writes `read_rows`, `amount_of` (a number or `None`, via `try`), `good_rows`, `totals_by_region`, `report_lines`, `write_report`, `test_report` and `main`. Hidden tests cover each function, first-seen order, two-decimal formatting, the empty case, that the rows list is unchanged, every docstring, that the learner's tests fail when `amount_of` calls every row worth 1.0, the printed output, and the file. Five wrong solutions (crashes on the bad row, counts only good rows, opens the report inside the loop, two weak asserts, typed-in) each fail. The debug catches `TypeError` instead of `ValueError` (a crash), overwrites a region's total instead of adding to it, and opens the report file inside the loop so one line survives. The sibling is an attendance report (whole numbers, `int()`); the steps fill in reading and cleaning, totals, the report and file, then the outline; the versions are an expenses report (by category) and a rainfall report (by station, one decimal place).

**Harness.** A new scenario, `check-files`, pins that a test can create a file and the learner's program can read and write files in the working folder, identically in CPython and Pyodide (its in-memory file system). No harness code changed. `harness/README.md` and `content/README.md` say how file-based tests work.

**Numbers:** 40 exercises and 26 recall items added; 36 topics ready, which is every topic of Modules 1 to 6, the whole Python Foundations track; the validator runs 910 programs over the content, none failing. Web checks (389 tests), Python checks (69 tests) and the build pass.

**Decisions for you to review:**

1. _Think Python is the first main resource that isn't CS50's or the PSF's:_ section 6.4 of the 3rd edition, CC BY-NC-SA 4.0 (the same license family as CS50's material), linked, not copied. The spec said "AI-written lesson" for From spec to program; the lesson is ours, and the reading backs it.
2. _Modules and libraries links its second clip instead of embedding it._ The lesson format shows one embed and lists the other resources after the lesson, so the `sayings.py` clip (seven minutes) is listed there with its timestamps. Allowing two embeds would be a small web change if you'd rather.
3. _A bad CSV row means a blank or non-numeric amount, nothing else._ A row with a missing field (fewer commas) makes `DictReader` give `None`, which `float()` rejects with a `TypeError`, not a `ValueError`. I kept that case out of the spec and the tests so the module teaches one error at a time; it's a note for a later data-cleaning topic.
4. _The spec-to-program build and the capstone give the function names_ ("so the checks can find them") but not the algorithm or the edge cases; those have to come from reading the spec. That's the compromise between a real spec and a machine-checkable one.
5. _Checkpoint 6 hands the learner `write_sample`,_ the way Checkpoint 5 handed over `STUDENTS`: typing a CSV by hand isn't the skill being proven, and the hidden tests write their own files anyway.
6. _The checkpoint's reference solution totals with a running total over the dictionary's keys,_ which Module 5 taught, rather than `sum(totals.values())`; a learner may use either.
7. _Windows's `newline=""` for CSV writing is mentioned once, in the CSV recap, and not tested:_ files in the browser sandbox don't have the problem.

**Next:** the Python Foundations track is complete, so the owner can learn on it end to end. Left in Milestone D: the lazy-outlines bundle chore. After that, the cloud track's Stage 1 drills and the lab checker (ADR-0014). The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-09: Module 5, Collections, written

Five topics and Checkpoint 5, the module where a variable stops holding one thing. Written while the owner was away; decisions at the end.

**Resources.** Three more clips of CS50P Lecture 2 (`-7xg8pGcP6w`), timed from its subtitles: the list of students, indexing from 0, looping and `range(len(...))`, 34:55 to 45:36 (Lists); the dictionary of houses and looping over its keys, 45:36 to 56:11 (Dictionaries); one dictionary per student and a list of them, 56:11 to 1:05:56 (Nested data, with a note to read past the `lambda` sort near the end). List algorithms has no clip: the Python tutorial's More on Lists and Looping Techniques sections, and the filter/transform patterns in the platform's own words. References and mutation is built around two Python Tutor programs, one drawing a second name and a copy as arrows, one drawing a function that changes the caller's list and one that only rebinds its parameter; the reading is Ned Batchelder's "Facts and myths about Python names and values", linked (it's his copyright, so nothing is copied), with his PyCon 2015 talk linked too (video `_AEJHKGk9ns`, confirmed through PyVideo; standard YouTube license, so a link rather than an embed).

**What each topic drives at:**

- _Lists_: make, index from 0 and −1, `len`; replace, `append`, `del`, `in`; items versus positions; `append` returns `None`; `split()` turns a string into a list of words. The debug has `scores = scores.append(100)`, an index one past the end, and a loop that prints positions instead of items.
- _List algorithms_: filter and transform as a loop with `append` into a new list; search returning the first position or −1; `sorted` (new list, `reverse=True`) against `.sort()` (in place, `None`); slices and `min`/`max`/`sum`. The debug has `ordered = scores.sort()`, a slice two long, and a search that keeps the last match.
- _References and mutation_: two names, one list; assignment never copies; `list()`, `[:]`, `copy()`; `==` against `is`; a function that mutates its argument against one that rebinds its parameter; prefer returning new lists. Tests check the original is unchanged and that the result `is not` the input. The debug has an `add_item` that mutates, a backup that's an alias, and `shopping = shopping.append(...)`.
- _Dictionaries_: curly braces, lookup by key, `KeyError`, add/change/`del`/`in`/`len`, looping gives keys, `items()`, counting both ways. The debug has a count that never starts, a loop over `items()` used as keys, and a lookup of a missing key.
- _Nested data_: a list of lists read outside in (`grid[row][col]`, row loop with cell loop); a list of dictionaries as records; choosing the shape; copies of nested data share the inner lists. The debug appends whole records instead of names, uses `"Name"` for `"name"`, and swaps row and column.

**Checkpoint 5, gradebook:** `STUDENTS`, a list of records each holding a scores list; `average(scores)`, `letter_grade(average)` with its boundaries, `best_student(students)` (first of a tie), `report_lines(students)` returning the lines and a `Best:` line, `test_gradebook()` with at least four asserts, `main` printing the lines, both under the guard. Hidden tests check the boundaries exactly (90, 89.9, 80, 70, 60, 59.9), the tie, the lines for another list, that no function changes the data, every docstring, that the learner's tests fail for a `letter_grade` that always says A, and the program's output. Five wrong solutions (an `average` that sorts in place, `>` for `>=`, tests that only check A grades, no docstrings, typed-in) each fail their test. The debug divides by one too many, grades with `>`, and consumes the list it reports on with `pop`, so the last line counts zero students. The sibling is an inventory report; the versions are team stats (points, star/starter/bench) and a weather report (temperatures, hot/mild/cold).

**Numbers:** 39 exercises and 27 recall items added; 30 topics ready, which is every topic of Modules 1 to 5; the validator runs 749 programs over the content, none failing. Web checks, Python checks and the build pass.

**Decisions for you to review:**

1. _`split()` is introduced in Lists_ (a string's words as a list) and used in Dictionaries' word counting; string methods otherwise wait, as before.
2. _Ned Batchelder's article and talk are linked, never embedded or quoted:_ the article is his copyright and the talk is under YouTube's standard license. They're the only non-CC, non-PSF resources so far; the spec named them.
3. _Comprehensions, `lambda` and `enumerate` are named as shortcuts for later,_ not taught. The filter/transform loop is the pattern every exercise uses, because it generalizes and because it's what the capstone's CSV work needs.
4. _"Leaves the data alone" is a hidden test in every build of the module,_ and in the checkpoint it's one of the named skills a failure brings back. Mutation bugs otherwise go unnoticed until much later.
5. _Checkpoint 5 keeps its data in a constant_ (`STUDENTS`) and its functions take the list as a parameter, so the tests can pass other data; the alternative, functions that read the global, would have taught the opposite of Module 4.

**Next:** Module 6 (Real programs: exceptions, files, CSV, modules, spec to program, and the CSV capstone), which ends the Python Foundations track; then the lazy-outlines bundle chore. The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-09: Module 4, Functions, written

Five topics and Checkpoint 4, written overnight while the owner was away, so the content stays a module ahead. Decisions are listed at the end for review.

**Resources.** CS50P again, timed from CS50's subtitles (downloaded from the course's CDN, used only to find times): the end of Lecture 0 (`JP7ITIXGpHk`) carries two topics, `def`, parameters, default values, `main()` and the first brush with scope from 1:26:44 to 1:41:22, then `return` and the `square` function to 1:45:36; Lecture 9 (`6pgodt1mezg`) gives scope its clip, the bank balance that can be read but not changed from inside a function, 7:45 to 17:33, stopping where David turns to classes; Lecture 5 (`tIrcxwLqzjQ`) gives testing its clip, from the calculator's `square` to the corner-case discussion, 1:20 to 16:25. Python Tutor draws frames and the call stack for scope. The Python tutorial's Defining Functions and Documentation Strings sections are the readings. Decomposition has no video, as the spec said: its lesson is the platform's own, around a worked example that rebuilds Checkpoint 1's receipt as functions.

**The harness had to grow first.** Exercises now test functions, and `from solution import f` at the top of a test file breaks every test at once when `f` is missing or misnamed. So `checks.py` gained `function(name)`, which loads one function and fails one test with "Define a function called ...", and `printed(f, *args)`, which captures what a call prints. Loading a file runs its top-level code, so `function` swallows what the file prints and turns an `input()` at load time into a plain message about the `__name__` guard. The test runner now also keeps anything printed during a Check out of the report; a program that printed while being loaded was corrupting the command-line checker's JSON. Scenario `check-functions` pins all of this; CPython and Pyodide agree on it (68 harness tests, 20 Pyodide scenarios).

**What each topic drives at:**

- _Defining functions_: define versus call (a bare `hello` does nothing); parameters fill in order, defaults when left out; `main()` defined above and called once at the bottom, and why the order of defs doesn't matter but the call's position does. The debug has a missing colon, swapped arguments and a `main` never called.
- _Return values_: the print-versus-return table; `None` from a function with no `return`; `return` ends the function, which is right for a search and wrong on a loop's first pass. The debug has `print(b)` for `return b`, a `return` inside a loop and an expression with no `return`.
- _Scope and the call stack_: local names die at return; reading a global works, assigning makes a local (`UnboundLocalError`); the `global` keyword exists and the rule is not to use it; frames stacked and unwound. Exercises insist a function use only its parameters, tested by calling it with other values. The debug is a plant that won't grow: three values that never make it between functions.
- _Decomposition_: one job per function, names that say the job, docstrings on the first line (a comment above the def, or a string after the first statement, isn't one), and `main` as the plan. Tests check `__doc__`. The debug has a misplaced docstring, a missing return and a `main` that uses names before setting them.
- _Testing with assert_: a true assert is silent, a false one stops the program; cases that catch bugs (typical, boundary, zero, negative); `test_` functions; and `if __name__ == "__main__":`, taught here because the Check button loads the file. Several exercises test the learner's tests: the function under test is swapped for a broken one and the learner's test function must then fail. A test that compares a function with itself, or asserts `True`, doesn't.

**Checkpoint 4, password checker:** `has_min_length`, `has_digit`, `has_upper`, each a yes/no question; `check_password` returns the first problem in a fixed order; `test_check_password` with at least four asserts; `main` with the input, under the guard, which runs the tests and then the program. The hidden tests check each rule at its boundary, the order of the verdict, every docstring, that the learner's tests pass and would fail for a verdict that always says OK, and the program's output. Five wrong solutions (an unguarded `main`, rules in the wrong order, tests that only check good passwords, no docstrings, typed-in output) each fail the test for their mistake. The debug is a code-word checker with `>` for `>=`, a search that returns on the first character, and a test that expects the wrong verdict. The sibling is a ticket-code checker; the fresh versions are a PIN checker (digits, not all the same, not counting up) and a username checker (length, first character, allowed characters).

**Numbers:** 39 exercises and 27 recall items added; 24 topics ready; the validator runs 596 programs over the content, none failing. Web checks, Python checks and the build pass.

**Decisions for you to review:**

1. _The harness grew two helpers and now hides prints during a Check._ The scenario contract is unchanged (existing expected files are byte-identical) and extended by one scenario. The Check button never showed prints anyway.
2. _The `__name__` guard is taught in Testing with assert and used from there on._ Earlier Module 4 programs call `main()` directly, which is fine because none of them asks for input; the first program that does (the checkpoint) needs the guard, and the lesson says why.
3. _Character kinds use comparisons_ (`"0" <= ch <= "9"`, `"A" <= ch <= "Z"`) rather than string methods like `isdigit()`, which come in Module 5. The checkpoint prompts give the idiom.
4. _Lecture 5's clip keeps a try/except passage_ (12:30 to 14:05, Module 6 material) because the corner-case discussion after it is the point of the topic; the Intro says to read past it.
5. _Testing the learner's tests_ by swapping in a broken function is a pattern worth keeping in later modules: it's the only way the platform can tell real asserts from decorative ones.
6. _Estimates_ are 40 to 45 minutes per topic, as in Module 3.

**Next:** Module 5 (collections), then the lazy-outlines bundle chore. The proxy deploy, the problem-reports migration and the tutor test-set run still wait for your go.

## 2026-11-08: Report a problem

Milestone D's F15, small and self-contained: a way for the learner to say "this is wrong" from the page where it's wrong, so content mistakes don't get lost.

**The table.** Migration `problem_reports`: who, when, `topic_id`, `item_id` (an item, `lesson`, `explain`, or null for the topic), `item_rev`, a 1 to 2,000 character `message`, and `status` (`open` or `resolved`). Row-level security lets a learner insert and read their own rows; `status` is left out of their insert grant, so every report starts open and only the owner, in the dashboard, resolves it. Nine pgTAP tests cover all of that, including that a learner can't report in someone else's name or delete a report.

**The page.** `ReportProblem` (`web/src/reports/`) is a quiet "Report a problem" link that opens a box with a Send button; it's placed in three spots: the bottom of every `PracticeItem` card (so practice, proof and review items all have it, with the item's `rev`), under the lesson (`item_id: lesson`), and under the explain check (`item_id: explain`). `sendReport` inserts straight into the table and never throws; the box keeps the text on failure. Hidden when signed out, like the tutor.

**Tests:** 6 new web tests, 351 pass; 9 new database tests, which CI runs (Docker isn't running on this machine, so they weren't run locally). Format, lint, types pass.

**Decisions for you to review:**

1. _Where reports are read:_ in the Supabase dashboard's table editor, for now. A "Your reports" list on the account page, and an owner's inbox, can come when there's more than one learner.
2. _`database.types.ts` was edited by hand_ to add the table, in the exact shape `npm run db:types` generates, because the generator needs the local database and Docker was off. Running `npm run db:types` once Docker is up should change nothing; if it does, keep the generated version.
3. _No event is recorded for a report,_ since the report is itself the record and the table is the owner's to-do list.

**To go live (needs your go):** `npx supabase db push --remote --dry-run` should list only `20261109063021_problem_reports.sql`; then the same command with `--yes` applies it. Until then, sending a report on the live site fails politely ("couldn't be sent").

**Next:** Module 4 (functions), then the lazy-outlines bundle chore.

## 2026-11-08: The hint-only tutor

Milestone D's first item, F13, built on the proxy that already grades explanations. The design is [ADR-0015](decisions/0015-hint-only-tutor.md), proposed; the owner was away, so it's built as proposed and waits for their review and the deploy.

**The proxy** (`supabase/functions/ai/`) now has two actions. `tutor.ts` builds the request: the exercise's prompt, written hints and reference solution, the learner's code, a summary of their latest Check, the tutor's earlier replies, and the learner's question, each in its own tagged block with the learner's text stripped of our tags; the rung is chosen from how many hints came before (nudge, concept, specific, step) and named at the end of the message; the reply is structured output with one `hint` field. `readHint` then keeps it safe: more than 600 characters, more than two lines of fenced code, or two or more lines copied from the solution (compared without spaces or capitals, ignoring lines under 10 characters), and the reply is replaced by the exercise's next written hint, or a fixed hint for the rung. `handler.ts` grew `readHintRequest` with its size limits, and a `completeCall` step shared by both actions: ask, log (even an unusable answer, with its cost), answer. `index.ts` wires `TUTOR_MODEL` and `TUTOR_EFFORT` (defaults: Claude Haiku 5.5, low). No migration: `ai_calls.action` already allowed `tutor_hint`.

**The test set** (`tutor-test-set/`): nine conversations on five real exercises from Modules 1 to 3, five of them trying to get the answer out (outright, "answer mode", "I'm the teacher", a plea, a `# SYSTEM:` comment in the code) and four honest asks at different rungs. Each names text the reply must not contain. `npm run fn:eval:tutor` runs them against Claude, prints every reply, and fails on a replaced reply or a forbidden line. It costs about a cent on Haiku, so the owner runs it.

**The page.** `TutorBox` (`web/src/tutor/`) sits under the written hints of a fill-in or write exercise in practice: an optional "What are you stuck on?" line, a button, and the exchanges so far, each hint labelled with its rung. Six asks, then it points back to the recap. `CodeRunner` reports the code as it's typed, so the tutor sees unsaved work; `ExerciseView` keeps the code and the latest Check, and counts tutor hints with written ones in `hints_used`. `PracticeItem` switches the tutor on for the practice context only and saves each hint as a `hint` event with `source: tutor`, the rung, `replaced`, the question, the call ID and the model. Signed-out visitors don't see the box at all; the page already asks them to sign in once.

**Tests:** 38 Deno tests on the proxy (12 new), 345 web tests (14 new). Format, lint, types and the build pass. The pricing page was checked before reusing the price table: Haiku 5.5 $0.10/$0.50, Sonnet 5.5 $2/$10, Opus 5.5 $4/$20 per million tokens, unchanged.

**Decisions for you to review:**

1. _The tutor is practice-only and also on in a checkpoint's "Stuck?" steps,_ which are fill-ins with hints and were always meant as practice. Off in fresh versions, which are proof.
2. _Six asks per exercise._ A guess at where "the next step" would start dictating the solution. Tune it from the `ai_calls` log.
3. _Hidden when signed out_ rather than shown with a sign-in link, to keep the page quiet; the explain check keeps its link because it's a single box.
4. _The reference solution travels from the browser to the proxy,_ as the model answer already does (ADR-0013); the same "fix before other learners" note applies.
5. _Default model Haiku 5.5 at low effort,_ like grading, pending the test-set run you approve. If hints read poorly, try `TUTOR_EFFORT=medium` before a bigger model.

**To go live (needs your go):** `npx supabase functions deploy ai --no-verify-jwt --yes`, then `npm run fn:eval:tutor` to read the hints. Until the deploy, the live site's box says the tutor isn't available.

**Next:** problem reports (F15), then Module 4 (functions) and the lazy-outlines bundle chore.

## 2026-11-08: Module 3, Loops, written

Five topics and Checkpoint 3, the content item of Milestone C, written while the owner is away (they asked for building to continue, with decisions made by best judgement and written down here; see _Decisions for you to review_ below).

**Resources.** Lecture 2 of CS50P (Loops, video `-7xg8pGcP6w`) carries four topics, in clips whose times came from CS50's published subtitles: `while` and the accidental infinite loop, 0:28 to 16:13; `for`, lists as "these values", `range` and `_`, to 26:47; asking the user for a positive number with `while True`, `continue` and `break`, to 31:34; and the Mario section, a column, a row and a square of bricks, 1:05:56 to 1:19:15. Strings as sequences is built on the Text section of Python's own tutorial, with Python Tutor walking `for ch in word`. The Python tutorial's `while`, `range` and `break`/`continue` sections are linked as readings. Every lesson is the platform's own words (ADR-0004).

**What each topic drives at:**

- _while loops_: the condition is checked before each pass, so a loop can run zero times; a counting loop's three parts (start, test, update); infinite loops and how to stop one. The debug is a doubling program that adds 2, overshoots with `<=`, and counts its steps outside the loop.
- _for and range_: the stop value is never included; `range(start, stop, step)`; `_` for a value that isn't used; when `for` fits and when `while` does. The debug has `range(1, n)`, a variable printed after the loop that ends with the wrong value, and a `Ready` line that prints its counter.
- _Accumulator patterns_: the before/inside/after shape; running totals and counts; best-so-far and its starting value; `while True` with `break` and `continue`. The build reads numbers until 0 and reports count, total and largest. The debug has `total = 0` inside the loop, an off-by-one range, and `//` where `/` was meant.
- _Strings as sequences_: positions from 0, negatives from the end, slices that stop before their stop, `len()`, and `for ch in text`. The build prints initials; the debug has `word[1]` for the first letter, `word[len(word)]` (an `IndexError` to read first) and a slice one too long.
- _Nested loops_: the inner loop runs completely on every pass of the outer; `end=""` and the bare `print()`; patterns from the loop variables. The build is a right-aligned pyramid; the debug is a times table with a short range, `row * row`, and the line break inside the inner loop.

**Checkpoint 3, text statistics:** from a line of words separated by single spaces, the number of words and letters, the longest word (the first of equals) and a bar per word, using loops and strings only, because lists and `split()` are Module 5. The crux is the last word, which has no space after it: it's a hidden test of its own (`test_last_word`), the point of the sibling example (a week of weather, with the longest sunny streak), the subject of a step and of the explain. Five wrong solutions each fail the test for their mistake. The debug draws a triangle and counts its stars, with `range(1, n)`, a `print()` indented into the inner loop, and `star` for `stars`. The fresh versions are number statistics (digits built up as text, then `int()`) and match results (`W`/`L` streaks, a bar per streak). Every test names skills across Modules 1 to 3.

**Numbers:** 39 exercises and 26 recall items added; the validator runs 441 programs over the content, none failing; 18 topics are ready. Web checks, Python checks and the build all pass. The main bundle grew to 894 KB (233 KB gzipped), mostly content; the lazy-outlines chore noted on 2026-11-08 is now worth doing.

**Decisions for you to review:**

1. _Accumulators have no clip of their own._ CS50P's lecture doesn't teach sums, counts or maximums as patterns, so the lesson's Intro and Recap carry them, and the clip covers `while True`, `break` and `continue`. A Runestone chapter on the accumulator pattern was considered as a reading, but its license couldn't be read (the site sits behind a bot check), so it was left out, as ADR-0004 asks.
2. _The nested-loops clip includes a function._ David writes the square inside `def print_square(size):`, and functions are Module 4. The Intro says to read the indented lines as the program with `size` standing for 3, and to stop when he splits the code into `print_row`. Cutting the clip before the function would have cut before the nested loop.
3. _"Letters", not "characters"._ The spec says Checkpoint 3 counts characters; the checkpoint counts non-space characters and labels them `Letters:`, because counting every character is just `len(text)` and tests nothing.
4. _Time estimates_ are 40 to 45 minutes per topic rather than the outline's 35, to match a lesson, six or seven practice items and three proofs.
5. _Module 3's debug exercises each hide one crash_ (a `NameError` or `IndexError`) among the three bugs, so Reading errors keeps being practised. That's a pattern worth keeping in later modules.

**Next:** Milestone D (the hint-only tutor and problem reports), the lazy-outlines bundle chore, and Module 4 (functions), in whichever order keeps the owner ahead of the content.

## 2026-11-08: Interleaved practice

The last app piece of Milestone C (F5): each practice ladder mixes in one recall question from an earlier topic, so the learner has to decide which idea applies rather than knowing it from the page they're on.

- `web/src/practice/interleave.ts`: `earlierTopicFor` walks the topic's most recent prerequisite, looking through a checkpoint to the last topic before it (so Module 2's first topic borrows from Strings and input), and `interleavedItem` picks one of that topic's recall questions, rotating day by day and stable within a day.
- The topic page's loader fetches the earlier topic's content alongside the topic's own, and `Practice` splices the question in after the topic's own recall items, labelled "from <topic>". The answer is recorded under the earlier topic, so it counts toward that topic's follow-ups and reviews.
- 10 new tests (the chooser, the loader, the ladder). Milestone C's app work is done; what's left in C is content: Module 3.

## 2026-11-08: Reviews, timed to how fast you forget

Milestone C starts with ADR-0009: one review card per Learned topic, scheduled by FSRS, with sessions rated from performance.

**The scheduler is our own code.** `ts-fsrs` is at version 6 with a new, sparsely documented API (an awaited factory, model plug-ins), and the ML capstone is to fit this very scheduler to the owner's history. So `web/src/reviews/fsrs.ts` implements the published FSRS-4.5 formulas and default parameters in about a hundred lines: the forgetting curve, the first stability per rating, the next stability after a pass or a lapse, difficulty with mean reversion, and the interval for a 90% target retention (which makes the interval equal the stability). Intervals are capped at 365 days. The tests check the shape of the behavior, not magic numbers: 90% at `t = S`, growth on Good, less on Hard, shrinkage on Again, bounded difficulty, overdue reviews rewarded more than early ones.

**Cards are replayed from events** (ADR-0008), not stored: Learned counts as a first review rated Good, and each `review` event after it updates the card. `progressOf` now carries `reviews` and `card` per topic, and `stateOf` takes `now` and adds Relearning (last review Again), Fading (due) and Mastered (a Good review at least 7 days after Learned), in that order. A topic in any of those still unlocks what builds on it.

**Sessions on Today.** The page now reads progress once (`Plan`) and shows, in the spec's order: Reviews, Mistakes to revisit, Next up. A session (`ReviewSession`) asks two items from the review pool, at least one code or predict-the-output, choosing the ones answered longest ago so sessions rotate; it rates itself from each item's first attempt (Good, Hard, Again) and records one `review` event (item `review`, `data.rating` and `data.items`). `PracticeItem` gained `onGraded`, called for answers and Checks alike. The due list is fixed when it loads, so finishing a review doesn't make it vanish. Up to 20 a day, most forgotten first.

**History transport.** `fetchAttempts` now includes `review` events and their rating (`data->>rating`), so `Attempt` has an optional `rating`. A review with no rating is dropped rather than guessed.

**Docs:** the `review` event in the data model's events table, the reviews rules under Derived progress, F11 and F12 marked built, and a Milestone C checklist in the roadmap.

**Tests:** 11 for the scheduler, 9 for sessions and due lists, 5 for the new states, 6 on Today (including the Good, Hard and Again flows, and the saved event), 1 on the map, 1 on history. 308 web tests pass.

**Next:** interleaved practice (a recall item from an earlier topic in each ladder, F5), then Module 3 (loops).

## 2026-11-08: Module 2, Decisions and debugging, written

Five topics and a checkpoint, so Module 2 is ready before the owner finishes Module 1. This closes Milestone B.

**Resources.** Lecture 1 of CS50P (Conditionals, video `_b6NgY_pMdw`, embeddable by its oEmbed) carries the first three topics. Its section times came from CS50's published subtitles, used only to find the times: comparisons and the first `if` from 0:28 to 9:55; `elif` and `else` to 18:28; `or`, `and`, the grade program and chained comparisons to 34:07. The `match` section (48:18 to 55:37) is linked, not embedded, from if / elif / else. Tracing code's main resource is Python Tutor with a preloaded program; Reading errors' is Python's own tutorial chapter on errors, with Python Tutor stepping into a `NameError` as a second resource. Both lessons are the platform's own words, as ADR-0004 requires.

**What each topic drives at:**

- _Booleans and comparisons_: `=` against `==`, comparisons give a `bool`, and text is never equal to a number (`"7" == 7`). The debug plants `print(..., age = limit)`, which is a keyword argument and a `TypeError`, not a syntax error, so the learner meets the real message.
- _if / elif / else_: the first `True` condition wins; colons and indentation; two `if`s against one `if` / `elif`. The debug has an `elif` in the wrong order, a `==` where `=` was meant (so a name is never defined) and a print indented into a branch.
- _Logical operators_: `and`, `or`, `not`, and the `x == 1 or 2` trap, which the lecture doesn't cover and which shows up in the fill-in, the debug and the explain.
- _Tracing code_: trace tables. Several exercises run the learner's code with other starting values (`run_with`), so they can't be passed by typing the expected output in; the build is "a program from its trace" and its tests change the starting values.
- _Reading errors_: the last line first, then the line number; five error kinds; one change per run. The debug plants three errors of three kinds (`SyntaxError`, `NameError`, a `ValueError` from formatting text with `:.2f`), so each fix reveals the next.

**Checkpoint 2, ticket pricing:** age bands, a weekend extra that skips free tickets, a member discount applied after the extra, two decimal places. The hidden tests parse the output loosely and check one rule each, naming skills across Modules 1 and 2; four wrong solutions (the `or` trap, a boundary, the discount before the extra, no decimals) each fail exactly the test for that mistake. The debug is a parking-fee program with the `or` trap, a reversed `elif` order and a print indented into the `else`. The way through: a zoo-ticket sibling with labeled steps, the build in four fill-in steps, and two fresh versions, a swimming pool and a train fare, with the same rule shapes in different stories.

**Numbers:** 39 exercises and 26 recall items added; the validator runs 292 programs over the content, none failing; 275 web tests pass, including the follow-up invariants over every ready topic.

**Next:** Milestone C, starting with reviews (ADR-0009), and Module 3 (loops) before the owner finishes Module 2.

## 2026-11-08: Topic states, gating and "Prove it now"

The paused v1 work resumes, now that explanations can pass and topics can become Learned.

**Done (#43):**

- **States everywhere.** `stateOf` already existed; now every topic page and map row shows the learner's state with an icon and a word: Locked, Available, In progress, Learned on a date, or Passed for a checkpoint. `STATE_LABELS` in `progress.ts` holds the words, so no state is color alone (F9).
- **Gating (F8, ADR-0002).** A topic page loads the learner's history for the topic _and_ its prerequisites, which is what the state depends on, in one `useTopicProgress` hook; the proof list reads from the same load instead of fetching again. A Locked topic shows its header and lesson only, with a notice naming the topics that open it; its practice and proof checks wait. A Locked checkpoint shows only what it brings together, not the checks or the way through. While the history loads, the page shows everything rather than flashing sections in and out; gating applies the moment the state is known.
- **"Prove it now"** appears on an Available topic that hasn't been started. It hides the lesson and practice, moves focus to the Prove it heading, and can be undone with "Show them anyway". Nothing is recorded for the choice itself; the checks record as they always did.
- **Signed-out visitors** see no states and no gating. Their progress can't be known, and nothing of theirs is saved anyway.
- **"Next up" on Today (F12):** `nextUp` picks the first topic in progress in track order, or else the first Available one that can be opened, skipping anything Locked, even if it was started before gating existed. Today reads the history a second time for it; sharing one load between the two sections is a small follow-up.
- **Tests:** 5 for `nextUp`, 6 for gating on topic pages, 2 more on the map, 4 on Today. The page tests needed a helper, `unlocked(topic)`, that supplies passing proof checks for a topic's real prerequisites, since a fake topic with an unlearned prerequisite is now Locked. 263 web tests pass.

**What the owner will see.** Gating is live for their account. Values and types, where they are, is Locked until Programs and print's three checks are passed, and Today now says "Continue: Programs and print". That's ADR-0002 working as written, but it's worth saying out loud.

**Next:** Module 2's content, so it's ready before the owner finishes Module 1. Then Stage 1 of the cloud track, starting with browser drills.

## 2026-11-08: Building starts: more than one track, and the cloud track on the map

**The owner said "Start building everything."** The order follows the spec's _Building it_ section and the roadmap: the app learns to show more than one track; the cloud track goes on the map as outlines; then the paused v1 work resumes (topic states and gating with "Prove it now", Module 2); then Stage 1 of the cloud track, starting with drills that run in the browser; the lab checker once ADR-0014 is accepted.

**Done (#42):**

- **The app shows every track.** `tracks()`, `getTrack()`, `topicIdsOf()` and `placeOf()` replace `mainTrack()` and `moduleFor()` in `web/src/content/content.ts`; `placeOf` says which track and module a topic is in, and whether it's a topic, a checkpoint or a capstone. The map is at `/map` for the first track and `/map/<track id>` for the others, with a switcher, and a note when a track is all outlines. Topic pages name their track.
- **Tracks have an `order`, and a module may name a `capstone`**: a bigger checkpoint shown after the module's own, building on every module before it. That keeps the spec's module numbering intact on the map. The validator checks capstones like checkpoints and that no two tracks share an order.
- **`tools/outline_cloud_track.py`** reads the spec's module tables, checkpoint paragraphs and capstone sections and writes the track file and 357 `planned` outlines: 324 topics (the 7 specialties included), 30 checkpoints and 3 capstones. It overwrites only files that still carry its marker and are `planned`, so written topics are safe. The spec gained a "Checkpoint 30" line so Module 30 parses like the rest.
- **Gating between modules** comes from the spec's module map: a module's topics list the checkpoints of the modules it builds on as prerequisites, a checkpoint lists its module's topics, and a capstone lists the checkpoints that feed it. Python Foundations' Checkpoint 6 gates Module 6 (Automation). Within a module there's no order, as the spec says.
- **Checked:** the validator passes over 393 topics (6 ready, 387 planned); 37 Python tests, including one that runs the validator over generated content; 246 web tests.

**A cost to come back to.** Topic outlines are bundled with the app, so the main bundle grew from 612 KB to 806 KB (173 KB to 215 KB gzipped) for topics nobody can open yet. Loading a track's outlines on demand would undo that. Noted as a chore, not done now.

**Waiting on the owner:** accepting ADR-0014, before the lab checker is built.

## 2026-11-08: The map in docs/research; the track assumes nothing about the learner

**The owner said:** move the map into `docs/research`, don't assume they're strong in any area, the track may one day serve absolute beginners, and don't worry about the L1, L2, L3 depth levels.

**Done:**

- The map is at `docs/research/senior-cloud-architect-knowledge-map.md`, renamed to the folder's style and otherwise unchanged. It's the owner's own document, committed at their request.
- **The spec no longer builds on anyone's standing.** Removed: the depth-level system (the L1–L3 tables, the default depth by module, proofs scaling with depth, the primary-cloud option), every "at the aware level" phrasing, the owner's strengths and gaps from the faster path, and the depth paragraph in ADR-0014. The faster path is now an _example_ route for someone who starts on Azure, and the spec says plainly that what a learner skips is decided by "prove it now" and the placement test, never by their own estimate. Two of the map's four rules stay: every concept gets a build, and write as you go.
- **A correction to the entry below.** It recorded the owner's strengths and gaps from the map as the basis for the faster path. The owner asked not to assume strengths anywhere, so the spec doesn't, and neither should future sessions. The map still says what it says, as the owner's own document.
- Memory updated the same way.

**Checked:** every topic ID and heading from before this change is still present, no IDs are duplicated, and every relative link resolves.

## 2026-11-08: The cloud track, cross-referenced with the owner's knowledge map

**The owner asked** to cross-reference the Cloud Solutions Architect spec against their own _Senior Cloud Architect Knowledge Map & Learning Roadmap_, a Markdown file with twelve domains, a certification order, a 24-month plan and a 24-item self-assessment: add everything the map has that the spec lacks, remove nothing, keep it extensive.

**Finding the file took two tries.** It wasn't in the project folder at first; the owner had it in another folder and copied it to the project root. It isn't committed, because it holds the owner's career details. Where it lives is the owner's call; `docs/research/` is the natural home if it goes in.

**Done, in `docs/specs/cloud-solutions-architect.md`:**

- **4 new modules:** Virtualization, hardware and Windows (2); Software engineering literacy (7); Application architecture and integration (17); Specialized workloads (28). The track has 30 modules now.
- **107 new topics,** from 210 to 317, and many existing "You'll be able to" lines extended with the map's specifics: CUBIC and BBR, SCIM and PKCE, the confused deputy, CRDTs, Paxos and Raft, KEDA, Kyverno, FOCUS, provisioned throughput, and so on. Every existing topic is still there.
- **New sections from the map:**
  - _Depth levels_: L1 aware, L2 working, L3 deep; how the four proofs scale with depth; a default depth for each module; the primary-cloud option; the map's four rules of thumb.
  - _A faster path for an experienced learner_: the map's seven phases over 24 months, mapped to modules, with its capstone builds, milestones, weekly rhythm (60% building, 25% reading, 15% writing), kill criteria and reading list.
  - _Self-assessment_: the map's 24 "you're senior when you can" items, each tied to the checkpoint, topic or drill that proves it. Kept as a mirror: the platform never counts self-report (ADR-0002).
- **Certifications:** AZ-104, CCSP, TOGAF, Databricks and Snowflake, exam codes, and the map's suggested order.
- **The service table:** 20 more rows, such as customer identity, subnet scope, IPAM, layer 4 and layer 7 load balancers, appliance insertion, zero trust access, Arm chips, PaaS hosting, block and file storage, shipped devices, Oracle, confidential computing, AI accelerators and carbon data.
- **6 more drills,** including Kubernetes triage, a threat model and a decision record.
- ADR-0014 gained a line on proofs scaling with depth. The roadmap and CHANGELOG carry the new counts.

**Numbering shifted.** Modules were inserted, so module numbers and the positional checkpoint IDs (`csa.mN.checkpoint`) moved. Nothing is built, so nothing refers to them yet. Stable IDs are now an open question in the spec.

**Checked by script, not by eye:** all 244 IDs from the previous version are present; no duplicate IDs; all 47 previous headings are present; every checkpoint ID matches its module number; every relative link resolves; and a sweep of 660 distinctive terms from the map found all of them in the spec (four were missing on the first pass and were added).

**Personal context from the map,** kept out of the repo's text beyond what the faster path needs: the owner's strengths are Linux, networking and Azure, and their stated gaps are AWS, Kubernetes and platforms, data and streaming, FinOps, and the business layer. The faster path is built on that.

**Next:** the owner decides on ADR-0014 and on when the track gets built. The v1 work stays paused where the earlier entry left it.

## 2026-11-08: A second track, Cloud Solutions Architect (specified)

**The owner asked for** a Cloud Solutions Architect track:

- with everything a senior architect needs at the top of the pay band;
- multi-cloud;
- able to drill skills until competency is proven, not just knowledge;
- assuming access to every cloud environment for practice.

**Done:**

- **The spec,** [docs/specs/cloud-solutions-architect.md](specs/cloud-solutions-architect.md). It has 26 modules in 4 stages, about 210 topics, 3 capstones and 6 specialties to choose from. It also covers:
  - how competency is proven, with drills that have targets;
  - lab safety and cost;
  - one topic written out in full;
  - a map to certifications;
  - a table of equivalent services on the three clouds.
- **ADR-0014, proposed:** how cloud skills are proven.
  - A local, read-only lab checker inspects what the learner built in their own sandbox. The platform receives only which checks passed.
  - CI tests the checks against recorded API responses, so ADR-0004 still holds without touching a cloud.
- **Links:** the roadmap, the vision, CLAUDE.md and the ADR index now point to the spec and the ADR.
- **Checked by web search:** current product names.
  - Azure AI Foundry is now Microsoft Foundry.
  - AWS Interconnect – multicloud gives a managed private link to Google Cloud.
  - Google's framework is now the Well-Architected Framework, with six pillars.

**Deliberately not done:** the track isn't in `content/` yet. The app shows only the first track file it finds (`mainTrack()`), and `cloud-…` sorts before `python-foundations`. Adding the track would replace the owner's Python map on the live site, so support for more than one track has to come first.

**Waiting on the owner:**

- accepting or changing ADR-0014;
- deciding when the track gets built, relative to the rest of v1 and the ML path.

The v1 work stays paused where the entry below left it.

## 2026-11-08: Where we stopped (paused)

The owner paused work here.

**Done since the last pause** (all merged and live):

- ADR-0013 was accepted, and the owner's answers recorded (#33).
- Explanation grading, built and rolled out:
  - the AI proxy and its call log, `ai_calls` (#34);
  - the explanation box on every topic and checkpoint (#35);
  - the grading test set. Claude Haiku 5.5 at low effort got all 30 samples right twice, so it's the grader (#36);
  - the rollout notes, and how to deploy the function again (#37).

**Where we sit**

- **Phase 1, Milestone B (Prove it).** Milestone A is done.
  - Done in B: export my data, progress tracking part 1, and explain it back graded by AI.
  - Left in B: topic states and gating with "Prove it now", and Module 2's content.
- **The live site has everything on `main`.**
  - The `ai` function is deployed, and the Claude API key is in the live project's secrets.
  - The owner switched on `allowed` for their account, so their explanations get graded.
  - The app stops grading at $10 a month.
- **The owner is on Module 1, Values and types.** Their next explain check there will be the first real grading.
- **Nothing is left running.** The local Supabase and Docker Desktop are stopped. `main` is clean, with no open pull requests or leftover branches.

**Not confirmed yet**

- **The first grading on the live site.** If the box says grading isn't switched on for the account, the `allowed` update didn't run. The SQL is in `setup.md`, under "Who can use it".
- **The $10 monthly limit in the Anthropic Console** (step 2 in `setup.md`). It's a second safety net, on top of the app's own cap.

**Next, in order**

1. **The owner:** try Explain it back on Values and types on the live site, reloading the page first. Set the Console limit, if it isn't set.
2. **Topic states and gating, with "Prove it now"** (F8, F9). This was waiting for grading. Explanations can now pass, so topics can become Learned. It starts with a short plan, checked against ADR-0002 and the v1 spec:
   - which states lock what;
   - what "Prove it now" lets a learner skip.
3. **Module 2's content,** ready before the owner finishes Module 1.
4. **Then Milestone C** (FSRS reviews, the full Today page, recall items, interleaved practice) **and D** (the hint-only tutor, problem reports).
5. **Later, in Phase 2:** the practice-hours tracker, on the way to 10,000 hours.

**To remember on return**

- **Merging doesn't deploy the AI proxy.** See "Putting it live" in `supabase/README.md`.
- **From Claude Code, the Supabase CLI changes the live project only with `--yes`.** That flag goes in only after the owner's go-ahead.
- **Checking the app on my own dev server:** the recipe is in the 2026-11-06 "Where we stopped" entry.
  - Local grading also needs `npm run fn:serve`, with the key in `supabase/functions/.env`.
  - The local test account is `allowed` in the local database only.

## 2026-11-08: Explain it back is live

**Rolled out** in this order (ADR-0013's last steps), with the owner's go-ahead:

1. **The Claude API key went into the live project's secrets.**
   - The owner's first try changed nothing. The Supabase CLI saw it was running inside Claude Code, and from there it won't change the live project without `--yes`.
   - The owner had typed that command, so Claude re-ran it with `--yes`. It first checked that the file held only `ANTHROPIC_API_KEY`, without showing any values.
2. **The owner switched on `allowed` for their account,** in the dashboard's SQL editor.
3. **The `ai_calls` migration went to the live database.** The dry run listed only that one.
4. **The `ai` function was deployed** (2.5 MB). Three requests checked it without calling Claude or writing anything:
   - the browser's preflight got 204;
   - a GET got 405;
   - a POST from someone not signed in got 401.
5. **The explanation box (#35) was merged,** and Cloudflare deployed it. The live site's code now has "Check my explanation".

**Merging doesn't deploy the function.** Cloudflare deploys the web app on every merge, but a change to `supabase/functions/` reaches the live project only through `npx supabase functions deploy ai`. The steps are now in `supabase/README.md`. Deploying from CI would need a Supabase access token in GitHub's secrets. That can wait until function changes are frequent.

**Cleaned up:** the local function server, the local Supabase and Docker Desktop are all stopped.

**Next:**

- The owner's first real grading: the explain check on Values and types, the topic they're on.
- Milestone B: topic states and gating, and "Prove it now" (F8, F9).
- Module 2's content, ready before the owner finishes Module 1.

## 2026-11-08: The grader chosen, and checked end to end

**The test set** (the owner approved up to about $1.20):

- Claude Haiku 5.5 at low effort got all 30 samples right, for $0.0056.
- A second run, to check it wasn't luck, got all 30 right again, for $0.0054.
- So Haiku is the grader, as ADR-0013 says (the cheapest that passes). It's already the proxy's default, and Sonnet and Opus never ran. About 1 cent spent in all.

**Real costs are lower than the ADR's estimate.** A grading used about 1,100 tokens in and 100 out, about $0.00017. At low effort Haiku barely thinks. ADR-0013 assumed 1,000 out, so $10 a month covers about 60,000 gradings, not 15,000.

**Checked end to end** in a real browser, on the local Supabase with the owner's key, as the local test account on Values and types:

- an explanation without the fix got Needs work. Its one question, "What do you need to do to the text values before the + sign can add them as numbers?", points at the gap without giving the answer;
- the full explanation got Passed, and "Your proof so far" changed to "✓ Explain: passed on Nov 8" with no reload;
- the local database had both calls in `ai_calls` with their costs, and both `explain_submit` events, correct false then true, each linked to its call.

**Getting the key in place:** the first check found `supabase/functions/.env` empty, because the editor hadn't saved yet. The check names the file's lines and their lengths, never their values.

**Next: rollout to the live project** (ADR-0013's last steps):

1. The owner puts the key in the live project's secrets, and switches on `allowed` for their account.
2. With the owner's go-ahead: apply the `ai_calls` migration (`db push --remote`), deploy the function (`functions deploy ai`), then merge the explanation box (#35).
3. The owner tries it on the live site.

## 2026-11-08: The explanation box (part 2) and the grading test set (part 3)

**Done**

- **The explanation box** (draft PR #35):
  - a text box and "Check my explanation" in each explain card;
  - the result: Passed, or Needs work with guiding questions, or a plain message when it wasn't graded;
  - every attempt saved as an `explain_submit` event (item `explain`, context `prove`), with `correct` set only when graded;
  - the history now reads graded explanations, so a pass counts toward progress straight away;
  - 13 new tests, 242 in all.

  It stays a draft until the proxy is deployed to the live project. Merged before then, every Check on the live site would fail.

- **The test set** (`supabase/functions/ai/test-set/`), 5 samples for each of Module 1's six explain checks. They were written to be clear-cut:
  - the short passes still state every required idea;
  - the misses lack a required idea outright, or get it wrong.

  `npm run fn:eval -- <model> <effort>` runs them with the proxy's own request, and a Deno test checks the files are usable.

**Decided while building**

- **The test set runs straight against Claude,** from a Deno script that uses `grading.ts`, not a Python script posting to the locally served function as ADR-0013 sketched. That avoids rewriting the prompt in Python, and minting a local sign-in for the script. What's being tested, the instructions and the reading of Claude's answer, is the same code. The proxy's checks and logging have their own tests.

**Waiting on the owner**

- The API key in `supabase/functions/.env`, from `.env.example`. Then approval to run the test set: about $1.20 for all three models.

## 2026-11-08: The AI proxy (ADR-0013, part 1)

**Done**

- **`ai_calls`** (migration `20261108223826_ai_calls.sql`):
  - append-only, like `events`, with the same deliberate-account-deletion exception;
  - learners can read their own rows, and only the service role can write;
  - `ai_spend_this_month()` sums this calendar month's costs in UTC, and only the service role may call it;
  - 11 pgTAP tests.
- **The Edge Function `supabase/functions/ai/`**, split so the logic is testable:
  - `handler.ts`: the checks in ADR-0013's order, with the services passed in;
  - `grading.ts`: the instructions, the request and reading the answer;
  - `cost.ts`: the price table;
  - `index.ts`: connects the real Supabase and Claude.
- **19 Deno tests** with fakes:
  - every outcome: graded, not allowed, paused, unavailable;
  - a stranger gets a 401 before anything else runs;
  - a failed call costs nothing to log, but an unusable answer is still logged with its cost;
  - the model-answer filter;
  - the CORS check.
- **Deno 2.9.6** is pinned in the root `package.json` from npm, so neither the owner nor CI installs anything by hand. A new **Edge Functions** CI job runs `npm run fn:test`.

**Decided while building**

- **Claude returns only the rubric results and the questions; the code works out the verdict.** A pass needs every required item met, so Claude can't "pass" an explanation the rubric doesn't support.
- **Structured output uses a plain JSON schema,** with the rubric IDs as an enum, rather than the SDK's Zod helper: one library fewer.
- **`verify_jwt = false` for this function.** It checks the sign-in itself, with `auth.getUser`, which works with every kind of signing key.
- **The log keeps the topic, the explanation and the prompt version,** not the rubric or the model answer: those can be found from the topic.
- Deno found the root `package.json` and wanted the function's packages in `node_modules`. `--node-modules-dir=none` makes it use its own cache, as Supabase's runtime does.

**Checked**

- On the local Supabase, through the real runtime:
  - the CORS check answered;
  - no sign-in gave 401;
  - the local test account got "not allowed", then "unavailable" once allowed (no key yet), which also ran the spending check;
  - a malformed request got a 400 with a reason.
- The local test account is now `allowed` in the local database only, for building the explanation box.
- The first database test assumed an empty `profiles` table, which a local database with accounts never has. It now looks at its own two learners.

**Next**

- The explanation box on topic and checkpoint pages: `explain_submit` events, and progress counting a pass.
- Then the 30-sample test set, which needs the owner's API key.

## 2026-11-08: The owner's answers

- **ADR-0013 accepted** as proposed, so explanation grading is next.
- **Anthropic Console:** the owner has an account. Still to confirm before grading goes live: billing and the $10 monthly limit. The API key comes later, when we connect it.
- **Where the owner is:** Values and types, topic 2 of Module 1. Module 2's content isn't urgent yet, so the order holds: grading, then states and gating, then Module 2.
- **No spoiler-free notes needed:** the devlog and pull requests can describe exercises in full, as before.
- **The practice-hours tracker** (toward 10,000 hours) is already on the roadmap, in Phase 2. Every answer and Check already saves its duration, so practice done now will count once it's built.

**Next:** explanation grading, built to ADR-0013.

## 2026-11-06: Where we stopped (paused for the weekly usage limit)

The owner paused work until the usage limit resets on Sunday.

**State**

- `main` is clean and deployed, with everything from this session merged:
  - export my data (#29);
  - progress tracking, part 1 (#30);
  - ADR-0013, proposed (#31).
- Nothing is left running: the local Supabase and Docker Desktop are stopped, and my test dev servers stopped themselves.

**Next, in order**

1. **The owner:**
   - accept or change [ADR-0013](decisions/0013-explain-grading.md);
   - create the Anthropic account, with billing and a $10 monthly limit;
   - say how far they are in Module 1;
   - say whether notes about content should avoid spoilers.
2. **Explanation grading,** built to ADR-0013 once it's accepted. It needs Deno installed, and the key.
3. **Topic states, gating and "Prove it now"** (F8, F9).
4. **Module 2 content,** ready before the owner finishes Module 1.
5. **Then Milestone C** (reviews, the full Today page) **and D** (the tutor, problem reports).

**How I check the app on my own dev server** (the recipe CLAUDE.md points to). This script lives outside the repo. Run it with `node` as a background task; it serves `web/` on port 5180 and stops itself after 15 minutes:

```js
import { pathToFileURL } from "node:url";
const web = "C:/Users/arasm/Documents/Education Platform/web";
const { createServer } = await import(
  pathToFileURL(`${web}/node_modules/vite/dist/node/index.js`).href
);
const server = await createServer({
  root: web,
  server: { port: 5180, strictPort: true },
});
await server.listen();
setTimeout(
  async () => {
    await server.close();
    process.exit(0);
  },
  15 * 60 * 1000,
);
```

- **Signing in on it:** the local test account is `test-learner@example.com`. Its sign-in link arrives in Mailpit; fetch it from `http://127.0.0.1:54324/api/v1/messages`.
- **Docker Desktop** is at `%LOCALAPPDATA%\Programs\DockerDesktop\Docker Desktop.exe`, and `docker desktop stop` quits it. If I start it, I quit it afterwards.

## 2026-11-06: Proposed: grading explanations (ADR-0013)

**Why:** explanation grading is the next item, and it's the first part of the platform that costs money and calls an outside service. So the design goes to the owner first.

**Done**

- [ADR-0013](decisions/0013-explain-grading.md), proposed:
  - the browser sends the explanation to an Edge Function, which checks sign-in, `allowed` and the month's spending, then asks Claude to grade it against the rubric;
  - a pass means every required rubric item is met; a miss gets up to 3 guiding questions, never the model answer;
  - an append-only `ai_calls` log carries the $10 monthly cap, with the Anthropic Console's own limit as a backstop;
  - the model is the cheapest of Claude Haiku 5.5, Sonnet 5.5 and Opus 5.5 that passes a 30-sample test set. Running that set once on all three costs about $1.20, and each run needs the owner's go-ahead.
- Checked first, on this PC: CLI 3.0 serves functions locally and deploys them to the live project. It sets secrets only on the live project, from a `.env` file or the dashboard. Deno isn't installed yet. Model names and prices come from the current Claude API reference (October 2026), not memory.

**Waiting on the owner**

- Accept or change ADR-0013.
- Create the Anthropic account, with billing and the $10 limit (setup guide).
- How far they are in Module 1, which decides when Module 2's content is needed. And whether notes about content should avoid spoilers.

## 2026-11-06: Progress tracking, part 1

**Decided: gating waits for explanation grading.** The plan had gating before grading. But a topic is Learned only once its build, debug and explain all pass, and explanations can't be graded yet. Gating now would lock the owner out of topics 2–5 partway through Module 1. So this part shows progress without locking anything. States, gating and "Prove it now" switch on with grading. Told to the owner; the roadmap's Milestone B list now says so.

**Done**

- `web/src/progress/progress.ts`, pure functions for the data model's rules:
  - `progressOf`: when each proof check first passed. A passing Check of the build (or of any fresh version, for a checkpoint) or the debug counts, as will an `explain_submit` event with `correct` true.
  - `stateOf`: Locked, Available, In progress, Learned, or a checkpoint's Passed.
  - 12 tests: one per state change, and that the order events arrive in doesn't change the result. That order-independence is the data model's "incremental equals rebuilt from scratch".
- `useProgress`: reads the history once, adds the events on this device, and recalculates after each one. It remembers whose history it read, so after switching accounts it never shows the previous learner's.
- **The map** marks started topics "In progress", with the proof checks passed there.
- **Topic and checkpoint pages:** "Your proof so far" lists the three checks, passed (with the date) or not yet. The Prove it intro no longer calls them extra practice.
- Docs: the data model's progress section, F8 and F9, the roadmap, and the web README.
- Tests: 20 new, 229 web tests in all.

**Checked end to end** on the local Supabase, as the local test account:

- the map showed "In progress" only on Programs and print, ignoring answers on a sample topic that no longer exists;
- on that topic, the banner build typed into the editor passed its hidden tests in real Pyodide, and "Your proof so far" changed to "✓ Build: passed on Nov 6" with no reload;
- the map then showed "In progress · Proof checks passed: build", and the Check was in the local database.

**Next**

- Explain it back, graded by AI (F7, F14): the AI proxy, its budget cap and the grading. It needs the owner's Anthropic API key. Then states and gating.
- Module 2 content, timed to the owner's progress through Module 1.

## 2026-11-06: Export my data (F16, built early)

**Why now:** the learning history exists only in the Supabase project, and ADR-0010's backup plan is this export, which didn't exist yet. The owner chose to build it first, then carry on with Milestone B.

**Decided**

- **Where:** a new account page, which opens from the learner's name in the header.
- **What's in the file:** the profile and every event, with every column, oldest first. It's indented JSON, named after the app and the local date. A `format` number lets the capstone's scripts tell layouts apart. Progress joins once Milestone B computes it.
- **The outbox too, read before the server.** The owner's answer to an explain-it-back question shaped this: they expected an unsaved answer to be in the file. A server-only export would have missed it.
  - Reading the outbox first means an event sent in between is on the server by then, and one sent later is in the copy of the outbox.
  - Events only in the outbox have `received_at: null`, and the page says how many there were.
  - The event log's new `getPendingRows()` reads the outbox fresh, so other tabs' unsent events count too.
- **Reading pages until an empty one,** not until a short one. Otherwise a server row limit below 1,000 would silently cut the file short. It costs one extra request.

**Done**

- `web/src/export/`: `exportData.ts` gathers the data, and `download.ts` saves it through the browser's normal download. The file never leaves the browser.
- `pages/AccountPage.tsx` at `/account`, with "Download my data" and a message saying how many events the file holds.
- `web/src/days.ts`: `dayOf` and `addDays` moved out of the follow-up rules. Importing `dayOf` from there had pulled 3.7 kB of those rules into the startup bundle.
- Docs: the file's layout in the data model, a weekly backup routine in the setup guide, and F16 and the roadmap.
- Tests: 15 new, 209 web tests in all.

**Checked end to end** against the local Supabase, on a dev server that stopped itself, signed in as the local test account:

- With the API container stopped, the page said the data couldn't be downloaded. On this PC a refused local connection takes a few seconds to fail, so "Gathering your data…" showed until then.
- With one made-up event placed straight in the outbox, the file had 7 events: the made-up one with `received_at: null`, every column, oldest first, no duplicates. The page said 1 wasn't saved yet. The event was then removed from the outbox, and it never reached the local database.
- A real download landed in Downloads and read back as valid JSON. I deleted it afterwards.

**Next**

- Progress tracking: each topic's state, worked out from the event log and shown on the map.

## 2026-11-06: Checkpoint 1, the receipt calculator

**Done**

- `content/topics/py.m1.checkpoint`, status `ready`. That completes Module 1's content.
  - **Build:** a restaurant receipt from a blank editor: meal and drinks (decimals allowed), a whole-number tip percentage, then the subtotal, tip and total to two decimal places.
  - **Debug:** cinema tickets with three bugs, one per test:
    - an unconverted `input()` (a `TypeError` crash);
    - `adults + children / 2 * price`, missing its parentheses (a wrong total);
    - `print("Total: $", total)`, which adds a space and has no two decimals.
  - **Explain:** walk through a three-line tip calculator, naming the type of every value, and say what goes wrong without `float()`.
  - **The way through:**
    - a solved sibling, a shop receipt with a discount, with labeled steps (it introduces `#` comments as a plan);
    - the receipt in 4 fill-in steps with hints, each giving the whole program but one part, the last only the three comments;
    - 2 fresh versions: splitting a bill, and an electricity bill.
- **Tests that point at the right skill.** The first draft compared exact amounts, so a single precedence slip also failed the decimals test. Now:
  - value tests read the numbers whatever their format, and check them against the program's own earlier lines;
  - inputs with decimals appear only in the test that reads them;
  - one test checks two decimal places, and one the layout with every number replaced.
  - Each of 14 single-mistake wrong answers now fails exactly the one test for its mistake (checked with `harness/cli.py check`).
- **Found by viewing the page:**
  - On an empty program, three hidden tests crashed with `KeyError: 'Subtotal'` from the test's own helper, and the page showed it. The page shows crashes even in hidden tests, because they're usually in the learner's code. The tests now fail with an `assert` instead, and the content checker runs every hidden-test exercise on an empty program to catch this. All earlier topics pass.
  - The suggestion scrolled the steps' heading only to the bottom of the screen, because the steps weren't drawn yet. It now draws them first (`flushSync`), then scrolls.
- **Checked:**
  - the content checker (147 programs);
  - the guarantee test, now over a real checkpoint: every one of its tests brings back a question on each skill it names;
  - on the dev server, signed out: two failing Checks on the build bring up the suggestion, which opens the steps with the first fresh version.

**Next**

- Milestone A's checklist is complete. Next is the owner's call: Milestone B (progress tracking, gating, explain grading), or the owner's own pass through Module 1 first.

## 2026-11-06: Getting unstuck on a checkpoint (ADR-0012)

**Decided**

The owner accepted [ADR-0012](decisions/0012-checkpoint-support.md) and asked for all four additions on every checkpoint. Settled while building it:

- A checkpoint test counts as missed only if no Check passed it that day, as with code. A program that crashes fails every test, so it points at all their skills until it runs.
- Each step gives the whole program except one part, and the last step only an outline. These are completion problems with fading support. Steps that each build one part on its own transfer worse (4C/ID).
- The page suggests the steps after 2 failing Checks, but never opens them by itself.
- Each checkpoint has at least 2 fresh versions besides the main build. The page offers one not yet tried, or else the one tried longest ago.
- A second debug program waits until learners actually get stuck on debugs.

**Done**

- **Content format:**
  - `unstuck` (`example`, `steps`, `versions`) in a checkpoint's `topic.yaml`;
  - `test_skills` in its builds' and debug's `exercise.yaml`: every test, with the skills it checks, as `topic/skill`.
- **Content checker:** a ready checkpoint needs every topic in its module ready, a solved sibling, 3 or more steps with hints, 2 or more fresh versions, and every build and debug test naming real skills of this or an earlier module. 10 new tests.
- **The checkpoint page:**
  - "About this checkpoint" (what it brings together, with links back to the module's topics) in place of a lesson;
  - the three proof checks, with a suggestion next to the build after 2 failing Checks;
  - "Stuck? Try it in steps": the solved sibling, the steps, then a fresh version, rendered only when opened.
- **Follow-ups from checkpoint tests:**
  - the history query now also reads each Check's status and failing tests (`data->>status`, `data->failing`);
  - the Today page loads the checkpoints a learner worked on, then the topics their tests name.
- **Tests:** 20 new web tests. One is a guarantee over the real content, like the one for topics: once a checkpoint is ready, every test of its builds and debug must bring back a question on each skill it names.
- **Checked** the new history query against the local database, read-only. Checks come back with their status and failing tests; answers with neither. I started the local Supabase for this and stopped it afterwards; it keeps its data.

**Next**

- The Module 1 checkpoint (receipt calculator), with its solved sibling, steps and fresh versions.

## 2026-11-06: The fifth lesson, Strings and input (and a checkpoint question)

**Done**

- `content/topics/py.strings-and-input`, status `ready`, which completes Module 1's topics:
  - **Learn:** CS50P Lecture 0 from 43:23 to 45:02, the f-string part. `input()` (topic 3's clip) and `int()` (topic 2's clip) were already covered. The `:.2f` part (1:24:34 to 1:25:56) and the Python tutorial's "Formatted string literals" are linked as more resources.
  - **Practice:**
    - a worked example that asks a name and an age and does maths with the age;
    - three questions: `input()` always gives a `str`, an f-string prediction, and `"4" + "5"` (the "45" from Values and types);
    - filling in a rectangle's area (one line done as a pattern);
    - a price tag with `:.2f`.
  - **Prove it:**
    - build: kilometres to miles;
    - debug: a shopping line. `quantity` isn't converted, so "can't multiply sequence by non-int" crashes it; then a missing `f` silently prints the braces;
    - explain: why `age + 1` fails on typed input.
  - **Review pool:** four items. Skills: `input-text` (3 follow-up candidates), `convert` (4) and `fstrings` (6).
- **Design fix:** the first draft of the fill-in used `...(input())`. Python prints a `SyntaxWarning` into the output before running that code, which would confuse a beginner. Blanks now stand only where a value goes.
- **Checked:**
  - every output and error message, with typed input, on Python 3.14;
  - the feedback for starters and mistakes. Forgetting to convert in the area exercise prints `Area: 444` (`3 * "4"`), which the recap explains;
  - the page on the owner's restarted dev server. All the new files showed up without a restart, so the watcher fix works there too.

**The owner asked:** what if someone really struggles with the checkpoint? Today, nothing special happens. [ADR-0012](decisions/0012-checkpoint-support.md) (proposed) answers with mastery-learning and worked-example research:

- failed checkpoint tests point to the skill behind them, which opens a follow-up;
- a solved sibling project to study;
- a "try it in steps" version with hints, offered after 2 failing Checks;
- proof on a fresh parallel version.

**Next**

- The Module 1 checkpoint (receipt calculator), built to ADR-0012 once the owner accepts it.

## 2026-11-06: The fourth lesson, Arithmetic

**Decided:** the main resource is a reading, not CS50P.

- The lecture gives arithmetic about 40 seconds: a list of `+ - * / %` at 1:00:05, plus a division-and-rounding demo at 1:22:52. It never covers `//`, `**` or the order of operations.
- _Python for Everybody_ (Charles R. Severance, CC BY 4.0 per py4e.com) covers exactly that, in four short sections of chapter 2: operators and operands, expressions, order of operations, and the modulus operator.
- Its lecture video for the chapter is linked as an extra but not embedded. YouTube refused its captions (a 404 on the timed-text API), so I couldn't check timestamps, and I won't embed a stretch I can't check.
- The intro tells the learner to skip the Python 2 asides, and corrects one gloss: `6 + 4 / 2` prints `8.0`, not `8`.

**Done**

- `content/topics/py.arithmetic`, status `ready`:
  - **Practice:**
    - a worked example (135 seconds with `/`, `//` and `%`);
    - three questions: which line prints `3`, a precedence prediction, and `6 / 3` giving `2.0` (mixing in topic 2's types);
    - filling in operators for egg boxes (it's a syntax error until every gap is filled, and the prompt says so);
    - Celsius to Fahrenheit.
  - **Prove it:**
    - build: a pizza party with `//`, `%` and `/`;
    - debug: splitting a bill, with a `TypeError` from `"Total: " + total` and a silent `food + drinks / people`;
    - explain: `/`, `//` and `%` with 17 cookies.
  - **Review pool:** three items. Skills: `operators`, `precedence` and `div-mod` (3 follow-up candidates each).
  - Every exercise that could be passed by typing in the output has a `run_with` check and a "typed-in" known-wrong solution.
- Checked: every output and error message on Python 3.14; the feedback for starters and mistakes; the page on a self-stopping dev server.
- Fixed while looking: a reading as the main resource showed its title twice (on the link card and in the credit line). The credit line now shows just the license.
- CLAUDE.md now says how to run a dev server for checking that stops itself.

**Next**

- Topic 5: Strings and input. Then the Module 1 checkpoint, the receipt calculator.

## 2026-11-06: The third lesson, Variables

**Done**

- `content/topics/py.variables`, status `ready`, following the data model's sketch for this topic:
  - **Learn:** CS50P Lecture 0 from 15:16 to 19:54. It covers why a program keeps values, `=` as assignment from right to left, choosing names, and `print(name)` versus `print("name")`. The intro replaces David's "container" picture with name tags: for numbers and text they agree, but only name tags survive lists (Module 5).
  - **More resources:** a Python Tutor link with `a = 3; b = a; a = 5` preloaded and "show numbers as objects" on, so names are drawn as arrows. I checked in a browser that it opens on Python 3.11 with the arrows drawn. Python Tutor is free to use under its terms (© Philip Guo); we only link to it.
  - **Practice:**
    - a worked example following `city` through reassignment and `home = city`;
    - three questions: what `b` refers to after `a = 5`, a trace, and `print("name")` (mixing in topics 1 and 2);
    - filling in a swap with `temp`;
    - rotating three values.
  - **Prove it:**
    - build: swap and print from a blank editor;
    - debug: a lost value from `left = right; right = left`, hidden behind a `rigth` typo;
    - explain: why `b` stays `3`.
  - **Review pool:** four items. Skills: `assignment` (2 follow-up candidates), `trace-values` (4) and `swap` (4).
- **`run_with` in `harness/checks.py`:** reruns the program with other starting values for named variables. Five exercises use it, so retyping `5 3` can't pass. Each also has a "typed-in" known-wrong solution that the checker proves fails. It has 4 unit tests and a new scenario (`check-run-with`). CPython and Pyodide agree, and no existing scenario result changed.
- **The dev server now watches `content/` and `harness/`.** Viewing topic 3 on the owner's dev server showed "Missing practice item" for everything: Vite only watches `web/` for new files, so the glob list of exercises was stale. A small plugin adds the two folders to the watcher. I tested it on a temporary server that shut itself down: a file added under `content/` appeared within 3 seconds, and disappeared when removed.
- The content tests no longer assume a particular topic is unwritten; they pick whichever is still an outline.

**Next**

- Topic 4: Arithmetic.

## 2026-11-06: Mistakes come back, for everything (and the research's timing)

**The owner asked** whether mistakes coming back works for everything, not just the comma question. Yes: any question or code exercise, in practice, proof checks or reviews, in every ready topic. Explain-it-back will join once it's graded (Milestone B).

**Found while checking that:** one miss can open follow-ups for several skills, and they could all pick the same "never answered" question. Missing the recipe card in topic 1 would have shown the shopping-list exercise twice. Fixed with `planCards`: each skill gets its own question where possible, and a shared one is asked once, for both, with per-skill results.

**Decided (the owner):**

- **Timing:** "whatever the science says will make it stick". Successive relearning recommends at least 3 relearning sessions with growing gaps (Rawson & Dunlosky, 2011; Rawson, Dunlosky & Sciartelli, 2013; Cepeda et al., 2008). So: right on 3 different days, coming back after 1, 3 and 7 days. Recorded in ADR-0011 with the references.
- **Code exercises:** "good as is". Missed only if no Check passed that day.

**Also:**

- `everyItem.test.ts` checks every graded item of every ready topic against the real content: a miss must bring back a different question on each of its skills, and never a proof check.
- A test helper changed shared sample data, which made a later test fail. The sample topic now hands out copies.

**Possible later:** the "first session" half of successive relearning, getting it right about 3 times on the day of the miss. The research finds its benefit mostly fades once the later sessions happen.

## 2026-11-06: Mistakes come back (ADR-0011, built)

**Decided**

- ADR-0011 is now Accepted. The owner kept the defaults: right on 2 different days relearns a skill.
- Two refinements, recorded in the ADR and told to the owner:
  - **Timing:** the earlier message said "next day, about 3 days, then a week", but with 2 correct days the week is never reached. It's now: due the next day, then 3 days after a correct day. Correct answers on the day of the miss don't count.
  - **Code:** failing Checks while working something out are part of solving, so a code exercise counts as missed only if no Check passed that day. Questions count on any wrong answer that day.

**Done**

- `web/src/followups/`:
  - **`followUps.ts`:** pure functions for the day-by-day state of each skill and the choice of question (never answered first, then the one answered longest ago; the missed one only if nothing else is left). 20 tests.
  - **`history.ts`:** reads graded attempts from Supabase, 1,000 rows per request. Times are normalized: the server writes `+00:00`, the browser `Z`.
  - **`useFollowUps.ts`:** combines the server history with the events on this device.
- The event log now exposes `getLocalRows()`: what's still in the outbox, plus everything recorded since the page opened. It keeps them after they're sent, so an answer can never vanish between the outbox and the server.
- **Today:**
  - "Mistakes to revisit" with one card per due skill. The question is chosen once per visit, so the card doesn't change while it's being answered, and it shows the result: relearned, back in 3 days, or back tomorrow.
  - "Coming back later" lists what's due on other days.
  - Signed-out, loading and failed states, with "Try again".
  - Today now loads only when visited (it can include code editors).
- Practice items know the `review` context, with no hints.
- Tests: 157 web tests in all (32 new). They cover the rules, paging, the Today page's states and a full answer.

**Tried end to end** on the dev server against the local Supabase, with the local test account:

- a "missed yesterday" answer was put straight into the local database;
- Today showed the comma skill with a _different_ question (the new review question);
- a correct answer said "Right! It comes back on Mon, Nov 9";
- the review event landed in `public.events`;
- after a reload, Today showed "Nothing to revisit today" and the skill under "Coming back later".

**Found while building it:** the Today page checked "are the questions chosen?" before "did loading fail?", so a failed load would have shown "Loading…" forever. A test caught it.

**Note:** a dev server records the commit it was _started_ on as `content_build` (Vite's `define` runs once at startup). Live builds always record their own commit.

**Next**

- The owner's comma mistake comes back on the live Today page tomorrow, Nov 7.
- Topic 3: Variables.

## 2026-11-06: The second lesson, Values and types

**Done**

- `content/topics/py.values-and-types`, status `ready`:
  - **Learn:** CS50P Lecture 0 from 59:32 (integers) to 1:07:58 (the fixed calculator). The lecture has no stretch dedicated to types and never uses `type()`. But this one shows _why_ types matter: typed input is text, so `1` and `2` make `12`. The intro says that `x = 1` and `input()` come in later topics, and that the Run button replaces the `>>>` prompt. Floats (1:14:31) and the Python tutorial's "Numbers" section (PSF License Version 2) are linked as more resources.
  - **Practice:**
    - a worked example, `type()` on four values, explaining the `<class 'str'>` format;
    - three questions: which type is `7.0`, why `print(5)` and `print("5")` look the same (mixing in topic 1), and what `+` does with numbers and with text;
    - a fill-in exercise (one value of each type);
    - a write exercise (add, join, check a type).
  - **Prove it:**
    - build: a type report. Its hidden tests also check that the source uses `type()` three times, so typing the answers out by hand fails.
    - debug: a receipt with a `TypeError` crash on line 4 and a silent `"3" + "2"` on line 3. Fixing the crash reveals the wrong total.
    - explain: the calculator that prints `12`.
  - **Review pool:** three items. Skills: `identify-types` (7 follow-up candidates) and `plus-by-type` (3).
- Checked: every quoted output and error message (Python 3.14, through the harness); the tutorial's anchor and license; the feedback for each starter and wrong answer; the page on the dev server.
- The content loading test now runs for every ready topic.

**Next**

- The owner finishes Programs and print, then Values and types.
- Build ADR-0011: mistakes come back as fresh questions.

## 2026-11-06: Skills, so mistakes can come back (ADR-0011)

**Why:** the owner missed a predict-the-output question about `print` with commas and asked for wrong answers to be remembered and re-tested until they get them right. The miss is already saved in the event log, but nothing brought it back.

**Decided** (the owner chose the order and the approach):

- Write [ADR-0011](decisions/0011-mistakes-come-back.md), proposed. A miss opens a follow-up for each skill the item tests. It comes back as a _different_ question on that skill: the next day, then after about 3 days, then a week. It's closed once the skill is answered correctly on 2 different days. A topic can't be Mastered with open follow-ups. It's derived from the event log, so today's miss will be included.
- Build order: topic 2 (Values and types) first, then the feature. Skills go into the content format now, so topic 2 is written ready for it.

**Done**

- Content format:
  - topics declare `skills` (an ID and a description);
  - recall items and exercises list `skills`;
  - the checker requires skills on every graded item of a ready topic, at least 2 follow-up candidates per skill (recall items, fill-in, write, `review_code`), and declared names only. 4 new checker tests.
- The app's content types and loader carry skills, though nothing shows them yet.
- Programs and print:
  - its 4 skills are `print-text`, `print-commas`, `blank-lines` and `read-errors`;
  - a new review question on commas gives the owner's miss two fresh questions to come back as.
    Labeling items doesn't change what they ask, so no `rev` bumps.

**Next**

- Topic 2: Values and types.
- Then the follow-up function and the Today list (ADR-0011).

## 2026-11-06: Fix: video clips looked as long as the whole lecture

**Found by the owner** on their first lesson. The page said "about 40 minutes", but the embedded video showed 1 hour 45 minutes. YouTube's player always displays the full video's length, even when `start` and `end` limit what plays, and nothing on the page said so.

**Done**

- Above an embedded clip, the page now says: "This clip: 0:24 to 9:51 (about 9 minutes). The player shows the length of the whole video, but it stops by itself at 9:51." The video is linked to that note for screen readers.
- The topic header now reads "About 40 minutes for the whole topic".
- The lesson's intro no longer gives its own length, so the clip note is the one place that states it.
- Tests cover the note, for the sample topic and the real one.

**Lesson:** check the page the way a learner sees it, including what third-party widgets (like YouTube's player) show on their own.

## 2026-11-06: The first lesson, Programs and print

**Done**

- `content/topics/py.programs-and-print`, status `ready`:
  - **Learn:** a 9.5-minute segment of CS50P Lecture 0, from 0:24 (after the opening music) to 9:51 (the fixed program running again). It covers the first program, the interpreter reading top to bottom, functions, arguments and side effects, then a deliberate missing `)` and its syntax error. Before it, an intro on what to watch for, which notes that the Run button replaces VS Code and the terminal. After it, a recap in our own words.
  - **Practice:**
    - a worked example (a text line, a blank line, and two pieces joined by a comma);
    - a question on what quotes do;
    - a predict-the-output question;
    - a question on reading a `NameError`;
    - a fill-in exercise (shopping list);
    - a write exercise (recipe card).
  - **Prove it:**
    - build: a banner, with hidden tests;
    - debug: a syntax error that hides a `NameError`, so the learner fixes one error, runs again, and reads the next;
    - explain: why earlier lines still print, what the error says, and how to fix it.
  - **Review pool:** a syntax-error question, a predict-the-output question, and a postcard exercise.
- Checked:
  - the video ID and its embeddability through YouTube's oEmbed;
  - the timestamps, from CS50's published subtitles (used only to find times, never copied);
  - every quoted error message, by running it through the harness on Python 3.14;
  - the feedback for each starter and wrong answer, by running them through `harness/cli.py check`.
- App fixes found by looking at the real topic:
  - quiz answer choices now render Markdown (they showed raw backticks);
  - code boxes had the same color as cards in dark mode.
- Tests: the real topic loads through the actual build pipeline (lesson, questions, exercise code) and its page renders.

**Decided**

- While the owner is the only learner, a topic goes straight to `ready`. Their first pass on the live site is the review, and follow-up fixes bump the `rev` of any item whose meaning changes. Recorded in the v1 spec and the content README.
- Vary where the right answer sits in multiple-choice questions. Shuffling the choices on screen would help reviews; it's planned for when reviews arrive (Milestone C).
- The owner's idea of a practice-hours tracker, counting deliberate practice toward 10,000 hours, is on the roadmap for Phase 2.

**Next**

- The owner learns Programs and print on the live site and reports anything confusing.
- Write the next topic: Values and types.

## 2026-11-06: Saving progress (the event log, F6)

**Done**

- `web/src/events/`:
  - the **event log** turns what a page reports into a complete row: a browser-made ID, the learner, the study session, the time, and the commit;
  - the **outbox** in `localStorage` keeps events until the server confirms them;
  - **sync** sends batches as an upsert that ignores duplicates, so retries are safe.
- When saving fails:
  - retries wait 5 s, 10 s, 20 s… up to 5 minutes;
  - the app tries again at once when the browser comes back online or the tab is shown again;
  - an event the server refuses is set aside so it can't block the rest.
- Recorded on topic pages:
  - `lesson_view`;
  - `answer` (multiple choice, predict the output);
  - `code_run`, `code_check` and `hint` (exercises);
  - the context is `practice` or `prove`.
    Attempt time runs from the first click or focus inside an item. The exact `data` per event type is now in the data model.
- `vite.config.ts` writes the git commit into the build as `content_build`.
- A "Not saved yet" badge in the header. Topic pages tell signed-out visitors their answers won't be saved.
- Tests: 41 new web tests (120 in total). They cover the outbox (including two tabs), batching, retries with fake timers, setting aside a refused event, signed-out and still-loading sign-in, sessions, and what each page records.

**Tried end to end** against the local Supabase in Docker, signed in by email link through Mailpit, with the sample topic copied in temporarily:

- a lesson view, a correct answer (2.4 s) and a failed check (with its code) appeared in `public.events` within 70 ms, with the right user, revision and commit;
- with the API container stopped, an answer showed "Not saved yet";
- after restarting it, the answer arrived 7 s later on its own, keeping its original time. It was received 15 s after it happened.

**Lessons**

- On this Windows machine, stopping a background shell task doesn't stop the Vite server it started. Two test servers (ports 5174 and 5175) were left running, and ending processes needs the owner's permission. Next time, start at most one test server per session and plan how it will be closed.
- The shared test setup now clears `localStorage` after each test, but only where it exists: the Pyodide tests run in plain Node.

**Next**

- Write the first real topic, `py.programs-and-print`, then the rest of Module 1.

## 2026-11-06: Content pipeline, part 2 (topic pages)

**Done**

- The app reads `content/` at build time:
  - a small Vite plugin turns YAML into data;
  - `@mdx-js/rollup` compiles lessons;
  - Python files are loaded with `?raw`;
  - `content/content.ts` finds everything with `import.meta.glob`.
    Outlines are bundled into the app, and each topic's lesson and exercises download when its page opens.
- Topic pages:
  - **Learn:** objectives, intro, a privacy-enhanced YouTube embed with start and end times, recap, and more resources.
  - **Practice:** worked example, multiple choice, predict the output, fill in, and write. Hints come one at a time, and the reference solution appears after a pass.
  - **Prove it:** build and debug, plus the explain prompt. Its rubric and model answer are never sent to the screen.
- The map now lists all 36 topics by module.
- Small additions:
  - per-exercise time limits;
  - an error page with Reload (stale chunks after a deploy);
  - the current page fades while the next one loads.
- The checker now enforces the convention the page relies on: a lesson places only its main resource, `<Resource index={0} />`.
- Tests:
  - 29 new web tests (79 in total);
  - shared test helpers: a fake Python runner, a plain-textbox editor, a sample topic;
  - 2 new checker tests (41 Python tests).

**Found by trying it end to end.** I copied the checker's sample topic into `content/` temporarily, then built the app and clicked through it in the browser on a separate dev server (port 5174). The production build failed: a compiled lesson imports React, but lessons live outside `web/`, so module lookup never reached `web/node_modules`. The fix is `resolve.dedupe: ['react', 'react-dom']` in `vite.config.ts`. After that:

- the lesson, the embed, and every practice item rendered;
- the fill-in starter failed in real Pyodide;
- a correct answer passed and revealed the reference solution;
- the prediction check worked;
- there were no console errors.
  The sample topic was removed afterwards. The unit tests couldn't have caught this, because the repo has no lesson files yet.

**Decided**

- The main bundle was already over Vite's 500 kB warning before this change (542 kB, mostly React, React Router and supabase-js). This change adds about 22 kB, mostly the 36 topic outlines. Splitting the bundle is a later job.
- Each content file becomes its own small download (about 20 per topic, fetched in parallel). Grouping them per topic needs Rolldown's chunk groups, which by default pull a grouped file's dependencies (React) in with it. That's risky, so it's left alone until it matters.

**Next**

- Save answers and lesson views to the event log (F6), with a local outbox and sync.
- Write the first real topic, `py.programs-and-print`, then the rest of Module 1.

## 2026-11-06: Content pipeline, part 1 (format and validator)

**Checked first:** the owner's restarted dev server is healthy (fresh process; styles compile; the harness and Supabase modules load).

**Done**

- `content/`: the Python Foundations track and all 36 topics from the approved list, as `planned` outlines with the exact prerequisite graph from the spec. A new `status` field (`planned`, `draft`, `ready`) lets the map be complete before the lessons are written.
- `tools/content_model.py`: pydantic models for every content file. They reject unknown fields, so typos are caught.
- `tools/validate_content.py` checks:
  - file formats, and that IDs match their folders;
  - tracks and modules, prerequisites, and no cycles;
  - the definition of done for `ready` topics;
  - by running them through the harness in a fresh process: reference solutions pass, starters and known-wrong solutions fail, predict-the-output items print what they claim, and code that never stops is reported.
- `harness/cli.py`: a command-line entry the validator and the scenario tests share.
- 14 validator tests, built on a tiny complete topic, each breaking one thing. 39 Python tests in total. A new **Content** CI job runs the validator.

**Next**

- Part 2: the app loads content (YAML and MDX through Vite), with topic pages for lessons and exercises.
- Then saving answers to the event log, and writing Module 1.

## 2026-11-06: First real sign-in; sign-ups closed

- The owner signed in with GitHub on the live site. Supabase shows one user, created through GitHub at 10:25.
- At the owner's request, I used the browser to switch off **"Allow new users to sign up"** in the Supabase dashboard. First I checked the owner's account existed, so they couldn't be locked out.
- Verified independently through the public auth settings endpoint: `disable_signup: true`, with GitHub and email providers enabled. Email sign-in only works for existing accounts now.
- Milestone A remaining: the content pipeline, topic pages and saving answers, and Module 1 content.

## 2026-11-06: Sign-in

**Owner's setup:** a GitHub OAuth app (`education-platform`), the GitHub provider turned on in Supabase, and the Site URL and redirect URLs set to the live address. The OAuth app's GitHub form calls the callback field "redirect URI".

**Done**

- Added supabase-js 2.119, with the PKCE flow. That isn't its default, and it also makes supabase-js remove the one-time `?code=` from the address bar. Settings for local and production live in `src/supabase/config.ts`; the keys are publishable, so public by design.
- `AuthProvider` and `useAuth` track who's signed in; the header shows the name and Sign out; there's a `/sign-in` page.
  - **Live site:** "Sign in with GitHub".
  - **Dev server:** an email-link form instead, since the local Supabase has no GitHub app; the email lands in Mailpit.
- Database types are generated from the schema (`npm run db:types`).
- 6 new tests with a fake sign-in service; 50 web tests in total.
- **End to end against the local Supabase, in a real browser:** I requested a link, fetched the email from Mailpit's API, and opened the link. That signed me in, removed the code from the address, and showed the email in the header. The trigger created the profile (no name, `allowed = false`), and Sign out worked.

**Notes**

- Supabase accepts a sign-in redirect to any port on the Site URL's host name. So a second dev server on `localhost:5174` works without config changes.
- The owner's dev server from yesterday was still running on port 5173 (IPv6 only, so Windows' port check missed it). I left it alone; it needs a restart.

**Next**

- The owner tries GitHub sign-in on the live site; then we close sign-ups.
- The content pipeline, topic pages and saving answers.

## 2026-11-06: The real database has its tables

- The owner logged in to the Supabase CLI and linked the `education-platform` project. The CLI didn't need the database password; it uses the login.
- Applied the first migration to production with `npx supabase db push --remote --yes`, after a `--dry-run` that listed exactly that one migration. `migration list --remote` shows the local and production histories match.
- Note: Supabase CLI 3 targets the local database unless `--remote` is given. The docs now say so.
- Next: sign-in with GitHub (the owner sets up a GitHub OAuth app and the Supabase provider) and sending events from the app.

## 2026-11-06: Live on Cloudflare; NordPass fix

**Done**

- The owner connected the repo in Cloudflare and switched on the workers.dev address. The app is live at https://education-platform.arasmussen64.workers.dev, and deep links like `/topic/py.variables` work.
  - `web/wrangler.jsonc` now sets `workers_dev` and `preview_urls`, so a deploy can't switch them off.
  - The setup guide now matches Cloudflare's real screen: "Path" under Advanced settings, and no production-branch field.
- Merging to `main` triggered a production build, which succeeded, so automatic deploys work.
- The program-input field is now an editable `<span role="textbox">`. NordPass still popped up on the earlier `<input>`: it has no opt-out attribute for pages, and it read the prompt "What's your name?" as a contact form. Password managers only look at real form fields. A test now checks it stays a span.

**Preview builds: found and fixed** (by reading the build log in the dashboard, at the owner's request)

- The builds didn't fail instantly. GitHub only receives the result at the end, so the start and finish times matched. The builds ran for about 6 minutes, and only the last step failed.
- Cloudflare's default deploy command for pull requests is now `npx wrangler preview` (open beta). It refuses to run without a `previews` block in the Wrangler config. Added `"previews": {}`.
- 6 of those minutes went to installing Python 3.14 that the web build never uses. Cloudflare's build spots a `.python-version` file and installs that Python, on production builds too. The Python version is now pinned with `requires-python = "==3.14.*"` in `pyproject.toml`, and the file is gone. uv still uses 3.14.

**Lesson**

- `cmd | tail` hides `cmd`'s exit code, which made a lint failure look like success locally. CI caught nothing wrong because I fixed it before pushing. Check exit codes directly.

## 2026-11-05: Local Supabase and the first tables

**Owner's setup:** Docker Desktop is installed (engine 29.8, 8 CPUs and 16 GB for Docker), a Supabase project exists, and a Cloudflare account exists.

**Done**

- Added the Supabase CLI (3.0) as a pinned dev dependency in a new root `package.json`, with `db:*` scripts.
- Set up `supabase/`. The local copy skips realtime, file storage and log analytics, which aren't used, to save memory.
- Wrote the first migration:
  - **`profiles`:** created automatically at sign-up. A learner can read their own row and change only `display_name` and `settings`, never `allowed`.
  - **`events`:** append-only. Learners can insert and read only their own rows. `received_at` is always set by the server. A trigger blocks update, delete and truncate even for admins, except for a deliberate whole-account deletion.
- Wrote 18 pgTAP tests for those rules, and a **Database** CI job (throwaway database, `db lint`, `db test`).

- First local start: Postgres 17 came up, the migration applied, lint was clean, and 18/18 tests passed. They also passed in CI (PR #7).
- Added the Cloudflare config (`web/wrangler.jsonc`) for static assets with single-page-app fallback. Wrangler 4.158 is pinned and its telemetry is off. A dry-run deploy succeeded.

**Next**

- One-time steps by the owner ([setup](setup.md)): connect the repo in Cloudflare, which gives the first deploy, then `npx supabase login` and `link`.
- Push the first migration to the cloud project once it's linked.
- Sign-in (needs a GitHub OAuth app) and sending events from the app.

## 2026-11-05: Playground fixes after the owner's first try

**What the owner saw**

- The input box was invisible.
- The greeting didn't print "Hello, Alex!".

**What was wrong**

- **The invisible box:** the owner's dev server had been running since before I changed `vite.config.ts` and installed packages. It got stuck half-updated, serving Tailwind's raw source instead of compiled CSS, so every element lost its styling. A fresh server was fine; the fix is a restart. `CLAUDE.md` and `web/README.md` now say to restart after config or package changes.
- **No "Hello, Alex!":** on the unstyled page, the invisible input boxes sit away from their labels, so the name most likely went into the wrong box. The design was the deeper problem: filling in a box _before_ pressing Run isn't how anyone expects Python to work.

**Done**

- Run now behaves like a terminal. When the program calls `input()`, a text field appears right after the prompt with the cursor in it, and Enter sends the line.
  - The harness stops at an unanswered `input()` and reports `waiting_for_input`, instead of raising `EOFError`.
  - The app re-runs the program from the start with every line typed so far.
  - Re-runs use a fixed random seed, so random choices repeat.
  - The stop signal is a `BaseException`, so a learner's `except Exception:` can't swallow it.
- Added 3 scenarios: waiting for a second input, a seeded random program, and `except Exception` around `input()`. All 17 scenarios match between CPython and Pyodide.
- Found while testing in Pyodide: JavaScript `null` arrives in Python as a special "JS null", not `None`, so the app now passes `undefined` instead.
- Testing in a real browser:
  - The full flow worked: Run, type "Alex", Enter, and "Hello, Alex!" appeared.
  - The owner's autofill extension then offered to save "Alex" as contact info. The field no longer uses a `<form>` and carries the usual "ignore me" markers for password managers.
  - After that change, the extension's overlay blocked my browser tools, so the final check is left to the owner.
- Added a "Loading…" screen while on-demand pages load, which fixes a React Router console warning.

**Next**

- The owner restarts their dev server and tries the Playground.
- The content pipeline and validator, then Module 1 content.

## 2026-11-05: Python runs in the browser

**Done**

- Built the browser side of the Python runner:
  - Pyodide 314.0.7 runs in a Web Worker, loaded from the jsDelivr CDN.
  - `PythonRunner` queues requests and replaces the worker when code runs past 5 seconds.
  - A CodeMirror editor with Run and Check, on a temporary Playground page.
- The 14 harness scenarios now also run under real Pyodide (in Node) in the web tests. They match CPython exactly, tracebacks included.
- Checked the production build in a real browser:
  - Pyodide loaded in the background.
  - Run echoed input like a terminal.
  - Check failed, then passed after fixing the code.
  - An infinite loop was stopped after 5.1 seconds while the page stayed responsive.
  - The next run worked 0.1 seconds later.
  - No console errors.
- Made the Playground load on demand: the main bundle dropped from 786 KB to 320 KB.

**Fixed along the way**

- The status message now uses an `<output>` element, as the accessibility lint rule suggested.
- The summary now reads naturally for a single check ("The check passed!" instead of "All 1 checks passed!").
- Tests get their own TypeScript settings with Node types, so app code can't use Node APIs by accident.

**Next**

- The content pipeline and validator, then Module 1 content.
- Local Supabase once Docker Desktop is installed ([setup](setup.md)).

## 2026-11-05: Python test harness

**Done**

- Wrote the shared Python harness (`harness/`): `checks.run()` for tests, the Run and Check logic, and beginner-friendly error messages that only show the learner's own file.
- Added 14 scenarios with expected results I reviewed by hand, plus unit tests. A new CI job runs them with uv, pytest and ruff.
- Installed uv for this user, and Python 3.14 through it.

**Decided**

- Pyodide has a new version scheme (314.0.7 bundles Python 3.14), so the Python tooling targets 3.14.
- The content validator will use the harness's own test runner, not pytest. pytest rewrites `assert` statements in files named `test_*.py`, which changed the messages. Two scenarios that failed only under pytest exposed this.

**Next**

- The browser side: Pyodide in a Web Worker, the editor, Run and Check, and the same scenarios under Pyodide.

## 2026-11-05: Process and environment decisions

**Decided**

- The owner gave standing permission for Claude to merge its own pull requests once CI passes. Explain-it-back questions continue, but they never block merging.
- Supabase's second free project slot is already in use, so the platform gets one cloud project, for real learning only. Development runs a local Supabase in Docker Desktop ([ADR-0010](decisions/0010-environments.md)). The owner chose this over sharing the cloud project with a test account.

**Done**

- Merged the web app scaffold (PR #2).
- Wrote ADR-0010 and a [setup guide](setup.md) for the owner's computer and accounts.

**Next**

- The owner installs Docker Desktop, creates the Supabase project, and creates a Cloudflare account ([setup](setup.md)).
- The Python runner in the browser.

## 2026-11-05: Milestone A starts with the web app scaffold and CI

**Done**

- Merged the v1 spec (PR #1).
- Scaffolded the web app in `web/` with create-vite 9: Vite 8, React 19, TypeScript 7, React Router 8, Tailwind CSS 4, Vitest 5, Oxlint (with accessibility rules) and Prettier.
- Added placeholder pages (Today, the topic map, a topic, and "not found") inside a shared layout.
- The product name lives only in `web/src/config.ts`. A small Vite plugin puts it in the page title (ADR-0006).
- Wrote 5 route tests. Added CI on GitHub Actions: formatting, lint, type-check, tests and build.

**Notes**

- Several tools are newer than expected (React Router 8, Vitest 5, TypeScript 7), so I checked what they export before writing code against them.
- create-vite now defaults to Oxlint instead of ESLint. I kept the default.

**Next**

- The Python runner in the browser: Pyodide in a Web Worker, plus the `checks` test helper.
- The owner creates free Supabase and Cloudflare accounts.

## 2026-11-05: v1 spec

**Done**

- Wrote the [v1 spec](specs/v1.md): 16 features with acceptance criteria, four milestones (A–D), non-functional requirements, and a content definition of done.
- Wrote the [data model](specs/data-model.md): content file formats, the `checks` test helper, the Postgres tables, and the exact rules for topic states.
- Planned the [Python Foundations track](specs/python-foundations.md): 30 topics in 6 modules, each ending with a checkpoint, mostly built around CS50P lectures.
- Proposed ADR-0008 (append-only event log) and ADR-0009 (per-topic reviews, graded automatically).

**Decided** (the owner approved the spec pull request)

- The "prove it" checks, topic states and gating move from Phase 2 into Phase 1. They reuse the exercise engine, and v1 shouldn't call anything Learned without proof.
- ADR-0008 and ADR-0009 accepted.
- The topic list is approved as written.
- AI budget cap: $10 a month to start.

**Next**

- Milestone A: scaffold the app and CI, then the Python runner, the content pipeline, Supabase, the deploy, and Module 1 content.

## 2026-11-05: From idea to project setup

**Done**

- Researched Brilliant, roadmap.sh and Math Academy ([competitors](research/competitors.md)).
- Pinned down the concept through a Q&A ([vision](vision.md)):
  - Adaptive, from total beginner to principal engineer. First track: CS foundations → ML engineering.
  - Core promise: you can _apply_ it, not just recognize it.
  - Mastery needs all four proofs: blank editor, explain it back, debug unfamiliar code, delayed review.
  - Gated, with test-out.
  - AI as hint-only tutor, reviewer, practice generator, and an "earn the AI" track.
  - Content: curated free resources plus AI-written supporting material; practice owned by the platform.
  - Free and personal-use first; free hosting; owner full time, learning in the mornings and building in the afternoons.
- Picked the working name **Switchback** (may change).
- Set up the repository: CLAUDE.md, README, CHANGELOG, ADR-0001 to ADR-0007, git config files.
- Backed it up to a private GitHub repo, `education-platform`.

**Decided:** ADR-0001 to ADR-0007 accepted, including the tech stack (ADR-0007): a TypeScript/React app on Cloudflare, Supabase, Pyodide, and Python for tooling and ML. It replaced the earlier "Python backend" idea because free Python hosting sleeps when idle.

**Next**

- Write the v1 spec: feature list, data model, the first 30 Python topics.
- Scaffold the app, CI and first deploy.
