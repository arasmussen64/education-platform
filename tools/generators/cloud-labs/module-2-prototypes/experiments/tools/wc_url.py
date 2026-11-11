"""Fetch each URL, report HTTP status, final URL, and a word count of the
main content (for reading-time estimates). Text only; nothing is executed."""
import re, sys, urllib.request, html
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (compatible; reading-time-check/1.0)"

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*", "Accept-Language": "en-US,en"})
    with urllib.request.urlopen(req, timeout=40) as r:
        return r.status, r.geturl(), r.read().decode("utf-8", "replace")

def main_text(doc):
    doc = re.sub(r"(?is)<(script|style|noscript|svg|nav|header|footer|aside)\b.*?</\1>", " ", doc)
    m = re.search(r"(?is)<main\b.*?</main>", doc) or re.search(r"(?is)<article\b.*?</article>", doc) or re.search(r'(?is)<div[^>]+id="main-col-body".*', doc)
    body = m.group(0) if m else doc
    text = html.unescape(re.sub(r"(?s)<[^>]+>", " ", body))
    return re.sub(r"\s+", " ", text).strip()

for url in sys.argv[1:]:
    try:
        status, final, doc = fetch(url)
        text = main_text(doc)
        words = len(text.split())
        print(f"{status}\t{words}w\t~{max(1, round(words/200))}min\t{url}" + (f"\t-> {final}" if final != url else ""))
    except Exception as e:
        print(f"ERR\t{type(e).__name__}: {e}\t{url}")
