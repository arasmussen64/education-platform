import sys, re, urllib.request
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
for vid in sys.argv[1:]:
    t = urllib.request.urlopen(urllib.request.Request("https://www.youtube.com/watch?v=" + vid, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "en-US"}), timeout=20).read().decode("utf-8", "replace")
    m = re.findall(r'.{0,80}[Cc]reative [Cc]ommons.{0,120}', t)
    print(vid, "|", (m[0] if m else "no CC text")[:220].replace("\u0026", "&"))
