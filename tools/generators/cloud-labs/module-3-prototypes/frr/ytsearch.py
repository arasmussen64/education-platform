import sys, re, json, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
q = sys.argv[1]
req = urllib.request.Request("https://www.youtube.com/results?search_query=" + urllib.parse.quote(q), headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"})
t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
m = re.search(r"var ytInitialData = (\{.*?\});</script>", t, re.S)
d = json.loads(m.group(1))
out = []
def walk(o):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            v = o["videoRenderer"]
            title = "".join(r.get("text", "") for r in v.get("title", {}).get("runs", []))
            ch = "".join(r.get("text", "") for r in v.get("ownerText", {}).get("runs", []))
            ln = v.get("lengthText", {}).get("simpleText", "?")
            pub = v.get("publishedTimeText", {}).get("simpleText", "?")
            out.append(f"{v['videoId']}  {ln:>8}  {ch} | {title} | {pub}")
        for x in o.values(): walk(x)
    elif isinstance(o, list):
        for x in o: walk(x)
walk(d)
print("\n".join(out[:int(sys.argv[2]) if len(sys.argv) > 2 else 8]))
