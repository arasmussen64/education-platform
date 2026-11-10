import json

LINES = """{"sensor": "a", "temperature": 18.5}
{"sensor": "b", "temperature": 21.5}
{"sensor": "c"}
{"sensor": "d", "temperature": 20.0}
"""
with open("readings.jsonl", "w") as f:
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
            f.write(f"{name}: count={s['count']} mean={s['mean']} min={s['max']} max={s['min']}\n")


ds = Dataset("readings.jsonl")
print(len(list(ds.rows())), "rows")
print(ds.summary("temperature"))
ds.write_report("temperature", "report.txt")
with open("report.txt") as f:
    print(f.read(), end="")
