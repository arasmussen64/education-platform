import sys
import sys, re, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for f in sys.argv[1:]:
    t = open(f, encoding="utf-8", errors="replace").read()
    title = re.search(r"<title>(.*?)</title>", t, re.S)
    body = re.search(r"<article.*?</article>|<main.*?</main>|<div[^>]*role=\"main\".*?</footer>", t, re.S)
    b = body.group(0) if body else t
    b = re.sub(r"<script.*?</script>|<style.*?</style>|<nav.*?</nav>", "", b, flags=re.S)
    txt = html.unescape(re.sub(r"<[^>]+>", " ", b))
    words = len(txt.split())
    heads = [html.unescape(re.sub(r"<[^>]+>", "", h)).strip() for h in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", b, re.S)]
    lic = re.findall(r"(Creative Commons[^<.]{0,80}|CC BY[^<]{0,30}|Attribution[^<]{0,60}|licen[cs]ed under[^<]{0,80}|GNU Free Documentation[^<]{0,40}|Copyright[^<]{0,80}|©[^<]{0,80})", t)
    print(f"== {f}: title={html.unescape(title.group(1).strip()) if title else '?'} words~{words} min@130={words//130}")
    print("   headings:", " | ".join(h for h in heads[:25] if h))
    print("   licence:", sorted(set(l.strip()[:90] for l in lic))[:4])
