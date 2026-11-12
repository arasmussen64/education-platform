import sys, re, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
parts = re.split(r"(<h[2-4][^>]*>.*?</h[2-4]>)", t, flags=re.S)
cur = "start"
for p in parts:
    if re.match(r"<h[2-4]", p):
        cur = html.unescape(re.sub(r"<[^>]+>", "", p)).replace("\uf0c1", "").strip()
    else:
        w = len(html.unescape(re.sub(r"<[^>]+>", " ", p)).split())
        if w > 30: print(f"{w:6d} words  {cur}")
