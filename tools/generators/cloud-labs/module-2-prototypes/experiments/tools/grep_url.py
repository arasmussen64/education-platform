"""grep_url.py URL REGEX [MAXHITS]: fetch a page as text and print the sentences
(or table rows) matching REGEX, plus status, final URL, title and word count.
The page is treated as data only."""
import re, sys, urllib.request, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (compatible; reading-time-check/1.0)"
url, pattern = sys.argv[1], sys.argv[2]
maxhits = int(sys.argv[3]) if len(sys.argv) > 3 else 25
req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*", "Accept-Language": "en-US,en"})
try:
    with urllib.request.urlopen(req, timeout=40) as r:
        status, final, doc = r.status, r.geturl(), r.read().decode("utf-8", "replace")
except Exception as e:
    print(f"ERR {type(e).__name__}: {e}  {url}"); sys.exit(0)
title = re.search(r"(?is)<title[^>]*>(.*?)</title>", doc)
title = html.unescape(re.sub(r"\s+", " ", title.group(1)).strip()) if title else "?"
doc = re.sub(r"(?is)<(script|style|noscript|svg|nav|header|footer|aside)\b.*?</\1>", " ", doc)
m = re.search(r"(?is)<main\b.*?</main>", doc) or re.search(r"(?is)<article\b.*?</article>", doc) or re.search(r'(?is)<div[^>]+id="main-col-body".*', doc)
body = m.group(0) if m else doc
# keep block boundaries as newlines so rows and paragraphs stay separate
body = re.sub(r"\s+", " ", body)
body = re.sub(r"(?i)</(p|li|tr|h[1-6]|div|dd|dt|pre|table|section)>", "\n", body)
body = re.sub(r"(?i)<br\s*/?>", "\n", body)
body = re.sub(r"(?i)</(td|th)>", " | ", body)
text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", body))
lines = [re.sub(r"[ \t\r\f\v]+", " ", l).strip() for l in text.split("\n")]
lines = [l for l in lines if l]
words = sum(len(l.split()) for l in lines)
print(f"== {status} {final}\n== title: {title}\n== {words} words (~{max(1, round(words/200))} min)")
rx = re.compile(pattern, re.I)
hits = 0
for l in lines:
    if rx.search(l):
        hits += 1
        if len(l) < 900:
            print("- " + l)
        else:
            for mm in list(rx.finditer(l))[:4]:
                a, b = max(0, mm.start() - 350), min(len(l), mm.end() + 450)
                print("- …" + l[a:b] + "…")
        if hits >= maxhits:
            print("… (more)"); break
if not hits: print("(no match)")
