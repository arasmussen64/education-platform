import json

LINES = """{"player": "ada", "score": 12}
{"player": "bo", "score": 30}
{"player": "cy"}
{"player": "di", "score": 18}
"""
with open("scores.jsonl", "w") as f:
    f.write(LINES)


class Dataset:
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
            f.write(f"{name}: count={s['count']} mean={s['mean']} min={s['min']} max={s['max']}\n")


def test_summary_of_score():
    ds = Dataset("scores.jsonl")
    assert ds.summary("score") == {'count': 3, 'mean': 20.0, 'min': 12, 'max': 30}


def test_summary_of_a_missing_column():
    ds = Dataset("scores.jsonl")
    assert ds.summary("nothing") == {"count": 0, "mean": None, "min": None, "max": None}


ds = Dataset("scores.jsonl")
print(len(list(ds.rows())), "rows")
print(ds.summary("score"))
ds.write_report("score", "report.txt")
with open("report.txt") as f:
    print(f.read(), end="")

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
