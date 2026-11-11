"""Writes ml.m2.checkpoint, "Checkpoint 2: a small data library", which closes
the ML track's Module 2. Run from the repository root. Files are written as
bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.m2.checkpoint")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


READINGS = '''{"sensor": "a", "temperature": 18.5}
{"sensor": "b", "temperature": 21.5}
{"sensor": "c"}
{"sensor": "d", "temperature": 20.0}
'''
RAIN = '''{"station": "north", "mm": 3.0}
{"station": "south", "mm": 0.0}
{"station": "east"}
{"station": "west", "mm": 7.5}
'''
SCORES = '''{"player": "ada", "score": 12}
{"player": "bo", "score": 30}
{"player": "cy"}
{"player": "di", "score": 18}
'''

RUNNER = '''
passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
'''


def file_prelude(filename, lines):
    return f'''import json

LINES = """{lines}"""
with open("{filename}", "w") as f:
    f.write(LINES)


'''


CLASS_HEAD = '''class Dataset:
    def __init__(self, path):
        self.path = path

    def rows(self):
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def column(self, name):
        for row in self.rows():
            if name in row:
                yield row[name]

    def summary(self, name):
        values = list(self.column(name))
        if not values:
            return {"count": 0, "mean": None, "min": None, "max": None}
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def write_report(self, name, path):
        s = self.summary(name)
        with open(path, "w") as f:
            f.write(f"{name}: count={s['count']} mean={s['mean']} min={s['min']} max={s['max']}\\n")
'''


def use_it(filename, column):
    return f'''

ds = Dataset("{filename}")
print(len(list(ds.rows())), "rows")
print(ds.summary("{column}"))
ds.write_report("{column}", "report.txt")
with open("report.txt") as f:
    print(f.read(), end="")
'''


def learner_tests(filename, column, summary_literal):
    return f'''

def test_summary_of_{column}():
    ds = Dataset("{filename}")
    assert ds.summary("{column}") == {summary_literal}


def test_summary_of_a_missing_column():
    ds = Dataset("{filename}")
    assert ds.summary("nothing") == {{"count": 0, "mean": None, "min": None, "max": None}}
'''


def build_solution(filename, lines, column, summary_literal):
    return (
        file_prelude(filename, lines)
        + CLASS_HEAD
        + learner_tests(filename, column, summary_literal)
        + use_it(filename, column)
        + RUNNER
    )


def build_tests(expected):
    return f'''import importlib
import io
import sys
from contextlib import redirect_stdout

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).

EXPECTED = {expected!r}
OTHER = '{{"id": 1, "x": 2}}\\n\\n{{"id": 2}}\\n{{"id": 3, "x": 4}}\\n'


def load_solution():
    """The learner's module, imported fresh, with its prints swallowed."""
    sys.modules.pop("solution", None)
    importlib.invalidate_caches()
    with redirect_stdout(io.StringIO()):
        return importlib.import_module("solution")


def learner_tests(module):
    return [getattr(module, name) for name in dir(module) if name.startswith("test_")]


def catches(module, bug):
    """Whether any of the learner's tests fails once Dataset.summary is replaced by bug."""
    if not hasattr(getattr(module, "Dataset", None), "summary"):
        raise AssertionError("Define a class called Dataset with a summary method.")
    original = module.Dataset.summary
    module.Dataset.summary = bug
    try:
        for test in learner_tests(module):
            try:
                test()
            except Exception:
                return True
        return False
    finally:
        module.Dataset.summary = original


def other_dataset():
    with open("other.jsonl", "w") as f:
        f.write(OTHER)
    return function("Dataset")("other.jsonl")


def test_the_output():
    """Prints the row count, the summary, the report line and 2 passed."""
    assert run() == EXPECTED


def test_rows_is_a_lazy_generator():
    """Making a Dataset reads nothing; rows() hands out one record per next() and skips blank lines."""
    Dataset = function("Dataset")
    Dataset("no-such-file.jsonl")
    rows = other_dataset().rows()
    assert next(rows) == {{"id": 1, "x": 2}}
    assert list(rows) == [{{"id": 2}}, {{"id": 3, "x": 4}}]


def test_column_and_summary():
    """column skips records without the key; summary has count, mean, min and max, and a zero count for a missing column."""
    ds = other_dataset()
    assert list(ds.column("x")) == [2, 4]
    assert ds.summary("x") == {{"count": 2, "mean": 3.0, "min": 2, "max": 4}}
    assert ds.summary("nope") == {{"count": 0, "mean": None, "min": None, "max": None}}


def test_the_report():
    """write_report writes the one-line report to the path it's given."""
    other_dataset().write_report("x", "other-report.txt")
    with open("other-report.txt") as f:
        assert f.read() == "x: count=2 mean=3.0 min=2 max=4\\n"


def test_the_tests_catch_a_wrong_summary():
    """At least two tests, all passing, that fail for a summary that counts every row, and for one that crashes on a column no record has."""
    module = load_solution()
    assert len(learner_tests(module)) >= 2
    for test in learner_tests(module):
        test()

    def counts_every_row(self, name):
        rows = list(self.rows())
        values = [row[name] for row in rows if name in row]
        return {{"count": len(rows), "mean": sum(values) / len(rows), "min": min(values), "max": max(values)}}

    def crashes_on_empty(self, name):
        values = list(self.column(name))
        return {{"count": len(values), "mean": sum(values) / len(values), "min": min(values), "max": max(values)}}

    assert catches(module, counts_every_row)
    assert catches(module, crashes_on_empty)
'''


BUILD_TEST_SKILLS = '''# Every test names the module skills it checks (ADR-0012), so a failed test
# says which topics to revisit.
test_skills:
  test_the_output: [ml.py.classes/define, ml.py.json-and-nested-data/json-io]
  test_rows_is_a_lazy_generator: [ml.py.iterators-and-generators/generators, ml.py.iterators-and-generators/protocol, ml.py.classes/instances]
  test_column_and_summary: [ml.py.json-and-nested-data/safe-walk, ml.math.probability-and-statistics/center, ml.py.classes/methods]
  test_the_report: [ml.py.classes/methods, ml.py.json-and-nested-data/json-io]
  test_the_tests_catch_a_wrong_summary: [ml.py.writing-tests/write-tests, ml.py.writing-tests/edge-cases]
'''


def build_prompt(opening, filename, lines, column, summary_literal, report_line):
    return f'''  {opening}

  **The data.** Your program writes this file first, as `{filename}`, exactly as shown: one JSON object per line (JSON Lines), with a record that lacks the `{column}` key.

  ```
{"".join("  " + line + chr(10) for line in lines.strip().splitlines())}  ```

  **The class.** Then a class `Dataset`:

  - `Dataset(path)` remembers the path. Nothing is read until `rows()` is called.
  - `rows()` is a **generator**: it opens the file and yields each line's record as a dict, one at a time, skipping blank lines.
  - `column(name)` is a generator of that column's values, from the records that have it.
  - `summary(name)` returns a dict with the `count`, `mean`, `min` and `max` of the column; for a column no record has, `{{"count": 0, "mean": None, "min": None, "max": None}}`.
  - `write_report(name, path)` writes one line to the file at `path`, in this shape: `{report_line}`, followed by a newline.

  **The tests.** Write at least two tests of `summary`, functions named `test_…` that use `{filename}`: one for `{column}`, and one for a column that no record has. The hidden checks run your tests against a `summary` that counts every row, and against one that crashes on an empty column; your tests must fail on both.

  **Using it.** The program makes `Dataset("{filename}")`, prints the number of rows, prints the summary of `{column}`, writes the report to `report.txt` and prints the report file's contents, then ends with the runner from Writing tests, which calls every `test_` function and prints how many passed:

  ```
  4 rows
  {summary_literal}
  {report_line}
  2 passed
  ```

  The checks also make a `Dataset` of their own file, with another column, and take records from `rows()` one at a time.
'''


def write_dataset_build(folder, title, opening, filename, lines, column, summary_literal, report_line):
    expected = f"4 rows\n{summary_literal}\n{report_line}\n2 passed\n"
    write(
        f"exercises/{folder}/exercise.yaml",
        f'''id: {folder}
stage: build
rev: 1
title: "{title}"
prompt: |
{build_prompt(opening, filename, lines, column, summary_literal, report_line)}{BUILD_TEST_SKILLS}''',
    )
    write(f"exercises/{folder}/starter.py", "")
    write(f"exercises/{folder}/solution.py", build_solution(filename, lines, column, summary_literal))
    write(f"exercises/{folder}/test_exercise.py", build_tests(expected))
    # A list where a generator was asked for: next() on it fails.
    write(
        f"exercises/{folder}/wrong/rows-returns-a-list.py",
        build_solution(filename, lines, column, summary_literal).replace(
            '''        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)
''',
            '''        with open(self.path) as f:
            return [json.loads(line) for line in f if line.strip()]
''',
        ),
    )
    # The mean divided by the number of rows, not the number of values.
    write(
        f"exercises/{folder}/wrong/mean-over-all-rows.py",
        build_solution(filename, lines, column, summary_literal).replace(
            '"mean": sum(values) / len(values),', '"mean": sum(values) / len(list(self.rows())),'
        ),
    )
    # A correct class with tests that would pass whatever summary did.
    write(
        f"exercises/{folder}/wrong/tests-that-dont-test.py",
        build_solution(filename, lines, column, summary_literal).replace(
            learner_tests(filename, column, summary_literal),
            f'''

def test_summary_of_{column}():
    assert True


def test_summary_of_a_missing_column():
    assert True
''',
        ),
    )
    write(
        f"exercises/{folder}/wrong/typed-in.py",
        f'''class Dataset:
    def __init__(self, path):
        self.path = path


print("4 rows")
print("{summary_literal.replace('"', "'")}")
print("{report_line}")
print("2 passed")
''',
    )


TEMPERATURE_SUMMARY = "{'count': 3, 'mean': 20.0, 'min': 18.5, 'max': 21.5}"
TEMPERATURE_REPORT = "temperature: count=3 mean=20.0 min=18.5 max=21.5"

# --- topic ---------------------------------------------------------------------

write(
    "topic.yaml",
    '''id: ml.m2.checkpoint
kind: checkpoint
status: ready
title: "Checkpoint 2: a small data library"
summary: "A Dataset class that reads JSON records lazily, summarizes a column and writes a report, with tests."
prerequisites: [ml.py.iterators-and-generators, ml.py.functions-as-values, ml.py.writing-tests, ml.py.json-and-nested-data]
estimated_minutes: 120
rev: 1
objectives:
  - "Write a class whose methods read records lazily from a JSON Lines file."
  - "Summarize a numeric column with count, mean, min and max, skipping records that lack it."
  - "Write a report file, and tests that would catch a wrong summary."
  - "Find and fix three bugs spread across a class's methods."
  - "Explain the difference between a class, an instance and a generator."
prove:
  build: build-dataset
  debug: debug-dataset-three-bugs
  explain:
    prompt: |
      Your `Dataset` has a class, an instance and a generator in it: `Dataset`, `ds = Dataset("readings.jsonl")`, and `ds.rows()`. In your own words: what is each of the three, and what does each one hold in memory? Why can `summary` call `self.column(name)` and get all the values, then another method call it again and get them all again, when a generator can only be used once? And what would change if `rows()` returned a list instead: what would get simpler, and what would stop working for a file of a billion lines?
    rubric:
      - id: three-things
        required: true
        description: "The class is the blueprint, the code for every dataset; the instance holds this dataset's state, which is only the path; the generator is one in-progress walk through the file, holding the open file and the current line."
      - id: fresh-each-call
        required: true
        description: "Each call to rows() or column() makes a new generator, which reads the file again from the start; single use is a property of one generator object, not of the method."
      - id: list-tradeoff
        required: true
        description: "A list would allow len, indexing and reuse without re-reading, but it holds every record in memory at once, which a billion-line file can't afford; the generator holds one line at a time, at the price of re-reading per pass."
      - id: memory
        required: false
        description: "Says that the instance holds no data at all, so a thousand Datasets cost nothing until they're read, or connects this to a training data loader."
    model_answer: |
      Dataset, the class, is the code: it says what every dataset can do, and nothing is read or stored by defining it. ds is an instance, one particular dataset; all it holds is the path, a short string, because the records stay in the file until something asks for them. ds.rows() is a generator, a walk through the file that is in progress: it holds the open file and the record it's on, and each next() reads one more line, turns it into a dict and hands it over. A generator can be walked once, but a method call makes a fresh generator every time: summary's self.column(name) makes a new column generator, which itself calls self.rows() and gets a new rows generator, so the file is read again from the top for every pass. That's why two methods can each get all the values. If rows() returned a list instead, a lot would get simpler: len(ds.rows()), indexing, looping twice without re-reading. The price is that the whole file is in memory at once. For a billion lines that's the program running out of memory before it starts, while the generator version holds one line at a time and finishes, slower, but it finishes. That trade is the one every training data loader makes.
# For a learner who's stuck on the build (ADR-0012): a solved sibling, the
# build in steps with hints, then fresh versions.
unstuck:
  example: example-a-log-library
  steps: [step-the-rows, step-the-column, step-the-summary, step-the-report]
  versions: [build-dataset-rainfall, build-dataset-scores]
''',
)

# --- the build and its fresh versions ----------------------------------------------

write_dataset_build(
    "build-dataset",
    "A small data library",
    "Starting from a blank editor, write a small data library and use it: a class that reads records from a file lazily, summarizes a column, writes a report, and comes with tests.",
    "readings.jsonl",
    READINGS,
    "temperature",
    TEMPERATURE_SUMMARY,
    TEMPERATURE_REPORT,
)
write_dataset_build(
    "build-dataset-rainfall",
    "A small data library: rainfall",
    "Starting from a blank editor, write a small data library for rain gauges and use it: a class that reads records from a file lazily, summarizes a column, writes a report, and comes with tests.",
    "rain.jsonl",
    RAIN,
    "mm",
    "{'count': 3, 'mean': 3.5, 'min': 0.0, 'max': 7.5}",
    "mm: count=3 mean=3.5 min=0.0 max=7.5",
)
write_dataset_build(
    "build-dataset-scores",
    "A small data library: scores",
    "Starting from a blank editor, write a small data library for game scores and use it: a class that reads records from a file lazily, summarizes a column, writes a report, and comes with tests.",
    "scores.jsonl",
    SCORES,
    "score",
    "{'count': 3, 'mean': 20.0, 'min': 12, 'max': 30}",
    "score: count=3 mean=20.0 min=12 max=30",
)

# --- the debug -----------------------------------------------------------------------

DEBUG_EXPECTED = f"4 rows\n{TEMPERATURE_SUMMARY}\n{TEMPERATURE_REPORT}\n"
write(
    "exercises/debug-dataset-three-bugs/exercise.yaml",
    f'''id: debug-dataset-three-bugs
stage: debug
rev: 1
title: "Three bugs in a Dataset"
prompt: |
  This `Dataset` should print the row count, the summary of `temperature` and the report line:

  ```
  4 rows
  {TEMPERATURE_SUMMARY}
  {TEMPERATURE_REPORT}
  ```

  It has three bugs, in three different methods, and each one hides the next: fix the first and the second shows itself. Run it, read what happens, fix, and run again until the output matches. Check each method against its job: `column` yields values from the records **that have** the column; the mean divides the total of the values by **how many values** there are; the report prints min and max in the right places.
test_skills:
  test_the_output: [ml.py.json-and-nested-data/safe-walk, ml.math.probability-and-statistics/center, ml.py.classes/methods]
  test_other_records: [ml.py.iterators-and-generators/generators, ml.math.probability-and-statistics/center]
''',
)
DEBUG_SOLUTION = file_prelude("readings.jsonl", READINGS) + CLASS_HEAD + use_it("readings.jsonl", "temperature")
write(
    "exercises/debug-dataset-three-bugs/starter.py",
    DEBUG_SOLUTION.replace(
        '''            if name in row:
                yield row[name]
''',
        '''            yield row[name]
''',
    )
    .replace('"mean": sum(values) / len(values),', '"mean": sum(values) / len(list(self.rows())),')
    .replace("min={s['min']} max={s['max']}", "min={s['max']} max={s['min']}"),
)
write("exercises/debug-dataset-three-bugs/solution.py", DEBUG_SOLUTION)
write(
    "exercises/debug-dataset-three-bugs/test_exercise.py",
    f'''from checks import function, run

EXPECTED = {DEBUG_EXPECTED!r}


def test_the_output():
    """Prints the row count, the summary and the report line."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{{EXPECTED}}\\nYour program printed:\\n{{printed}}"


def test_other_records():
    """Works for other records: a column present in two of three rows."""
    Dataset = function("Dataset")
    with open("other.jsonl", "w") as f:
        f.write('{{"temperature": 1}}\\n{{"x": 0}}\\n{{"temperature": 3}}\\n')
    ds = Dataset("other.jsonl")
    assert ds.summary("temperature") == {{"count": 2, "mean": 2.0, "min": 1, "max": 3}}, (
        f"With temperatures 1 and 3 in three rows, summary gave {{ds.summary('temperature')}}"
    )
    ds.write_report("temperature", "other-report.txt")
    with open("other-report.txt") as f:
        report = f.read()
    assert report == "temperature: count=2 mean=2.0 min=1 max=3\\n", f"The report for that file reads:\\n{{report}}"
''',
)
write(
    "exercises/debug-dataset-three-bugs/wrong/two-of-three.py",
    DEBUG_SOLUTION.replace("min={s['min']} max={s['max']}", "min={s['max']} max={s['min']}"),
)
write(
    "exercises/debug-dataset-three-bugs/wrong/typed-in.py",
    f'''LINES = """{READINGS}"""
print("4 rows")
print("{TEMPERATURE_SUMMARY.replace('"', "'")}")
print("{TEMPERATURE_REPORT}")
''',
)

# --- the way through: a solved sibling -------------------------------------------------

write(
    "exercises/example-a-log-library/exercise.yaml",
    '''id: example-a-log-library
stage: worked_example
rev: 1
title: "A small log library"
prompt: |
  Before a `Dataset` of JSON records, here is the same shape of program over a plain log file: a class that remembers a path, reads the file lazily, filters one stream out of another, counts, and writes a summary. Press **Run**, then read how each part works. Every method of `Dataset` has a twin here.
steps:
  - label: "The data file"
    lines: "1-9"
    note: "The program writes its own data first, so it can run anywhere. A log is one entry per line, like JSON Lines; one line is blank, which the reader will have to skip."
  - label: "A class that remembers only the path"
    lines: "12-14"
    note: "Making a `Log` reads nothing. The instance holds a path and nothing else; the file stays on disk until a method asks for it."
  - label: "A lazy stream of lines"
    lines: "16-20"
    note: "`lines()` is a generator: `for line in f` reads one line at a time, blank lines are skipped, and `yield` hands each one out. However long the log, one line is in memory."
  - label: "A stream filtered from a stream"
    lines: "22-28"
    note: "`level()` loops over `self.lines()`, a fresh generator each call, and yields only the lines that start with the level. `count()` consumes one such stream without building a list. `Dataset.column` is this method with `name in row` as the test."
  - label: "A report"
    lines: "30-32"
    note: "The summary is computed by calling the other methods and written as one line. Opening with `\\"w\\"` creates or replaces the file."
  - label: "Using it"
    lines: "35-40"
    note: "Make one instance, ask it things, write the summary, read it back. `len(list(...))` is the one place the whole stream is collected; it's fine for a count, and it's what `summary` does with `list(self.column(name))`."
''',
)
write(
    "exercises/example-a-log-library/solution.py",
    '''TEXT = """INFO started
WARN disk 91% full
INFO heartbeat

ERROR cannot reach db
WARN retrying
"""
with open("app.log", "w") as f:
    f.write(TEXT)


class Log:
    def __init__(self, path):
        self.path = path

    def lines(self):
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield line.strip()

    def level(self, name):
        for line in self.lines():
            if line.startswith(name + " "):
                yield line.removeprefix(name + " ")

    def count(self, name):
        return sum(1 for _ in self.level(name))

    def write_summary(self, path):
        with open(path, "w") as f:
            f.write(f"WARN={self.count('WARN')} ERROR={self.count('ERROR')}\\n")


log = Log("app.log")
print(len(list(log.lines())), "lines")
print(list(log.level("WARN")))
log.write_summary("summary.txt")
with open("summary.txt") as f:
    print(f.read(), end="")
''',
)
write(
    "exercises/example-a-log-library/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints 5 lines, the two warnings, and the summary line."""
    assert run() == "5 lines\\n['disk 91% full', 'retrying']\\nWARN=2 ERROR=1\\n"
''',
)

# --- the way through: the build in steps ------------------------------------------------

PRELUDE = file_prelude("readings.jsonl", READINGS)

write(
    "exercises/step-the-rows/exercise.yaml",
    '''id: step-the-rows
stage: fill_in
rev: 1
title: "Step 1: the rows"
prompt: |
  The first part of the data library is reading the file lazily. Replace each `...` so `rows()` is a generator that yields each line's record, skipping blank lines, and the program prints:

  ```
  {'sensor': 'a', 'temperature': 18.5}
  3 more
  ```
hints:
  - "A file can be looped over directly: `for line in f:` gives one line at a time, without reading the whole file."
  - "A generator hands a record out with `yield`, not `return`: `yield json.loads(line)`."
''',
)
ROWS_SOLUTION = PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def rows(self):
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)


ds = Dataset("readings.jsonl")
rows = ds.rows()
print(next(rows))
print(len(list(rows)), "more")
'''
write("exercises/step-the-rows/solution.py", ROWS_SOLUTION)
write(
    "exercises/step-the-rows/starter.py",
    ROWS_SOLUTION.replace("            for line in f:", "            for line in ...:").replace(
        "                    yield json.loads(line)", "                    ... json.loads(line)"
    ),
)
write(
    "exercises/step-the-rows/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints the first record, then 3 more."""
    printed = run()
    assert printed == "{'sensor': 'a', 'temperature': 18.5}\\n3 more\\n", f"Your program printed:\\n{printed}"


def test_rows_is_a_generator():
    """rows() gives one record per next()."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\\n\\n{"a": 2}\\n')
    rows = Dataset("two.jsonl").rows()
    assert next(rows) == {"a": 1}
    assert next(rows) == {"a": 2}
''',
)
write(
    "exercises/step-the-rows/wrong/return-not-yield.py",
    ROWS_SOLUTION.replace("                    yield json.loads(line)", "                    return json.loads(line)"),
)
write(
    "exercises/step-the-rows/wrong/typed-in.py",
    PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def rows(self):
        yield {"sensor": "a", "temperature": 18.5}


print({"sensor": "a", "temperature": 18.5})
print("3 more")
''',
)

write(
    "exercises/step-the-column/exercise.yaml",
    '''id: step-the-column
stage: fill_in
rev: 1
title: "Step 2: one column"
prompt: |
  Now one column out of the rows. Replace each `...` so `column(name)` yields that column's value from each record **that has it**, and the program prints:

  ```
  [18.5, 21.5, 20.0]
  []
  ```
hints:
  - "`name in row` is true when the record has that key; a record without it is skipped, not an error."
  - "The value is `row[name]`, and a generator hands it out with `yield`."
''',
)
COLUMN_SOLUTION = PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def rows(self):
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def column(self, name):
        for row in self.rows():
            if name in row:
                yield row[name]


ds = Dataset("readings.jsonl")
print(list(ds.column("temperature")))
print(list(ds.column("humidity")))
'''
write("exercises/step-the-column/solution.py", COLUMN_SOLUTION)
write(
    "exercises/step-the-column/starter.py",
    COLUMN_SOLUTION.replace("            if name in row:", "            if ... in row:").replace(
        "                yield row[name]", "                yield row[...]"
    ),
)
write(
    "exercises/step-the-column/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints the three temperatures, then an empty list."""
    printed = run()
    assert printed == "[18.5, 21.5, 20.0]\\n[]\\n", f"Your program printed:\\n{printed}"


def test_other_column():
    """column skips records without the key and yields one value per next()."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\\n{"b": 2}\\n{"a": 3}\\n')
    values = Dataset("two.jsonl").column("a")
    assert next(values) == 1
    assert list(values) == [3]
''',
)
write(
    "exercises/step-the-column/wrong/square-brackets.py",
    COLUMN_SOLUTION.replace(
        '''            if name in row:
                yield row[name]
''',
        '''            yield row[name]
''',
    ),
)
write(
    "exercises/step-the-column/wrong/typed-in.py",
    PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def column(self, name):
        yield 18.5


print([18.5, 21.5, 20.0])
print([])
''',
)

write(
    "exercises/step-the-summary/exercise.yaml",
    '''id: step-the-summary
stage: fill_in
rev: 1
title: "Step 3: the summary"
prompt: |
  Now the numbers. Replace each `...` so `summary(name)` returns the count, mean, min and max of a column, with a zero count and `None`s for a column no record has, and the program prints:

  ```
  {'count': 3, 'mean': 20.0, 'min': 18.5, 'max': 21.5}
  {'count': 0, 'mean': None, 'min': None, 'max': None}
  ```
hints:
  - "`list(self.column(name))` collects the column's values, so they can be counted and summed."
  - "The mean is the total divided by **how many values** there are, `len(values)`, not how many rows."
  - "An empty list is false, so `if not values:` is the missing-column case."
''',
)
SUMMARY_SOLUTION = PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def rows(self):
        with open(self.path) as f:
            for line in f:
                if line.strip():
                    yield json.loads(line)

    def column(self, name):
        for row in self.rows():
            if name in row:
                yield row[name]

    def summary(self, name):
        values = list(self.column(name))
        if not values:
            return {"count": 0, "mean": None, "min": None, "max": None}
        return {
            "count": len(values),
            "mean": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }


ds = Dataset("readings.jsonl")
print(ds.summary("temperature"))
print(ds.summary("humidity"))
'''
write("exercises/step-the-summary/solution.py", SUMMARY_SOLUTION)
write(
    "exercises/step-the-summary/starter.py",
    SUMMARY_SOLUTION.replace("        values = list(self.column(name))", "        values = list(self.column(...))")
    .replace("        if not values:", "        if not ...:")
    .replace('            "mean": sum(values) / len(values),', '            "mean": sum(values) / ...,'),
)
write(
    "exercises/step-the-summary/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints the temperature summary, then the empty one."""
    printed = run()
    assert printed == (
        "{'count': 3, 'mean': 20.0, 'min': 18.5, 'max': 21.5}\\n"
        "{'count': 0, 'mean': None, 'min': None, 'max': None}\\n"
    ), f"Your program printed:\\n{printed}"


def test_other_column():
    """The mean divides by the number of values, not rows."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\\n{"b": 2}\\n{"a": 3}\\n')
    assert Dataset("two.jsonl").summary("a") == {"count": 2, "mean": 2.0, "min": 1, "max": 3}
''',
)
write(
    "exercises/step-the-summary/wrong/mean-over-rows.py",
    SUMMARY_SOLUTION.replace('"mean": sum(values) / len(values),', '"mean": sum(values) / len(list(self.rows())),'),
)
write(
    "exercises/step-the-summary/wrong/typed-in.py",
    PRELUDE + '''class Dataset:
    def __init__(self, path):
        self.path = path

    def summary(self, name):
        return {"count": 3, "mean": 20.0, "min": 18.5, "max": 21.5}


print({"count": 3, "mean": 20.0, "min": 18.5, "max": 21.5})
print({"count": 0, "mean": None, "min": None, "max": None})
''',
)

write(
    "exercises/step-the-report/exercise.yaml",
    '''id: step-the-report
stage: fill_in
rev: 1
title: "Step 4: the report, and a test"
prompt: |
  The last two parts: a report written to a file, and a test. Replace each `...` so `write_report` writes the summary as one line, the test expects the right mean, and the program prints:

  ```
  temperature: count=3 mean=20.0 min=18.5 max=21.5
  1 passed
  ```
hints:
  - "Opening a file with `\\"w\\"` creates it, or replaces what was there."
  - "The report shows the summary's `mean`, so the f-string reads `s['mean']`."
  - "The mean of 18.5, 21.5 and 20.0 is their total divided by 3."
''',
)
REPORT_SOLUTION = PRELUDE + CLASS_HEAD + '''

def test_summary_of_temperature():
    ds = Dataset("readings.jsonl")
    assert ds.summary("temperature") == {"count": 3, "mean": 20.0, "min": 18.5, "max": 21.5}


ds = Dataset("readings.jsonl")
ds.write_report("temperature", "report.txt")
with open("report.txt") as f:
    print(f.read(), end="")
''' + RUNNER
write("exercises/step-the-report/solution.py", REPORT_SOLUTION)
write(
    "exercises/step-the-report/starter.py",
    REPORT_SOLUTION.replace('        with open(path, "w") as f:', "        with open(path, ...) as f:")
    .replace("mean={s['mean']}", "mean={s[...]}")
    .replace('"mean": 20.0, "min": 18.5', '"mean": ..., "min": 18.5'),
)
write(
    "exercises/step-the-report/test_exercise.py",
    '''from checks import function, run


def test_the_output():
    """Prints the report line, then 1 passed."""
    printed = run()
    assert printed == "temperature: count=3 mean=20.0 min=18.5 max=21.5\\n1 passed\\n", f"Your program printed:\\n{printed}"


def test_other_report():
    """write_report writes the one-line report for another column and file."""
    Dataset = function("Dataset")
    with open("two.jsonl", "w") as f:
        f.write('{"a": 1}\\n{"b": 2}\\n{"a": 3}\\n')
    Dataset("two.jsonl").write_report("a", "two-report.txt")
    with open("two-report.txt") as f:
        assert f.read() == "a: count=2 mean=2.0 min=1 max=3\\n"
''',
)
write(
    "exercises/step-the-report/wrong/wrong-field.py",
    REPORT_SOLUTION.replace("mean={s['mean']}", "mean={s['count']}"),
)
write(
    "exercises/step-the-report/wrong/typed-in.py",
    PRELUDE
    + CLASS_HEAD.replace(
        '''            f.write(f"{name}: count={s['count']} mean={s['mean']} min={s['min']} max={s['max']}\\n")''',
        '''            f.write("temperature: count=3 mean=20.0 min=18.5 max=21.5\\n")''',
    )
    + '''

print("temperature: count=3 mean=20.0 min=18.5 max=21.5")
print("1 passed")
''',
)

print("ml.m2.checkpoint written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
