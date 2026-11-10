import json

record = {"name": "Ada", "tags": ["math", "code"], "scores": {"quiz": 9, "exam": 17}}
text = json.dumps(record)
print(text)
print(type(text).__name__)

back = json.loads(text)
print(back == record)
print(back["scores"]["exam"])

print(json.dumps({"ok": True, "missing": None}))

with open("record.json", "w") as f:
    json.dump(record, f, indent=2)
with open("record.json") as f:
    loaded = json.load(f)
print(loaded["tags"][0])
print(loaded.get("email", "no email"))
