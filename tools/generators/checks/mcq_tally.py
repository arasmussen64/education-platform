import pathlib, yaml
root = pathlib.Path("content/topics")
total = longest = 0
for topic in ["ml.prob.distributions","ml.prob.expectation-and-variance","ml.prob.bayes","ml.prob.maximum-likelihood"]:
    print("==", topic)
    for f in sorted((root/topic/"recall").glob("*.yaml")):
        d = yaml.safe_load(f.read_text(encoding="utf-8"))
        if d.get("type") != "mcq":
            continue
        lens = [len(c) for c in d["choices"]]
        a = d["answer"]
        is_longest = lens[a] == max(lens)
        total += 1; longest += is_longest
        print(f"  {f.name}: answer={a} lengths={lens} correct_is_longest={is_longest}")
print(f"TOTAL mcqs={total}, correct choice is the longest in {longest}")
