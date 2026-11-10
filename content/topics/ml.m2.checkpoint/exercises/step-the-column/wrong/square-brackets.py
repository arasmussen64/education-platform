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
            yield row[name]


ds = Dataset("readings.jsonl")
print(list(ds.column("temperature")))
print(list(ds.column("humidity")))
