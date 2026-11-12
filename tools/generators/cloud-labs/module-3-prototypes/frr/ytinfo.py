import sys, re, json, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for vid in sys.argv[1:]:
    req = urllib.request.Request("https://www.youtube.com/watch?v=" + vid, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"})
    t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
    m = re.search(r"var ytInitialPlayerResponse = (\{.*?\});(?:var|</script>)", t, re.S)
    p = json.loads(m.group(1))
    vd = p.get("videoDetails", {}); mf = p.get("microformat", {}).get("playerMicroformatRenderer", {})
    emb = p.get("playabilityStatus", {}).get("playableInEmbed")
    print(f"{vid} | {vd.get('author')} | {vd.get('title')} | {int(vd.get('lengthSeconds',0))//60}m{int(vd.get('lengthSeconds',0))%60:02d}s | published {mf.get('publishDate','?')[:10]} | embeddable={emb} | license? {'creative commons' in t.lower()}")
    print("   ", (vd.get("shortDescription") or "")[:400].replace("\n", " "))
