"""Fetch a public web page and print the sentences that match some patterns.

    python factgrep.py URL [PATTERN ...]

Prints the page's title, its date metadata when it has any, its length in
words (and minutes at 200 words a minute), then up to four sentences per
pattern. Used to confirm that a resource exists, how long it is, and that a
specific claim is on the page, without reading the whole page.
"""

import html
import re
import sys
import urllib.request

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
url, *patterns = sys.argv[1:]
request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (docs-check)"})
try:
    with urllib.request.urlopen(request, timeout=60) as response:
        final_url = response.geturl()
        raw = response.read().decode("utf-8", errors="replace")
except Exception as error:  # noqa: BLE001 - report and stop
    print(f"FAILED {url}: {error}")
    sys.exit(1)

title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
print("URL   :", final_url)
print("TITLE :", html.unescape(title.group(1)).strip() if title else "(none)")
for name in ("ms.date", "updated_at", "article:modified_time", "date", "last-modified"):
    found = re.search(rf'<meta[^>]+(?:name|property)="{re.escape(name)}"[^>]+content="([^"]+)"', raw, re.I)
    if found:
        print(f"META  : {name} = {found.group(1)}")

# The main text: prefer <main> or <article> when the page has one.
body = raw
for tag in ("main", "article"):
    block = re.search(rf"<{tag}\b.*?</{tag}>", raw, re.S | re.I)
    if block:
        body = block.group(0)
        break
body = re.sub(r"<(script|style|nav|footer|header)\b.*?</\1>", " ", body, flags=re.S | re.I)
text = html.unescape(re.sub(r"<[^>]+>", " ", body))
text = re.sub(r"\s+", " ", text)
words = len(text.split())
print(f"LENGTH: {words} words, about {max(1, round(words / 200))} min to read")

sentences = re.split(r"(?<=[.!?:])\s+(?=[A-Z0-9\"'(])", text)
for pattern in patterns:
    print(f"--- /{pattern}/")
    shown = 0
    for sentence in sentences:
        if re.search(pattern, sentence, re.I):
            print("  *", sentence.strip()[:420])
            shown += 1
            if shown == 4:
                break
    if not shown:
        print("  (no match)")
