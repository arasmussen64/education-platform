import re, sys
text = open(sys.argv[1], encoding="utf-8").read().splitlines()
items = []; cur = None
for line in text:
    m = re.search(r"\*\*`(mcq-[a-z0-9-]+)`\*\*", line)
    if m:
        cur = {"id": m.group(1), "choices": []}; items.append(cur); continue
    c = re.match(r'\s+- "(.*)"( ✔)?\s*$', line)
    if c and cur is not None and len(cur["choices"]) < 4:
        cur["choices"].append((c.group(1).replace("`", ""), bool(c.group(2))))
longest = 0; n = 0
for it in items:
    ch = it["choices"]
    if len(ch) != 4: print("??", it["id"], len(ch)); continue
    n += 1
    right = [len(t) for t, r in ch if r][0]; wrong = [len(t) for t, r in ch if not r]
    ratio = right / max(wrong); is_long = right > max(wrong)
    longest += is_long
    print(f"{it['id']:28s} right {right:3d} maxwrong {max(wrong):3d} ratio {ratio:.2f} {'LONGEST' if is_long else ''}")
print(f"{n} items, right is longest in {longest}")
