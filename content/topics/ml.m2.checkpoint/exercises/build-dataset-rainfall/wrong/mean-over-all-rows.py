import json

LINES = """{"station": "north", "mm": 3.0}
{"station": "south", "mm": 0.0}
{"station": "east"}
{"station": "west", "mm": 7.5}
"""
with open("rain.jsonl", "w") as f:
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
            "mean": sum(values) / len(list(self.rows())),
            "min": min(values),
            "max": max(values),
        }

    def write_report(self, name, path):
        s = self.summary(name)
        with open(path, "w") as f:
            f.write(f"{name}: count={s['count']} mean={s['mean']} min={s['min']} max={s['max']}\n")


def test_summary_of_mm():
    ds = Dataset("rain.jsonl")
    assert ds.summary("mm") == {'count': 3, 'mean': 3.5, 'min': 0.0, 'max': 7.5}


def test_summary_of_a_missing_column():
    ds = Dataset("rain.jsonl")
    assert ds.summary("nothing") == {"count": 0, "mean": None, "min": None, "max": None}


ds = Dataset("rain.jsonl")
print(len(list(ds.rows())), "rows")
print(ds.summary("mm"))
ds.write_report("mm", "report.txt")
with open("report.txt") as f:
    print(f.read(), end="")

passed = 0
for name in sorted(dir()):
    if name.startswith("test_"):
        globals()[name]()
        passed = passed + 1
print(passed, "passed")
