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
        values = list(self.column(...))
        if not ...:
            return {"count": 0, "mean": None, "min": None, "max": None}
        return {
            "count": len(values),
            "mean": sum(values) / ...,
            "min": min(values),
            "max": max(values),
        }


ds = Dataset("readings.jsonl")
print(ds.summary("temperature"))
print(ds.summary("humidity"))
