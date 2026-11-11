"""Writes the topic ml.py.json-and-nested-data (Module 2's seventh and last
topic before its checkpoint). Run from the repository root. Files are
written as bytes with LF endings."""

import pathlib

ROOT = pathlib.Path("content/topics/ml.py.json-and-nested-data")


def write(relative: str, text: str) -> None:
    path = ROOT / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


write(
    "topic.yaml",
    '''id: ml.py.json-and-nested-data
kind: topic
status: ready
title: "JSON and nested data"
summary: "Read and write JSON, walk nested data safely, and validate what came in."
prerequisites: [ml.py.dataclasses-and-typing, py.csv-data]
estimated_minutes: 50
rev: 1
objectives:
  - "Read and write JSON, as text and as files."
  - "Walk nested lists and dicts without crashing on what's missing."
  - "Turn records into dataclasses and back, and validate what came in before using it."
resources:
  - title: "The Python Tutorial: Saving structured data with json (section 7.2.2) (Python Software Foundation)"
    url: https://docs.python.org/3/tutorial/inputoutput.html#saving-structured-data-with-json
    type: reading
    use: link
    license: PSF License Version 2
  - title: "The Python Standard Library: json, the table of how JSON and Python types correspond (Python Software Foundation)"
    url: https://docs.python.org/3/library/json.html#encoders-and-decoders
    type: reading
    use: link
    license: PSF License Version 2
practice:
  - example-json-round-trip
  - parsons-load-and-walk
  - mcq-what-json-can-hold
  - predict-missing-keys
  - mcq-validate-first
  - fill-safe-lookup
  - write-readings
prove:
  build: build-validate-orders
  debug: debug-nested-walk
  explain:
    prompt: |
      A teammate's script reads a JSON file that a partner company sends every night. Last night it crashed with `KeyError: 'email'`; the night before, with `TypeError` on `age + 1` because `age` had arrived as `"42"`. In your own words: what does `json.loads` hand back, in Python terms, and what can and can't be in it? Why does walking nested data need `.get()` and `isinstance()` rather than square brackets everywhere? Where in the program should the checking happen, and why there rather than at every use? And what would turning each checked record into a dataclass buy the rest of the program?
    rubric:
      - id: shape
        required: true
        description: "json.loads gives dicts, lists, strings, numbers, booleans and None, nested; no sets, tuples, dates or custom objects, and object keys are always strings."
      - id: safe-walk
        required: true
        description: "Square brackets raise on a missing key or an unexpected type; .get() with a default and isinstance() let the program decide what to do with data it didn't expect."
      - id: boundary
        required: true
        description: "Validate once at the boundary, right after reading, rejecting or fixing bad records there, so everything after can trust the data instead of defending at every use."
      - id: records
        required: false
        description: "A dataclass gives the checked record a fixed shape with named fields, so a typo is an AttributeError at once and the rest of the program knows exactly what it holds."
    model_answer: |
      json.loads turns JSON text into ordinary Python values: objects become dicts whose keys are always strings, arrays become lists, and the leaves are strings, numbers, True, False or None. That's the whole menu; there are no sets, tuples, dates or your own classes in JSON, so anything like that has to be rebuilt on the way in. The data is nested, and square brackets assume the shape is exactly what you expect: record["email"] raises KeyError the first night a record has no email, and record["address"]["city"] raises TypeError the night address is null. .get() with a default and isinstance() checks let the program notice and decide, instead of crashing. The checking belongs in one place, right after the file is read: a function that looks at each record, rejects or repairs the bad ones and logs them, and passes on only records with the right keys and types. Then nothing downstream has to defend itself, and when the partner changes the format there's one function to update. Turning each good record into a dataclass is the last step of that boundary: from then on it's record.age, an int, with a fixed set of fields, and a typo fails at once instead of being an empty dict somewhere later.
review_pool:
  - review-predict-dumps-types
  - review-mcq-loads-or-load
  - review-mcq-asdict
  - review-mcq-where-to-validate
  - review-sum-nested-lists
# What this topic teaches. Each question names the skills it tests, so a
# missed question can come back as a different one on the same skill
# (ADR-0011).
skills:
  - id: json-io
    description: "Read and write JSON with loads, dumps, load and dump, and know how its types map to Python's"
  - id: safe-walk
    description: "Walk nested dicts and lists with .get, in and isinstance instead of crashing on what's missing"
  - id: records
    description: "Turn a dict record into a dataclass and back with asdict"
  - id: validate
    description: "Check data's shape once, at the boundary, before the rest of the program trusts it"
''',
)

write(
    "lesson.mdx",
    '''<Intro>

Almost every piece of data that arrives from somewhere else arrives as JSON: web APIs, config files, the records a partner sends every night, the metadata beside a trained model. It's text, and Python turns it into dicts and lists with one call. The hard part isn't reading it; it's that data from somewhere else is never quite the shape you expected.

The main resource is the tutorial's short section **7.2.2, Saving structured data with json**, then the **table of how JSON types map to Python types** in the `json` module's reference. About 10 minutes. Watch for:

- **`dumps` and `loads`** work on strings; **`dump` and `load`** work on open files. The `s` is for string.
- **The type table:** object → dict, array → list, `true` → `True`, `null` → `None`. Keys are always strings.
- **What JSON can't hold:** sets, tuples (they become arrays), dates, your own classes.

Then the Recap below adds what the docs don't say: how to walk nested data without crashing, and where to check it.

</Intro>

<Resource index={0} />

<Recap>

- **Four functions.** `json.dumps(value)` gives a string; `json.loads(text)` reads one. `json.dump(value, file)` and `json.load(file)` do the same with an open file. `indent=2` makes the output readable.
- **The type map.** JSON object ↔ `dict` (keys become strings, even if they were numbers), array ↔ `list`, string ↔ `str`, number ↔ `int` or `float`, `true`/`false` ↔ `True`/`False`, `null` ↔ `None`. A set or a dataclass raises `TypeError: not JSON serializable`; convert first (`sorted(the_set)`, `asdict(record)`).
- **Walking nested data.** `data["user"]["langs"][1]` reaches in; each bracket assumes the shape is right. For data from outside, assume it isn't: `record.get("email")` gives `None` instead of raising; `record.get("tags", [])` gives something safe to loop over; `"phone" in record` asks first; `isinstance(address, dict)` checks before reaching into it.
- **Validate at the boundary.** Check each record once, right after reading: the keys it must have, the types they must be. Reject or repair the bad ones there, and say which. Everything after that can trust the data, so it stays simple.
- **Records in, dataclasses out.** `Reading(r["sensor"], float(r["value"]))` turns a checked dict into a record with a fixed shape; `asdict(reading)` turns it back for `json.dumps`. A typo becomes an `AttributeError` at once instead of an empty dict somewhere later.
- **JSON Lines.** Big datasets are often one JSON object per line (`.jsonl`), so a program can read and `json.loads` one line at a time, which is a generator's job. Checkpoint 2 builds on exactly this.
- **In machine learning:** training data, labels, experiment configs and model cards all travel as JSON; the first function in most pipelines is the one that reads it and refuses what doesn't fit.

</Recap>
''',
)

# --- practice: recall --------------------------------------------------------

write(
    "recall/parsons-load-and-walk.yaml",
    '''id: parsons-load-and-walk
type: parsons
rev: 1
prompt: |
  Put the lines in order so the program reads JSON text and prints `sql`. One line is a decoy that doesn't belong.
lines:
  - 'import json'
  - "text = '{\\"user\\": {\\"name\\": \\"Cy\\", \\"langs\\": [\\"py\\", \\"sql\\"]}}'"
  - 'data = json.loads(text)'
  - 'print(data["user"]["langs"][1])'
distractors:
  - 'data = json.load(text)'
explanation: |
  `json.loads` reads a **string**; `json.load` reads an open file, and given a string it fails. Once loaded, the JSON object is a dict and the array a list, so square brackets walk down to the second language.
skills: [json-io]
''',
)

write(
    "recall/mcq-what-json-can-hold.yaml",
    '''id: mcq-what-json-can-hold
type: mcq
rev: 1
prompt: |
  Which of these can `json.dumps` **not** write as it is?
choices:
  - '`{"a": [1, 2.5, None]}`'
  - '`["x", True]`'
  - '`{1, 2, 3}`, a set'
  - '`{"nested": {"deeper": []}}`'
answer: 2
explanation: |
  JSON has objects, arrays, strings, numbers, `true`, `false` and `null`, and nothing else. Dicts, lists, `None` and booleans all map onto those; a set doesn't, so `json.dumps` raises `TypeError: Object of type set is not JSON serializable`. Convert it first, for example `sorted(the_set)`, which is a list.
skills: [json-io]
''',
)

write(
    "recall/predict-missing-keys.yaml",
    '''id: predict-missing-keys
type: predict_output
rev: 1
prompt: |
  A record with some keys missing, asked about safely. What does the program print?
code: |
  data = {"name": "Bo", "address": {"city": "Oslo"}}
  print(data.get("email"))
  print(data.get("email", "unknown"))
  print(data["address"].get("zip", "none"))
  print("phone" in data)
expected_output: |
  None
  unknown
  none
  False
explanation: |
  `.get()` with no default gives `None` for a missing key, and with a default gives that instead; neither raises. `data["address"]` is fine because the key is there, and `.get("zip", "none")` on the inner dict is safe again. `in` asks whether a key exists. Square brackets would have raised `KeyError` for `email`, `zip` and `phone`.
skills: [safe-walk]
''',
)

write(
    "recall/mcq-validate-first.yaml",
    '''id: mcq-validate-first
type: mcq
rev: 1
prompt: |
  A record read from a partner's file is `{"age": "42"}`, and later `record["age"] + 1` fails with `TypeError`. What's the right fix?
choices:
  - 'Write `record["age"] + "1"`, so both sides are strings'
  - 'Check the record where it''s read: if `age` isn''t an int (or a string of digits you choose to convert), reject or convert it once, there; then the rest of the program can trust it'
  - 'Wrap every use of `age`, everywhere in the program, in `try`/`except`'
  - 'Call `json.loads` on the value again'
answer: 1
explanation: |
  The data is wrong at the point where it came in, so that's where to deal with it: one check, one conversion or rejection, and a message saying which record was bad. Fixing it at each use spreads the same defence through the whole program, and `+ "1"` makes the bug worse by hiding it.
skills: [validate]
''',
)

write(
    "recall/review-predict-dumps-types.yaml",
    '''id: review-predict-dumps-types
type: predict_output
rev: 1
prompt: |
  Python values out to JSON, and JSON text back in. What does the program print?
code: |
  import json

  print(json.dumps({"ok": True, "n": None, 1: "x"}))
  print(json.loads('[1, 2.0, "3"]'))
expected_output: |
  {"ok": true, "n": null, "1": "x"}
  [1, 2.0, '3']
explanation: |
  Out: `True` becomes `true`, `None` becomes `null`, and the key `1` becomes the string `"1"`, because JSON object keys are always strings. In: `1` is an int, `2.0` a float, and `"3"` stays a string; `json.loads` never guesses that a string is a number.
skills: [json-io]
''',
)

write(
    "recall/review-mcq-loads-or-load.yaml",
    '''id: review-mcq-loads-or-load
type: mcq
rev: 1
prompt: |
  You've read a web API's response into a string called `body`. Which call turns it into Python data?
choices:
  - '`json.load(body)`'
  - '`json.loads(body)`'
  - '`json.dumps(body)`'
  - '`json.dump(body)`'
answer: 1
explanation: |
  The `s` stands for string: `loads` reads a string, `dumps` writes one. `load` and `dump` take an open file. `dumps` and `dump` go the other way, from Python to JSON.
skills: [json-io]
''',
)

write(
    "recall/review-mcq-asdict.yaml",
    '''id: review-mcq-asdict
type: mcq
rev: 1
prompt: |
  ```python
  @dataclass
  class Reading:
      sensor: str
      value: float
  ```

  You have `r = Reading("a", 1.5)` and want to write it as JSON. What works?
choices:
  - '`json.dumps(r)`'
  - '`json.dumps(asdict(r))`, giving `{"sensor": "a", "value": 1.5}`'
  - '`json.dumps(str(r))`'
  - '`json.dumps(list(r))`'
answer: 1
explanation: |
  `json.dumps` doesn't know how to write your class and raises `TypeError`. `asdict`, from `dataclasses`, turns the record into a plain dict of its fields, which JSON can hold. `str(r)` would write the repr as one string, not a JSON object with fields.
skills: [records, json-io]
''',
)

write(
    "recall/review-mcq-where-to-validate.yaml",
    '''id: review-mcq-where-to-validate
type: mcq
rev: 1
prompt: |
  A program reads records from a file, then passes them through five functions. Where should it check that each record has the right keys and types?
choices:
  - 'In each of the five functions, so every one is safe on its own'
  - 'Once, right after reading, in one function that rejects or repairs bad records and says which; the five functions then trust what they get'
  - 'Nowhere: `json.loads` already checks the data'
  - 'Only in the last function, where the results are printed'
answer: 1
explanation: |
  `json.loads` checks that the text is JSON, not that it's *your* shape. Checking in every function repeats the same code five times and still misses the point where the bad record can be named and logged. One check at the boundary keeps the rest of the program simple and gives one place to update when the format changes.
skills: [validate]
''',
)

# --- practice: exercises -------------------------------------------------------

write(
    "exercises/example-json-round-trip/exercise.yaml",
    '''id: example-json-round-trip
stage: worked_example
rev: 1
title: "A JSON round trip"
prompt: |
  This program writes a record as JSON text and reads it back, then does the same through a file. Press **Run**, then read how each part works.
steps:
  - label: "Python to JSON text"
    lines: "1-6"
    note: "`json.dumps` turns the dict into a string that looks almost like Python, with double quotes. The nested list and dict come along."
  - label: "JSON text to Python"
    lines: "8-10"
    note: "`json.loads` reads the string back into a new dict, equal to the original, and square brackets walk into it."
  - label: "The type map"
    lines: "12"
    note: "`True` is written as `true` and `None` as `null`: JSON's words for them. The same map runs backwards on the way in."
  - label: "Through a file"
    lines: "14-19"
    note: "`dump` and `load`, without the `s`, work on an open file; `indent=2` makes the file readable. `.get` with a default reads a key that might not be there."
''',
)
write(
    "exercises/example-json-round-trip/solution.py",
    '''import json

record = {"name": "Ada", "tags": ["math", "code"], "scores": {"quiz": 9, "exam": 17}}
text = json.dumps(record)
print(text)
print(type(text).__name__)

back = json.loads(text)
print(back == record)
print(back["scores"]["exam"])

print(json.dumps({"ok": True, "missing": None}))

with open("record.json", "w") as f:
    json.dump(record, f, indent=2)
with open("record.json") as f:
    loaded = json.load(f)
print(loaded["tags"][0])
print(loaded.get("email", "no email"))
''',
)
write(
    "exercises/example-json-round-trip/test_exercise.py",
    '''from checks import run


def test_the_walkthrough():
    """Prints the JSON text, str, True, 17, the true/null line, math and no email."""
    assert run() == (
        '{"name": "Ada", "tags": ["math", "code"], "scores": {"quiz": 9, "exam": 17}}\\n'
        "str\\nTrue\\n17\\n"
        '{"ok": true, "missing": null}\\n'
        "math\\nno email\\n"
    )
''',
)

write(
    "exercises/fill-safe-lookup/exercise.yaml",
    '''id: fill-safe-lookup
stage: fill_in
rev: 1
title: "A safe lookup"
prompt: |
  `city_of(record)` should return a person's city, or `"unknown"` when the record has no address, the address isn't a dict, or the address has no city. Replace each `...` so the program prints:

  ```
  Ada Oslo
  Bo unknown
  Cy unknown
  Di unknown
  ```

  Until every `...` is replaced, Python can't run the program at all, and shows a syntax error.
hints:
  - "`record.get(\\"address\\")` gives `None` when the key is missing, instead of raising."
  - "`isinstance(address, dict)` is false for `None` and for a string, so one check covers both."
  - "`.get(\\"city\\", \\"unknown\\")` handles the address with no city."
skills: [safe-walk]
''',
)
PEOPLE = '''people = [
    {"name": "Ada", "address": {"city": "Oslo"}},
    {"name": "Bo"},
    {"name": "Cy", "address": None},
    {"name": "Di", "address": {"street": "Main"}},
]
for person in people:
    print(person["name"], city_of(person))
'''
write(
    "exercises/fill-safe-lookup/starter.py",
    '''def city_of(record):
    address = record.get(...)
    if not isinstance(address, ...):
        return "unknown"
    return address.get("city", ...)


''' + PEOPLE,
)
write(
    "exercises/fill-safe-lookup/solution.py",
    '''def city_of(record):
    address = record.get("address")
    if not isinstance(address, dict):
        return "unknown"
    return address.get("city", "unknown")


''' + PEOPLE,
)
write(
    "exercises/fill-safe-lookup/test_exercise.py",
    '''from checks import function, run


def test_these_people():
    """Prints Oslo for Ada and unknown for the other three."""
    printed = run()
    assert printed == "Ada Oslo\\nBo unknown\\nCy unknown\\nDi unknown\\n", f"Your program printed:\\n{printed}"


def test_other_records():
    """Works for a city, no address, an address that's a string, and an address with no city."""
    city_of = function("city_of")
    assert city_of({"address": {"city": "Rome"}}) == "Rome"
    assert city_of({}) == "unknown"
    assert city_of({"address": "Oslo"}) == "unknown"
    assert city_of({"address": {}}) == "unknown"
''',
)
write(
    "exercises/fill-safe-lookup/wrong/square-brackets.py",
    '''def city_of(record):
    address = record["address"]
    if not isinstance(address, dict):
        return "unknown"
    return address["city"]


''' + PEOPLE,
)
write(
    "exercises/fill-safe-lookup/wrong/typed-in.py",
    '''def city_of(record):
    if record["name"] == "Ada":
        return "Oslo"
    return "unknown"


''' + PEOPLE,
)

write(
    "exercises/write-readings/exercise.yaml",
    '''id: write-readings
stage: write
rev: 1
title: "Readings in and out"
prompt: |
  A sensor sends readings as JSON: `[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2}]`. Write a dataclass `Reading` with fields `sensor` (a str) and `value` (a float), a function `parse_readings(text)` that turns such JSON text into a list of `Reading`s with `value` converted to a float, and a function `to_json(readings)` that turns a list of `Reading`s back into JSON text. Then print the parsed readings and the JSON made from them:

  ```
  [Reading(sensor='a', value=1.5), Reading(sensor='b', value=2.0)]
  [{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]
  ```
hints:
  - "`json.loads(text)` gives a list of dicts; build a `Reading(r[\\"sensor\\"], float(r[\\"value\\"]))` from each."
  - "`asdict`, imported from `dataclasses`, turns a `Reading` into a dict that `json.dumps` can write."
skills: [records, json-io]
''',
)
write("exercises/write-readings/starter.py", "")
write(
    "exercises/write-readings/solution.py",
    '''import json
from dataclasses import asdict, dataclass


@dataclass
class Reading:
    sensor: str
    value: float


def parse_readings(text):
    return [Reading(r["sensor"], float(r["value"])) for r in json.loads(text)]


def to_json(readings):
    return json.dumps([asdict(r) for r in readings])


readings = parse_readings('[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2}]')
print(readings)
print(to_json(readings))
''',
)
write(
    "exercises/write-readings/test_exercise.py",
    '''import json

from checks import function, run


def test_the_output():
    """Prints the two readings, then the JSON made from them."""
    printed = run()
    assert printed == (
        "[Reading(sensor='a', value=1.5), Reading(sensor='b', value=2.0)]\\n"
        '[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]\\n'
    ), f"Your program printed:\\n{printed}"


def test_parse_converts_values():
    """parse_readings turns values into floats, and an empty array into an empty list."""
    parse_readings = function("parse_readings")
    readings = parse_readings('[{"sensor": "z", "value": "3.5"}]')
    assert readings[0].sensor == "z"
    assert readings[0].value == 3.5
    assert isinstance(readings[0].value, float)
    assert parse_readings("[]") == []


def test_round_trip():
    """to_json of parsed readings reads back as the same records."""
    parse_readings = function("parse_readings")
    to_json = function("to_json")
    text = '[{"sensor": "q", "value": 1.0}, {"sensor": "r", "value": 0.5}]'
    assert json.loads(to_json(parse_readings(text))) == json.loads(text)
''',
)
write(
    "exercises/write-readings/wrong/keeps-strings.py",
    '''import json
from dataclasses import asdict, dataclass


@dataclass
class Reading:
    sensor: str
    value: float


def parse_readings(text):
    return [Reading(r["sensor"], r["value"]) for r in json.loads(text)]


def to_json(readings):
    return json.dumps([asdict(r) for r in readings])


readings = parse_readings('[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]')
print(readings)
print(to_json(readings))
''',
)
write(
    "exercises/write-readings/wrong/typed-in.py",
    '''from dataclasses import dataclass


@dataclass
class Reading:
    sensor: str
    value: float


def parse_readings(text):
    return [Reading("a", 1.5), Reading("b", 2.0)]


def to_json(readings):
    return '[{"sensor": "a", "value": 1.5}, {"sensor": "b", "value": 2.0}]'


print(parse_readings(""))
print(to_json([]))
''',
)

# --- proof ------------------------------------------------------------------

write(
    "exercises/build-validate-orders/exercise.yaml",
    '''id: build-validate-orders
stage: build
rev: 1
title: "Validate the orders"
prompt: |
  Orders arrive as JSON text: a list of records that **should** each have an `id` (an int), an `item` (a non-empty string) and a `qty` (an int greater than 0). Some won't. Starting from a blank editor, write a dataclass `Order` with those three fields, and a function `load_orders(text)` that returns two things: a list of `Order`s for the records that follow the rules, and a list of the **positions** (0, 1, 2, ...) of the records that don't. A record that isn't a dict, lacks a key, or has a value of the wrong type is bad. Don't repair records: `"5"` is not a quantity, even if `int("5")` would be.

  Then print the result for this text:

  ```python
  text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
  ```

  ```
  [Order(id=1, item='pen', qty=2)]
  [1, 2, 3]
  ```

  The checks call `load_orders` with other records too: all good, missing keys, a float quantity, a record that's a number.
skills: [validate, records, json-io]
''',
)
write("exercises/build-validate-orders/starter.py", "")
write(
    "exercises/build-validate-orders/solution.py",
    '''import json
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def is_valid(record):
    if not isinstance(record, dict):
        return False
    if not isinstance(record.get("id"), int):
        return False
    item = record.get("item")
    if not isinstance(item, str) or item == "":
        return False
    qty = record.get("qty")
    return isinstance(qty, int) and qty > 0


def load_orders(text):
    orders = []
    bad = []
    for position, record in enumerate(json.loads(text)):
        if is_valid(record):
            orders.append(Order(record["id"], record["item"], record["qty"]))
        else:
            bad.append(position)
    return orders, bad


text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
orders, bad = load_orders(text)
print(orders)
print(bad)
''',
)
write(
    "exercises/build-validate-orders/test_exercise.py",
    '''from dataclasses import is_dataclass

from checks import function, run

# Hidden tests: the learner sees each docstring and whether it passed, but
# not the failure messages (v1 spec, F7).


def test_the_output():
    """Prints the one good order, then the positions 1, 2 and 3."""
    assert run() == "[Order(id=1, item='pen', qty=2)]\\n[1, 2, 3]\\n"


def test_good_records():
    """All-good records give Order dataclasses with the right fields and no bad positions."""
    load_orders = function("load_orders")
    orders, bad = load_orders('[{"id": 7, "item": "cup", "qty": 3}, {"id": 8, "item": "lid", "qty": 1}]')
    assert bad == []
    assert len(orders) == 2
    assert is_dataclass(orders[0])
    assert (orders[1].id, orders[1].item, orders[1].qty) == (8, "lid", 1)


def test_bad_records():
    """A float quantity, a record that's a number, a missing key and a string quantity are all bad."""
    load_orders = function("load_orders")
    text = '[{"id": 1, "item": "pen", "qty": 2.0}, 7, {"item": "x", "qty": 1}, {"id": 9, "item": "y", "qty": 3}, {"id": 5, "item": "z", "qty": "5"}]'
    orders, bad = load_orders(text)
    assert bad == [0, 1, 2, 4]
    assert [(o.id, o.item, o.qty) for o in orders] == [(9, "y", 3)]
    assert load_orders("[]") == ([], [])
''',
)
write(
    "exercises/build-validate-orders/wrong/repairs-strings.py",
    '''import json
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def load_orders(text):
    orders = []
    bad = []
    for position, record in enumerate(json.loads(text)):
        try:
            qty = int(record["qty"])
            if record["item"] and qty > 0:
                orders.append(Order(int(record["id"]), record["item"], qty))
            else:
                bad.append(position)
        except (KeyError, TypeError, ValueError):
            bad.append(position)
    return orders, bad


text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
orders, bad = load_orders(text)
print(orders)
print(bad)
''',
)
write(
    "exercises/build-validate-orders/wrong/accepts-zero.py",
    '''import json
from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def is_valid(record):
    if not isinstance(record, dict):
        return False
    if not isinstance(record.get("id"), int):
        return False
    item = record.get("item")
    if not isinstance(item, str) or item == "":
        return False
    qty = record.get("qty")
    return isinstance(qty, int) and qty >= 0


def load_orders(text):
    orders = []
    bad = []
    for position, record in enumerate(json.loads(text)):
        if is_valid(record):
            orders.append(Order(record["id"], record["item"], record["qty"]))
        else:
            bad.append(position)
    return orders, bad


text = '[{"id": 1, "item": "pen", "qty": 2}, {"id": 2, "item": "", "qty": 1}, {"id": 3, "item": "ink", "qty": "5"}, {"id": 4, "item": "pad", "qty": 0}]'
orders, bad = load_orders(text)
print(orders)
print(bad)
''',
)
write(
    "exercises/build-validate-orders/wrong/typed-in.py",
    '''from dataclasses import dataclass


@dataclass
class Order:
    id: int
    item: str
    qty: int


def load_orders(text):
    return [Order(1, "pen", 2)], [1, 2, 3]


print([Order(1, "pen", 2)])
print([1, 2, 3])
''',
)

write(
    "exercises/debug-nested-walk/exercise.yaml",
    '''id: debug-nested-walk
stage: debug
rev: 1
title: "A nested walk"
prompt: |
  This program should add up what each user has spent and print:

  ```
  Ada 30.0
  Bo 0
  Cy 0
  ```

  It has two bugs. Run it, read the error, fix it, run it again. One is in how the JSON is read; the other shows up only for a user without an `orders` key.
skills: [json-io, safe-walk]
''',
)
write(
    "exercises/debug-nested-walk/starter.py",
    '''import json

text = '[{"name": "Ada", "orders": [{"total": 12.5}, {"total": 17.5}]}, {"name": "Bo"}, {"name": "Cy", "orders": []}]'
users = json.load(text)

for user in users:
    spent = 0
    for order in user["orders"]:
        spent = spent + order["total"]
    print(user["name"], spent)
''',
)
write(
    "exercises/debug-nested-walk/solution.py",
    '''import json

text = '[{"name": "Ada", "orders": [{"total": 12.5}, {"total": 17.5}]}, {"name": "Bo"}, {"name": "Cy", "orders": []}]'
users = json.loads(text)

for user in users:
    spent = 0
    for order in user.get("orders", []):
        spent = spent + order["total"]
    print(user["name"], spent)
''',
)
write(
    "exercises/debug-nested-walk/test_exercise.py",
    '''from checks import run, run_with

EXPECTED = "Ada 30.0\\nBo 0\\nCy 0\\n"


def test_the_output():
    """Prints each user's name and total."""
    printed = run()
    assert printed == EXPECTED, f"Expected this:\\n{EXPECTED}\\nYour program printed:\\n{printed}"


def test_other_users():
    """Works for other users, including one with no orders key."""
    printed = run_with({"text": '[{"name": "Di", "orders": [{"total": 2}]}, {"name": "Ed"}]'})
    assert printed == "Di 2\\nEd 0\\n", f"With Di and Ed it printed:\\n{printed}"
''',
)
write(
    "exercises/debug-nested-walk/wrong/only-loads-fixed.py",
    '''import json

text = '[{"name": "Ada", "orders": [{"total": 12.5}, {"total": 17.5}]}, {"name": "Bo"}, {"name": "Cy", "orders": []}]'
users = json.loads(text)

for user in users:
    spent = 0
    for order in user["orders"]:
        spent = spent + order["total"]
    print(user["name"], spent)
''',
)
write(
    "exercises/debug-nested-walk/wrong/typed-in.py",
    '''text = '[{"name": "Ada", "orders": [{"total": 12.5}, {"total": 17.5}]}, {"name": "Bo"}, {"name": "Cy", "orders": []}]'
print("Ada 30.0")
print("Bo 0")
print("Cy 0")
''',
)

# --- review pool: a code exercise -------------------------------------------

write(
    "exercises/review-sum-nested-lists/exercise.yaml",
    '''id: review-sum-nested-lists
stage: review_code
rev: 1
title: "Add up the nested lists"
prompt: |
  `data` is a dict whose values are lists of numbers. Print the total of every number in it:

  ```
  6
  ```

  Keep the starting line: the checks run your program with other data too.
skills: [safe-walk]
''',
)
write("exercises/review-sum-nested-lists/starter.py", 'data = {"a": [1, 2], "b": [3]}\n')
write(
    "exercises/review-sum-nested-lists/solution.py",
    '''data = {"a": [1, 2], "b": [3]}
print(sum(sum(values) for values in data.values()))
''',
)
write(
    "exercises/review-sum-nested-lists/test_exercise.py",
    '''from checks import run, run_with


def test_this_data():
    """Prints 6."""
    assert run() == "6\\n"


def test_other_data():
    """Prints 9 for {"x": [], "y": [4, 5]}."""
    assert run_with({"data": {"x": [], "y": [4, 5]}}) == "9\\n"
''',
)
write(
    "exercises/review-sum-nested-lists/wrong/counts-the-numbers.py",
    '''data = {"a": [1, 2], "b": [3]}
print(sum(len(values) for values in data.values()))
''',
)
write(
    "exercises/review-sum-nested-lists/wrong/typed-in.py",
    '''data = {"a": [1, 2], "b": [3]}
print(6)
''',
)

print("ml.py.json-and-nested-data written:", sum(1 for _ in ROOT.rglob("*") if _.is_file()), "files")
