"""For every recall item in the given topics: MCQ answer positions and choice lengths; run predict_output and parsons code."""
import io
import contextlib
import pathlib
import sys

import yaml

root = pathlib.Path(sys.argv[1])
for topic in sys.argv[2:]:
    print("=" * 10, topic)
    for path in sorted((root / topic / "recall").glob("*.yaml")):
        item = yaml.safe_load(path.read_text(encoding="utf-8"))
        kind = item["type"]
        if kind == "mcq":
            lengths = [len(c) for c in item["choices"]]
            longest = max(range(len(lengths)), key=lambda i: lengths[i])
            flag = "LONGEST-IS-ANSWER" if longest == item["answer"] else ""
            print(f"{path.name}: answer={item['answer']} lengths={lengths} {flag}")
        elif kind == "predict_output":
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(item["code"], {"__name__": "__main__"})
            got = buf.getvalue()
            ok = got == item["expected_output"]
            print(f"{path.name}: predict {'OK' if ok else 'MISMATCH'}")
            if not ok:
                print("  expected:", repr(item["expected_output"]))
                print("  got     :", repr(got))
        elif kind == "parsons":
            code = "\n".join(item["lines"]) + "\n"
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                exec(code, {"__name__": "__main__"})
            print(f"{path.name}: parsons prints {buf.getvalue()!r}")
            for d in item.get("distractors", []):
                print("   distractor:", repr(d))
        else:
            print(f"{path.name}: type {kind}")
