"""Run every predict item's code in Module 8 and compare with its expected output;
list every MCQ whose correct answer is the longest choice (or within 5% of it)."""

import io
import contextlib
import sys
from pathlib import Path

import yaml

ROOT = Path(sys.argv[1])
TOPICS = [
    "ml.nn.neurons-and-layers",
    "ml.nn.backward-layers",
    "ml.nn.initialization-and-activations",
    "ml.nn.training-loop",
    "ml.nn.regularization",
    "ml.nn.convolution",
    "ml.nn.debugging-training",
]

for topic in TOPICS:
    for path in sorted((ROOT / "content" / "topics" / topic / "recall").glob("*.yaml")):
        item = yaml.safe_load(path.read_text(encoding="utf-8"))
        kind = item.get("type")
        rel = f"{topic}/recall/{path.name}"
        if kind == "predict_output":
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    exec(compile(item["code"], str(path), "exec"), {"__name__": "__main__"})
                got = buf.getvalue()
            except Exception as e:  # noqa: BLE001
                got = f"EXCEPTION: {e!r}\n"
            if got != item["expected_output"]:
                print(f"PREDICT MISMATCH {rel}\n--- expected\n{item['expected_output']}--- got\n{got}")
            else:
                print(f"predict ok {rel}")
        elif kind == "mcq":
            choices = item["choices"]
            lengths = [len(c) for c in choices]
            ans = item["answer"]
            longest = max(range(len(choices)), key=lambda i: lengths[i])
            flag = ""
            if longest == ans:
                flag = "ANSWER IS LONGEST"
            elif lengths[ans] >= 0.95 * lengths[longest]:
                flag = "answer within 5% of longest"
            print(f"mcq {rel}: answer={ans} lengths={lengths} {flag}")
        elif kind == "parsons":
            print(f"parsons {rel}: {len(item['lines'])} lines, {len(item.get('distractors', []))} distractors")
