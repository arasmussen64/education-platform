TEXT = """INFO started
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
            f.write(f"WARN={self.count('WARN')} ERROR={self.count('ERROR')}\n")


log = Log("app.log")
print(len(list(log.lines())), "lines")
print(list(log.level("WARN")))
log.write_summary("summary.txt")
with open("summary.txt") as f:
    print(f.read(), end="")
