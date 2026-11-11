import sys, pathlib, yaml
root = pathlib.Path(sys.argv[1])
def walk(obj, path):
    if isinstance(obj, dict):
        for k, v in obj.items():
            walk(v, path + "." + str(k))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            walk(v, path + f"[{i}]")
    elif isinstance(obj, str):
        if "''" in obj:
            i = obj.index("''")
            print(f"  {path}: ...{obj[max(0,i-40):i+40]!r}...")
for topic in ["ml.prob.distributions","ml.prob.expectation-and-variance","ml.prob.bayes","ml.prob.maximum-likelihood"]:
    for f in sorted((root/topic).rglob("*.yaml")):
        data = yaml.safe_load(f.read_text(encoding="utf-8"))
        found = []
        print(f"== {f.relative_to(root)}")
        walk(data, "")
