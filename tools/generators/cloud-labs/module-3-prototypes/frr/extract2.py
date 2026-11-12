import sys, re, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
t = open(sys.argv[1], encoding="utf-8", errors="replace").read()
t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
t = html.unescape(re.sub(r"<[^>]+>", " ", t)); t = re.sub(r"\s+", " ", t)
for k in sys.argv[2:]:
    for i, m in enumerate(re.finditer(re.escape(k), t)):
        print(f"[{k}] ...", t[max(0, m.start() - 250):m.end() + 250]); 
        if i >= 1: break
