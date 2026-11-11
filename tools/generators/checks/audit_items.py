# Audit: MCQ answer positions and choice lengths, skills ids, practice/review ids, per topic.
import pathlib, yaml
root = pathlib.Path("content/topics")
for topic in ("ml.dsa.complexity", "ml.dsa.arrays-and-hashing", "ml.dsa.stacks-queues-recursion", "ml.dsa.sorting-and-searching"):
    tdir = root / topic
    t = yaml.safe_load((tdir / "topic.yaml").read_text(encoding="utf-8"))
    skill_ids = {s["id"] for s in t["skills"]}
    print(f"===== {topic}: skills {sorted(skill_ids)}")
    recall = {p.stem: p for p in (tdir / "recall").glob("*.yaml")}
    exercises = {p.name: p for p in (tdir / "exercises").iterdir()}
    listed = set(t["practice"]) | set(t["review_pool"]) | {t["prove"]["build"], t["prove"]["debug"]}
    for name in sorted(listed):
        if name not in recall and name not in exercises:
            print("  MISSING item file for listed id:", name)
    for name in sorted(set(recall) | set(exercises)):
        if name not in listed:
            print("  item not listed in topic.yaml:", name)
    positions = []
    for name, path in sorted(recall.items()):
        item = yaml.safe_load(path.read_text(encoding="utf-8"))
        bad = set(item.get("skills", [])) - skill_ids
        if bad:
            print("  UNKNOWN skills on", name, bad)
        if item.get("type") == "mcq":
            lengths = [len(c) for c in item["choices"]]
            ans = item["answer"]
            positions.append(ans)
            flag = " <-- LONGEST" if lengths[ans] == max(lengths) and lengths.count(max(lengths)) == 1 else ""
            print(f"  mcq {name}: answer={ans} lengths={lengths}{flag}")
    for name, path in sorted(exercises.items()):
        ex = yaml.safe_load((path / "exercise.yaml").read_text(encoding="utf-8"))
        bad = set(ex.get("skills", [])) - skill_ids
        if bad:
            print("  UNKNOWN skills on exercise", name, bad)
    print("  mcq answer positions in file order:", positions)
