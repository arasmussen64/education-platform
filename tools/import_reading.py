"""Copy part of an openly licensed page into a topic, to be read inside the app.

    python -m uv run python tools/import_reading.py py.strings-as-sequences 0 \
        --name text --from "#text" --to "#lists"

It downloads the resource's page, keeps the part asked for, cleans it down to
the plain HTML a reading may hold (`reading_html.py`), and writes
`content/topics/<topic>/readings/<name>.html`. Then it prints the `text:`
lines to add to the resource in `topic.yaml`. It refuses a resource whose
recorded licence doesn't allow copying (ADR-0031).

Choosing the part:

    --select CSS   the element that holds the article (each site has a default)
    --from X       start here: "#an-id" or a heading's exact words
    --to X         stop before this: "#an-id" or a heading's exact words
    --drop CSS     also leave these out (may be repeated)
    --url URL      another page of the same work (a book's next section)
    --append       add to the file instead of replacing it

Read the result before committing it: the words must be the source's, in
order, with nothing of ours mixed in.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

import reading_html
import yaml
from bs4 import BeautifulSoup, Comment, NavigableString, Tag

ROOT = Path(__file__).resolve().parent.parent
READING_WORDS_A_MINUTE = 130

# Removed with everything inside them, on every site.
DROP_ALWAYS = (
    "script, style, noscript, template, nav, header, footer, form, button, input, "
    "select, textarea, svg, iframe, object, video, audio, canvas, link, meta, "
    "annotation, annotation-xml, a.headerlink, a.anchor, a.anchor-link, a.hash-link"
)

# Where each site keeps its article, and its page furniture to leave out.
SITES: dict[str, dict[str, str]] = {
    "docs.python.org": {
        "select": "div.body",
        "drop": ".headerlink, .versionadded, .versionchanged",
    },
    "en.wikipedia.org": {
        "select": "div.mw-parser-output",
        "drop": (
            ".mw-editsection, sup.reference, .navbox, .infobox, .hatnote, .reflist, "
            ".mw-references-wrap, table.sidebar, .ambox, .noprint, .metadata, "
            ".sistersitebox, "
            ".mwe-math-fallback-image-inline, .mwe-math-fallback-image-display, .toc, "
            ".mw-empty-elt, .navigation-not-searchable, .shortdescription, .catlinks"
        ),
    },
    "numpy.org": {"select": "article.bd-article", "drop": ".headerlink"},
    "docs.pytest.org": {
        "select": "article[role=main], div[role=main]",
        "drop": ".headerlink",
    },
    "www.investor.gov": {
        "select": "article, main",
        "drop": ".breadcrumb, .social-share, .visually-hidden",
    },
    "openstax.org": {
        "select": "div[data-type=page], main",
        "drop": "[data-type=abstract] > h3, .os-eoc, .os-teacher",
    },
    "developer.mozilla.org": {
        "select": "article.main-page-content, main",
        "drop": ".bc-data, .metadata",
    },
    "learn.microsoft.com": {
        "select": "div.content, main",
        "drop": (
            ".page-metadata-container, #article-header, .feedback-section, "
            "#user-feedback, .alert.is-primary"
        ),
    },
    "docs.kernel.org": {"select": "div.body", "drop": ".headerlink"},
    "wiki.archlinux.org": {
        "select": "div.mw-parser-output",
        "drop": ".mw-editsection, .archwiki-template-meta, .noprint, .toc, .catlinks",
    },
    "www.digitalocean.com": {
        "select": "div[class*=Markdown], article, main",
        "drop": "",
    },
    "missing.csail.mit.edu": {"select": "div#content, article, main", "drop": ""},
    "runestone.academy": {
        "select": "div#main-content, section.section, main",
        "drop": ".headerlink, .runestone, .ac_section",
    },
}

HEADINGS = ("h1", "h2", "h3", "h4", "h5", "h6")


def fetch(url: str) -> str:
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (reading importer)"}
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", "replace")


def words_of(tag: Tag) -> str:
    """A heading's words, without the "¶" or "#" link some sites add."""
    return re.sub(r"\s+", " ", tag.get_text(" ")).strip(" ¶#\n").casefold()


def find(root: Tag, where: str) -> Tag:
    """The element an option names: "#an-id", or a heading's exact words."""
    if where.startswith("#"):
        found = root.find(id=where[1:])
    else:
        wanted = re.sub(r"\s+", " ", where).strip().casefold()
        found = next(
            (h for h in root.find_all(HEADINGS) if words_of(h) == wanted), None
        )
    if not isinstance(found, Tag):
        sys.exit(f"Can't find {where!r} on the page.")
    return found


def keep_between(root: Tag, start: Tag | None, stop: Tag | None) -> None:
    """Empties the page of everything before `start` and from `stop` on.

    Pages nest their sections in different ways, so this goes by reading
    order: every piece of text and every picture is kept or removed by where
    it comes, and the boxes left empty are removed after.
    """
    inside = start is None
    for node in list(root.descendants):
        if node is start:
            inside = True
        if stop is not None and node is stop:
            inside = False
            start = None  # nothing after the stop comes back in
        leaf = isinstance(node, NavigableString) or (
            isinstance(node, Tag) and node.name in ("img", "br", "hr")
        )
        if leaf and not inside:
            node.extract()
    for tag in reversed(root.find_all(True)):
        if (
            tag.name not in ("img", "br", "hr", "td", "th")
            and not tag.get_text(strip=True)
            and not tag.find("img")
        ):
            tag.decompose()


def clean(root: Tag, page: str) -> None:
    """Turns the article into the plain HTML a reading may hold."""
    for comment in root.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()
    # Code keeps its text and loses its colouring.
    for pre in root.find_all("pre"):
        text = pre.get_text()
        pre.clear()
        code = BeautifulSoup("", "html.parser").new_tag("code")
        code.string = text.strip("\n")
        pre.append(code)
    # <mfenced> is an old way to write brackets in a formula that browsers
    # no longer draw: (1 + r) would show as 1 + r. Write the brackets out.
    for fenced in root.find_all("mfenced"):
        opening = str(fenced.get("open", "("))
        closing = str(fenced.get("close", ")"))
        separator = str(fenced.get("separators", ","))[:1]
        maker = BeautifulSoup("", "html.parser")

        def operator(sign: str, maker: BeautifulSoup = maker) -> Tag:
            mo = maker.new_tag("mo")
            mo.string = sign
            return mo

        parts = [child for child in fenced.children if isinstance(child, Tag)]
        fenced.clear()
        if opening:
            fenced.append(operator(opening))
        for index, part in enumerate(parts):
            if index and separator.strip():
                fenced.append(operator(separator))
            fenced.append(part)
        if closing:
            fenced.append(operator(closing))
        fenced.name = "mrow"
        fenced.attrs = {}
    for tag in root.find_all(True):
        if tag.name == "h1":
            tag.name = "h2"
        elif tag.name == "h6":
            tag.name = "h5"
        if tag.name == "img":
            source = tag.get("src") or tag.get("data-src") or ""
            tag.attrs = {
                "src": urljoin(page, str(source)),
                "alt": str(tag.get("alt") or ""),
            }
            if not tag["src"].startswith("https://"):
                tag.decompose()
            continue
        if tag.name == "a":
            address = urljoin(page, str(tag.get("href") or ""))
            if address.startswith("https://"):
                tag.attrs = {"href": address}
            else:
                tag.unwrap()
            continue
        if tag.name in reading_html.ALLOWED:
            allowed = reading_html.ALLOWED[tag.name]
            tag.attrs = {
                name: value for name, value in tag.attrs.items() if name in allowed
            }
    # Anything else (div, span, section, ...) goes, and what it held stays.
    for tag in root.find_all(True):
        if tag.name not in reading_html.ALLOWED:
            tag.unwrap()


def tidy(html: str) -> str:
    """One block to a line where that's safe, so a diff of a reading is readable."""
    parts = re.split(r"(<pre>.*?</pre>)", html, flags=re.S)
    for index in range(0, len(parts), 2):
        text = re.sub(r"[ \t\r\f\v]*\n\s*", "\n", parts[index])
        text = re.sub(r"\n{2,}", "\n", text)
        parts[index] = text
    return "".join(parts).strip() + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("topic")
    parser.add_argument(
        "index", type=int, help="which of the topic's resources (0 is the main one)"
    )
    parser.add_argument("--name", required=True, help="the file's name, without .html")
    parser.add_argument(
        "--url",
        help="another page of the same work, instead of the resource's own address",
    )
    parser.add_argument("--select")
    parser.add_argument("--from", dest="start")
    parser.add_argument("--to", dest="stop")
    parser.add_argument("--drop", action="append", default=[])
    parser.add_argument("--append", action="store_true")
    args = parser.parse_args()

    folder = ROOT / "content" / "topics" / args.topic
    topic = yaml.safe_load((folder / "topic.yaml").read_text("utf-8"))
    resource = topic["resources"][args.index]
    if resource["type"] != "reading":
        sys.exit("Only a reading can be copied in.")
    if not reading_html.copyable(resource["license"]):
        sys.exit(
            "This licence doesn't allow copying, so the resource stays a link: "
            + resource["license"]
        )

    page = args.url or resource["url"]
    site = SITES.get(urlparse(page).hostname or "", {})
    soup = BeautifulSoup(fetch(page), "html.parser")
    root = soup.select_one(args.select or site.get("select") or "main, article, body")
    if root is None:
        sys.exit("Can't find the article on the page: give --select.")
    # Some sites wrap a picture in a button that enlarges it: keep the picture.
    for button in root.select("button:has(img)"):
        button.unwrap()
    for selector in [DROP_ALWAYS, site.get("drop", ""), *args.drop]:
        if selector:
            for junk in root.select(selector):
                junk.decompose()
    start = find(root, args.start) if args.start else None
    stop = find(root, args.stop) if args.stop else None
    keep_between(root, start, stop)
    clean(root, page)
    html = tidy(root.decode_contents())

    problems, words = reading_html.check(html)
    if problems:
        sys.exit(
            "The cleaned page still holds things a reading can't:\n  "
            + "\n  ".join(problems)
        )
    if words == 0:
        sys.exit("Nothing was left: check --from, --to and --select.")

    out = folder / "readings" / f"{args.name}.html"
    out.parent.mkdir(exist_ok=True)
    before = out.read_text("utf-8") if args.append and out.exists() else ""
    # write_bytes: on Windows write_text would turn every line ending into CRLF.
    out.write_bytes((before + html).encode("utf-8"))
    total = reading_html.check(before + html)[1]
    minutes = round(total / READING_WORDS_A_MINUTE)
    where = out.relative_to(ROOT).as_posix()
    print(f"Wrote {where}: {total} words, about {minutes} minutes.")
    print("Add to the resource in topic.yaml (and set `use: embed`):")
    print("    text:")
    print(f"      file: readings/{args.name}.html")
    print('      by: "<the author or publisher, as the source credits itself>"')
    print('      license_url: "<the address of the licence\'s text>"')
    print(f'      retrieved: "{date.today().isoformat()}"')
    print('      changes: "<what was left out: which sections, the menus, the links>"')


if __name__ == "__main__":
    main()
