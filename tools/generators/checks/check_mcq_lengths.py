"""Lists every mcq(...) call in a generator whose right answer is the longest
choice (or ties), so they can all be fixed before the generator runs.
Usage: python check_mcq_lengths.py <generator.py>"""

import ast
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).read_text(encoding="utf-8")
bad = 0
for node in ast.walk(ast.parse(source)):
    if isinstance(node, ast.Call) and getattr(node.func, "id", "") == "mcq":
        item_id = ast.literal_eval(node.args[0])
        choices = [ast.literal_eval(c) for c in node.args[2].elts]
        answer = ast.literal_eval(node.args[3])
        lengths = [len(c) for c in choices]
        if lengths[answer] >= max(length for i, length in enumerate(lengths) if i != answer):
            bad += 1
            print("LONGEST", item_id, lengths, "answer", answer)
print(f"{bad} to fix")
sys.exit(1 if bad else 0)
