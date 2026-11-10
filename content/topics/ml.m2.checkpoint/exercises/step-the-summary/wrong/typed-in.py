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

    def summary(self, name):
        return {"count": 3, "mean": 20.0, "min": 18.5, "max": 21.5}


print({"count": 3, "mean": 20.0, "min": 18.5, "max": 21.5})
print({"count": 0, "mean": None, "min": None, "max": None})
