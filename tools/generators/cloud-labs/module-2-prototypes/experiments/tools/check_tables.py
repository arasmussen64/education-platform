"""Scan Markdown files for table rows whose number of cells differs from the
table's header row: the usual sign of an unescaped pipe inside a cell."""
import re
import sys

UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")

for name in sys.argv[1:]:
    lines = open(name, encoding="utf-8").read().split("\n")
    header = None
    problems = 0
    for number, line in enumerate(lines, 1):
        if line.startswith("|"):
            cells = len(UNESCAPED_PIPE.findall(line)) - 1
            if header is None:
                header = cells
            elif cells != header:
                problems += 1
                print(f"{name}:{number}: {cells} cells, header has {header}: {line[:100]}")
        else:
            header = None
    print(f"{name}: {problems} suspicious rows")
